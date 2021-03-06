# -*- coding: utf-8 -*-
from __future__ import print_function
from conans import AutoToolsBuildEnvironment, ConanFile, tools, VisualStudioBuildEnvironment
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

        tools.check_sha256(zip_name, self.checksum)

        tools.unzip(zip_name)
        os.unlink(zip_name)
        if self.settings.os != "Windows":
            self.run("chmod +x ./{}/configure".format(self.ZIP_FOLDER_NAME))

    def build(self):
        with tools.chdir(self.ZIP_FOLDER_NAME):
            files.mkdir("_build")
            with tools.chdir("_build"):
                if not tools.os_info.is_windows:
                    args = []
                    if self.options.shared:
                        args.append("--enable-shared=yes")
                        args.append("--enable-static=no")
                    else:
                        args.append("--enable-shared=no")
                        args.append("--enable-static=yes")

                    # Note: as usual compiling w/ gcc 4.1 is a mess. On
                    # environment used for tests (docker image
                    # uilianries/conangcc41) I had to disable RTCD AND
                    # manually patch supported SSE to build x86 arch.
                    #
                    # It was failed configuration w/ RTCD enabled w/
                    # message below:
                    #
                    # checking How to get X86 CPU Info... configure: error: no supported Get CPU Info method, please disable run-time CPU capabilities detection or intrinsics
                    #
                    # If RTCD disabled, it seems it was still unable to
                    # detect correct SSE features and it ended up failing
                    # in posterior link step. That's why a few lines
                    # below there is a hackish line to add arbitrarily the 
                    # most basic/old SIMD flags. It seems this is necessary
                    # because gcc4.1 only have a few of all expected SIMD
                    # flags by Opus.
                    #
                    # Reference about gcc4.1 flags:
                    # http://www.linuxcertif.com/man/1/gcc-4.1/
                    is_gcc41_x86 = self.settings.arch == "x86" and \
                        self.settings.compiler == "gcc" and \
                        self.settings.compiler.version == "4.1"
                    if is_gcc41_x86 or (not self.options.rtcd):
                        args.append("--disable-rtcd")

                    env_build = AutoToolsBuildEnvironment(self)
                    env_build.fpic = self.options.fPIC
                    if is_gcc41_x86:
                        env_build.flags.extend(["-msse", "-msse2"])
                    env_build.configure("..", args=args)
                    env_build.make()
                else:
                    # TODO: no idea how to apply rtcd option for Windows
                    # It enables RTCD based on definitions found by config.h
                    # file. Can we override it?
                    env_build = VisualStudioBuildEnvironment(self)
                    env_build.include_paths.append("../include")
                    with tools.environment_append(env_build.vars):
                        name = target = "opus"
                        msbuild = tools.msvc_build_command(
                            self.settings, 
                            r"..\win32\VS2015\{}.sln".format(name), 
                            targets=[target], 
                            arch="Win32" if self.settings.arch == "x86" else "x64", 
                            upgrade_project=True)
                        # TODO: msvc_build_command arch arg seems to have no effect!
                        msbuild += " /p:Platform={}".format("Win32" if self.settings.arch == "x86" else "x64")
                        command = "{vcvars} && {msbuild}".format(
                            vcvars=tools.vcvars_command(self.settings), 
                            msbuild=msbuild)
                        self.run(command)

    def package(self):
        self.copy(
            "*.h",
            dst="include",
            src="{basedir}/include".format(basedir=self.ZIP_FOLDER_NAME))
        if not tools.os_info.is_windows:
            self.copy(
                "*.a",
                dst="lib",
                src="{basedir}/_build/.libs".format(basedir=self.ZIP_FOLDER_NAME))
            self.copy(
                "*.so",
                dst="lib",
                src="{basedir}/_build/.libs".format(basedir=self.ZIP_FOLDER_NAME))
        else:
            self.copy(
                "*.dll",
                dst="lib",
                src="{basedir}/win32/".format(basedir=self.ZIP_FOLDER_NAME),
                keep_path=False)
            self.copy(
                "*.lib",
                dst="lib",
                src="{basedir}/win32/".format(basedir=self.ZIP_FOLDER_NAME),
                keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

