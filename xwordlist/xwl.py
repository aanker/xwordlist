import re
import requests
import urllib.parse

from bs4 import BeautifulSoup
from anyascii import anyascii


class WordList:
    def __init__(self, myList=[]):
        self.myList = myList

    # List transformation options
    def minimum(self, numChars):
        if isinstance(numChars, int) or numChars.isdigit():
            newList = []
            for line in self.myList:
                if line and len(line) >= int(numChars):
                    newList.append(line)
            self.myList = newList
        else:
            err_dict = {
                'error': 'Exiting... argument for minimum must be an integer, not {}',
                'arg': numChars,
            }
            raise XWLException(err_dict)

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
            err_dict = {
                'error': 'Exiting... unknown strip option {}',
                'arg': stripWhat,
            }
            raise XWLException(err_dict)

    def case(self, newCase):
        case_dict = {
            'upper': str.upper,
            'lower': str.lower,
        }
        if newCase in case_dict:
            self.myList = list(case_dict[newCase](line) for line in self.myList)
        elif newCase != 'none':
            err_dict = {
                'error': 'Exiting... unknown case option {}',
                'arg': newCase,
            }
            raise XWLException(err_dict)

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
            err_dict = {
                'error': 'Exiting... incorrect dedupe option {}',
                'arg': dedupeType,
            }
            raise XWLException(err_dict)

    def alphabetize(self, direction):
        if direction == 'normal':
            self.myList = sorted(self.myList, key=str.casefold)
        elif direction == 'reverse':
            self.myList = sorted(self.myList, key=str.casefold, reverse=True)
        else:
            err_dict = {
                'error': 'Exiting... incorrect alphabetize option {}',
                'arg': direction,
            }
            raise XWLException(err_dict)

    # Content parsing options
    def regex(self, regexInput):
        try:
            newList = []
            for line in self.myList:
                newList.extend(re.findall(regexInput, line))
            self.myList = newList

        except re.error:
            err_dict = {
                'error': 'Regex pattern {} not valid, please check and try again',
                'arg': regexInput,
            }
            raise XWLException(err_dict)

        except Exception as e:
            err_dict = {
                'error': 'Error {}',
                'arg': e,
            }
            raise XWLException(err_dict)

    def convert(self, parseChars):
        # Add a space to parseChars since we always parse by that
        parseChars += ' '
        for char in parseChars:
            newList = []
            for line in self.myList:
                if line.find(char) != -1:
                    newList.extend(line.split(char))
                else:
                    newList.append(line)
            self.myList = newList


class WebExtract:
    PARSEDICT = {}
    WEBEXTRACT = ''

    def __init__(self, parseDict={}, webExtract=''):
        self.returnWords = []
        self.scrapeWords = []
        self.parseDict = parseDict if parseDict != {} else self.PARSEDICT
        self.webExtract = webExtract if webExtract != '' else self.WEBEXTRACT

    def pull_data(self, getData):
        return self._get_web_page(getData)

    def _get_web_page(self, webURL):
        try:
            r = requests.get(webURL)
            if r.status_code == 200:
                inputSoup = BeautifulSoup(r.text, 'html.parser')
                if self.parseDict:
                    # See if we have a class, in which case, have to do more screening (1 to N classes)
                    if 'class' in self.parseDict:
                        classDict = {}
                        classDict['class'], whichNum = self.parseDict['class']
                        fullSoup = inputSoup.find_all(attrs=classDict)
                        for counter, whichSoup in enumerate(fullSoup, start=1):
                            if whichNum == counter or whichNum == 0:
                                self._extract_from_web(whichSoup, webURL)
                                self.returnWords.extend(self.scrapeWords)
                    else:
                        self._extract_from_web(inputSoup.find(attrs=self.parseDict), webURL)
                        self.returnWords.extend(self.scrapeWords)
                else:
                    self._extract_from_web(inputSoup, webURL)
                    self.returnWords.extend(self.scrapeWords)

            elif r.status_code == 403:
                err_dict = {
                    'error': 'Unable to load webpage due to code 403: this usually means we are being blocked',
                }
                raise XWLException(err_dict)

            else:
                err_dict = {
                    'error': 'Unable to load webpage, status code = {}',
                    'arg': r.status_code,
                }
                raise XWLException(err_dict)

        except XWLException:
            raise

        except (requests.URLRequired, requests.RequestException):
            err_dict = {
                'error': 'No content retrieved, error URL: {}',
                'arg': self.webURL,
            }
            raise XWLException(err_dict)

        except AttributeError:
            err_dict = {
                'error': 'HTML attribute {} not found, check document and try again',
                'arg': self.parseDict,
            }
            raise XWLException(err_dict)

        except Exception as e:
            err_dict = {
                'error': 'Web error {}',
                'arg': e,
            }
            raise XWLException(err_dict)

    def _extract_from_web(self, soup, extractURL):
        # A few ways the default option can come in, try that first
        if self.webExtract == 'text':
            self.scrapeWords = soup.stripped_strings
        elif self.webExtract == 'links':
            for link in soup.find_all('a'):
                getURL = link.get('href')
                if getURL:
                    parsePieces = urllib.parse.urlsplit(getURL)
                    # Check to see if absolute or relative URL.  If relative, make it absolute
                    if parsePieces.scheme == '' and parsePieces.netloc == '':
                        parseExtract = urllib.parse.urlsplit(extractURL)
                        getURL = urllib.parse.urljoin(f'{parseExtract.scheme}://{parseExtract.netloc}', getURL)
                    self.scrapeWords.append(getURL)
        elif self.webExtract[:5] == 'html-':
            extractTags = self.webExtract[5:].split('_')
            for tag in extractTags:
                for link in soup.find_all(tag):
                    text = link.get_text()
                    self.scrapeWords.append(text)
        else:
            error = f'Exiting... incorrect option for webextract: {self.err_text(self.webExtract)}'
            raise XWLException(error)

        self.scrapeWords = list(line for line in self.scrapeWords)


class XWLException(Exception):
    pass
