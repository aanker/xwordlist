---
layout: home
title:  Changelog
menu_title: Changelog
permalink: /changelog/
---

### Version 22.1.9 (10/XX/2022)
* Fix how user’s home directory is specified so it is more cross platform [(link)](https://github.com/aanker/xwordlist/commit/0e0edd4d892ee53525e948ea85e4e38cb1c92ba8)

### Version 22.1.8 (10/24/2022)
* Add --config option to help user discover where their configuration file is located [(link)](https://github.com/aanker/xwordlist/commit/bdc0a3b10cbbc05871243951fc38d827a24960ed)
* Clean up global names and how the variables are created to give more durability to referencing user home directory [(link)](https://github.com/aanker/xwordlist/commit/f2e9194937df29d054ca9f20e6e288a580c36c3e)

### Version 22.1.7 (10/23/2022)

* Better checking for configuration file, won’t fail if can’t find one [(link)](https://github.com/aanker/xwordlist/commit/10f32284c8bb54b47e713ee84dfae003bd9ab6ea)
* Add second location for configuration file, both same directory as executable (default) and \~/xwordlist/ directory [(link)](https://github.com/aanker/xwordlist/commit/d0a07f11a4d979a87c8e5d513e1979f7c6672732)
* Make include requirements for other Python modules less specific [(link)](https://github.com/aanker/xwordlist/commit/1fd258eaff6d40df357fc145778c8d1e26a4b9dc)

### Version 22.1.6 (10/22/2022)

* Add -v/--version option that pulls automatically from project setup file [(link)](https://github.com/aanker/xwordlist/commit/fdefd21931bd54a398c8234585934741cc079f2d)
* Fix defect where software can’t find the configuration file location [(link)](https://github.com/aanker/xwordlist/commit/3b6b76ba8d2fdcefa76a0efd56fe920394ac7f90)
* Move initialization of IMPACT_COLOR to same place as other globals [(link)](https://github.com/aanker/xwordlist/commit/d2f9873d01bbb1d49448bd0f00e861c8106da4cd)

### Version 22.1.5 (10/21/2022)

Initial commit
