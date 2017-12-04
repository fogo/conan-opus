# -*- coding: utf-8 -*-
from conans import ConanFile, tools
from conans.util import files
import os


class OpusConan(ConanFile):
    name = "opus"
    version = "1.2.1"
    ZIP_FOLDER_NAME = "opus-{}".format(version)
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        # 'rtcd' stands for runtime CPU detection. Opus has a series of
        # optimizations based on set of instructions available. Since with
        # conan it is distributed as a package, we can't assume end-user
        # available instructions so by default it enables this option.
        #
        # To recompile against your environment without runtime detection
        # just disable this option. For instance, you can use this install
        # line for this purpose:
        #
        # conan install opus/1.2.1@fogo/stable -o opus:rtcd=False --build=opus
        "rtcd": [True, False],
    }
    default_options = "shared=False", "fPIC=True", "rtcd=True"
    exports_sources = ["CMakeLists.txt"]
    url = "https://github.com/fogo/conan-opus"
    license = "http://opus-codec.org/license/"
    description = "Opus is a totally open, royalty-free, highly versatile " \
                  "audio codec. Opus is unmatched for interactive speech " \
                  "and music transmission over the Internet, but is also " \
                  "intended for storage and streaming applications. It is " \
                  "standardized by the Internet Engineering Task Force (" \
                  "IETF) as RFC 6716 which incorporated technology from " \
                  "Skype’s SILK codec and Xiph.Org’s CELT codec."
    checksum = "cfafd339ccd9c5ef8d6ab15d7e1a412c054bf4cb4ecbbbcc78c12ef2def70732"

    def configure(self):
        # it is just C code, this is unnecessary
        del self.settings.compiler.libcxx

    def source(self):
        # https://archive.mozilla.org/pub/opus/opus-1.2.1.tar.gz
        zip_name = "opus-{version}.tar.gz".format(version=self.version)
        tools.download(
            "https://archive.mozilla.org/pub/opus/{zip_name}".format(zip_name=zip_name),
            zip_name)

        candidate = tools.sha256sum(zip_name)
        if candidate != self.checksum:
            raise Exception("MD5 didn't match ({} != {})".format(candidate, self.checksum))

        tools.unzip(zip_name)
        os.unlink(zip_name)
        if self.settings.os != "Windows":
            self.run("chmod +x ./{}/configure".format(self.ZIP_FOLDER_NAME))

    def build(self):
        with tools.chdir(self.ZIP_FOLDER_NAME):
            files.mkdir("_build")
            with tools.chdir("_build"):
                if not tools.os_info.is_windows:
                    configure_options = []
                    if self.options.fPIC:
                        configure_options.append("CFLAGS='-fPIC'")

                    if self.options.shared:
                        configure_options.append("--enable-shared=yes --enable-static=no")
                    else:
                        configure_options.append("--enable-shared=no --enable-static=yes")

                    if not self.options.rtcd:
                        configure_options.append("--disable-rtcd")

                    self.run("../configure {}".format(" ".join(configure_options)))
                    self.run("make")
                else:
                    raise Exception("TODO: windows")

    def package(self):
        self.copy(
            "*.h",
            dst="include",
            src="{basedir}/include".format(basedir=self.ZIP_FOLDER_NAME))
        self.copy(
            "*.a",
            dst="lib",
            src="{basedir}/_build/.libs".format(basedir=self.ZIP_FOLDER_NAME))
        self.copy(
            "*.so",
            dst="lib",
            src="{basedir}/_build/.libs".format(basedir=self.ZIP_FOLDER_NAME))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
