# Opus Interactive Audio Codec package

[Conan.io](https://conan.io) package for [Opus audio codec](https://opus-codec.org/)

The packages generated with this **conanfile** can be found in [Bintray](TODO).

## Build packages

Download conan client from [Conan.io](https://conan.io) and run:

    $ python build.py

If your are in Windows you should run it from a VisualStudio console in order to get "mc.exe" in path.

## Upload packages to server

    $ conan upload opus/1.2.1@fogo/stable --all

## Reuse the packages

### Basic setup

    $ conan install opus/1.2.1@fogo/stable

### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*

    [requires]
    opus/1.2.1@fogo/stable

    [options]
    opus:shared=True # False by default

    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install .

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.

### License
[MIT](LICENSE)