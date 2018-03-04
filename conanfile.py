#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os
import shutil


class LibMP3LameConan(ConanFile):
    name = "libmp3lame"
    version = "3.100"
    url = "https://github.com/bincrafters/conan-libname"
    description = "LAME is a high quality MPEG Audio Layer III (MP3) encoder licensed under the LGPL."
    homepage = "http://lame.sourceforge.net/"
    license = "LGPL"
    exports_sources = ["LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"

    @property
    def is_mingw(self):
        return self.settings.compiler == 'gcc' and self.settings.os == 'Windows'

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        source_url = "https://downloads.sourceforge.net/project/lame/lame/%s/lame-%s.tar.gz" \
                     % (self.version, self.version)
        tools.get(source_url)
        extracted_dir = "lame-" + self.version
        os.rename(extracted_dir, "sources")

        tools.replace_in_file(os.path.join('sources', 'include', 'libmp3lame.sym'), 'lame_init_old\n', '')

    def build_vs(self):
        with tools.chdir('sources'):
            shutil.copy('configMS.h', 'config.h')
            command = 'nmake -f Makefile.MSVC comp=msvc asm=yes'
            if self.settings.arch == 'x86_64':
                tools.replace_in_file('Makefile.MSVC', 'MACHINE = /machine:I386', 'MACHINE =/machine:X64')
                command += ' MSVCVER=Win64'
            if self.options.shared:
                command += ' dll'
            with tools.vcvars(self.settings, filter_known_paths=False, force=True):
                self.run(command)

    def build_configure(self):
        with tools.chdir('sources'):
            prefix = os.path.abspath(self.package_folder)
            if self.is_mingw:
                prefix = tools.unix_path(prefix, tools.MSYS2)
            args = ['--prefix=%s' % prefix]
            if self.options.shared:
                args.extend(['--disable-static', '-enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])
            if self.settings.build_type == 'Debug':
                args.append('--enable-debug')
            if self.settings.os != 'Windows' and self.options.fPIC:
                args.append('--with-pic')

            env_build = AutoToolsBuildEnvironment(self, win_bash=self.is_mingw)
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self.build_vs()
        elif self.is_mingw:
            msys_bin = self.deps_env_info['msys2_installer'].MSYS_BIN
            with tools.environment_append({'PATH': [msys_bin],
                                           'CONAN_BASH_PATH': os.path.join(msys_bin, 'bash.exe')}):
                self.build_configure()
        else:
            self.build_configure()

    def package(self):
        self.copy(pattern="LICENSE", src='sources')
        if self.settings.compiler == 'Visual Studio':
            self.copy(pattern='*.h', src=os.path.join('sources', 'include'), dst=os.path.join('include', 'lame'))
            self.copy(pattern='*.lib', src=os.path.join('sources', 'output'), dst='lib')
            self.copy(pattern='*.exe', src=os.path.join('sources', 'output'), dst='bin')
            if self.options.shared:
                self.copy(pattern='*.dll', src=os.path.join('sources', 'output'), dst='bin')

    def package_info(self):
        if self.settings.compiler == 'Visual Studio':
            self.cpp_info.libs = ['libmp3lame' if self.options.shared else 'libmp3lame-static']
        else:
            self.cpp_info.libs = ['mp3lame']
