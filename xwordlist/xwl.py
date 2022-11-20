import re
import requests
import urllib.parse

from bs4 import BeautifulSoup
from anyascii import anyascii


class WordList:
    def __init__(self, myList=[], color=''):
        self.myList = myList
        self.color = color

    # List transformation options
    def minimum(self, numChars):
        if isinstance(numChars, int) or numChars.isdigit():
            newList = []
            for line in self.myList:
                if line and len(line) >= int(numChars):
                    newList.append(line)
            self.myList = newList
        else:
            error = f'Exiting... argument for minimum must be an integer, not {self.err_text(numChars)}'
            raise XWLException(error)

    def strip(self, stripWhat):
        newList = []
        if stripWhat in ['keepdiacritic', 'diacritic']:
            for word in self.myList:
                if stripWhat != 'keepdiacritic':
                    word = anyascii(word)
                newWord = ''.join([i for i in word if i.isalpha()])
                if len(newWord) > 0:
                    newList.append(newWord)
            self.myList = newList
        else:
            error = f'Exiting... unknown strip option {self.err_text(stripWhat)}'
            raise XWLException(error)

    def case(self, newCase):
        case_dict = {
            'upper': str.upper,
            'lower': str.lower,
        }
        if newCase in case_dict:
            self.myList = list(case_dict[newCase](line) for line in self.myList)
        elif newCase != 'none':
            error = f'Exiting... unknown case option {self.err_text(newCase)}'
            raise XWLException(error)

    def dedupe(self, dedupeType):
        if dedupeType == 'bycase':
            self.myList = list(dict.fromkeys(self.myList))
        elif dedupeType == 'nocase':
            newList = []
            newSet = set()
            for line in self.myList:
                newLine = line.casefold()
                if newLine not in newSet:
                    newSet.add(newLine)
                    newList.append(line)
            self.myList = newList
        else:
            error = f'Exiting... incorrect dedupe option {self.err_text(dedupeType)}'
            raise XWLException(error)

    def alphabetize(self, direction):
        if direction == 'normal':
            self.myList = sorted(self.myList, key=str.casefold)
        elif direction == 'reverse':
            self.myList = sorted(self.myList, key=str.casefold, reverse=True)
        else:
            error = f'Exiting... incorrect alphabetize option {self.err_text(direction)}'
            raise XWLException(error)

    # Content parsing options
    def regex(self, regexInput):
        try:
            newList = []
            for line in self.myList:
                newList.extend(re.findall(regexInput, line))
            self.myList = newList

        except re.error:
            error = f'Regex pattern {self.err_text(regexInput)} not valid, please check and try again'
            raise XWLException(error)

        except Exception as e:
            error = f'Error {self.err_text(e)}'
            raise XWLException(error)

    def convert(self, parseChars):
        # First trap for problem where defaults are assumed but not specified
        for char in parseChars:
            newList = []
            for line in self.myList:
                if line.find(char) != -1:
                    newList.extend(line.split(char))
                else:
                    newList.append(line)
            self.myList = newList

    def err_text(self, text):
        if self.color:
            return f'<{self.color}>{text}</{self.color}>'
        else:
            return text


class WebExtract:
    def __init__(self, color=''):
        self.returnWords = []
        self.scrapeWords = []
        self.color = color

    def get_web_page(self, webURL, parseDict, webExtract):
        try:
            r = requests.get(webURL)
            if r.status_code == 200:
                inputSoup = BeautifulSoup(r.text, 'html.parser')
                if parseDict:
                    # See if we have a class, in which case, have to do more screening (1 to N classes)
                    if 'class' in parseDict:
                        classDict = {}
                        classDict['class'], whichNum = parseDict['class']
                        fullSoup = inputSoup.find_all(attrs=classDict)
                        for counter, whichSoup in enumerate(fullSoup, start=1):
                            if whichNum == counter or whichNum == 0:
                                self._extract_from_web(webExtract, whichSoup, webURL)
                                self.returnWords.extend(self.scrapeWords)
                    else:
                        self._extract_from_web(webExtract, inputSoup.find(attrs=parseDict), webURL)
                        self.returnWords.extend(self.scrapeWords)
                else:
                    self._extract_from_web(webExtract, inputSoup, webURL)
                    self.returnWords.extend(self.scrapeWords)

            elif r.status_code == 403:
                error = 'Unable to load webpage due to code 403: this usually means we are being blocked'
                raise XWLException(error)

            else:
                error = f'Unable to load webpage, status code = {self.err_text(r.status_code)}'
                raise XWLException(error)

        except XWLException:
            raise

        except (requests.URLRequired, requests.RequestException):
            error = f'No content retrieved, error URL: {self.err_text(webURL)}'
            raise XWLException(error)

        except AttributeError:
            error = f'HTML attribute {self.err_text(parseDict)} not found, check document and try again'
            raise XWLException(error)

        except Exception as e:
            error = f'Web error {self.err_text(e)}'
            raise XWLException(error)

    def _extract_from_web(self, extractWhat, soup, extractURL):
        # A few ways the default option can come in, try that first
        if extractWhat == 'text' or extractWhat is None:
            self.scrapeWords = soup.stripped_strings
        elif extractWhat == 'links':
            for link in soup.find_all('a'):
                getURL = link.get('href')
                if getURL:
                    parsePieces = urllib.parse.urlsplit(getURL)
                    # Check to see if absolute or relative URL.  If relative, make it absolute
                    if parsePieces.scheme == '' and parsePieces.netloc == '':
                        parseExtract = urllib.parse.urlsplit(extractURL)
                        getURL = urllib.parse.urljoin(f'{parseExtract.scheme}://{parseExtract.netloc}', getURL)
                    self.scrapeWords.append(getURL)
        elif extractWhat[:5] == 'html-':
            extractTags = extractWhat[5:].split('_')
            for tag in extractTags:
                for link in soup.find_all(tag):
                    text = link.get_text()
                    self.scrapeWords.append(text)
        else:
            error = f'Exiting... incorrect option for webextract: {self.err_text(extractWhat)}'
            raise XWLException(error)

        self.scrapeWords = list(line for line in self.scrapeWords)

    def err_text(self, text):
        if self.color:
            return f'<{self.color}>{text}</{self.color}>'
        else:
            return text


class XWLException(Exception):
    pass
