#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class LibnameConan(ConanFile):
    name = "libmp3lame"
    version = "3.100"
    url = "https://github.com/bincrafters/conan-libname"
    description = "LAME is a high quality MPEG Audio Layer III (MP3) encoder licensed under the LGPL."
    license = "http://lame.sourceforge.net/license.txt"
    exports_sources = ["LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"

    def source(self):
        source_url = "https://downloads.sourceforge.net/project/lame/lame/%s/lame-%s.tar.gz" \
                     % (self.version, self.version)
        tools.get(source_url)
        extracted_dir = "lame-" + self.version
        os.rename(extracted_dir, "sources")

        tools.replace_in_file(os.path.join('sources', 'include', 'libmp3lame.sym'), 'lame_init_old\n', '')

    def build_vs(self):
        raise Exception('TODO')

    def build_configure(self):
        with tools.chdir('sources'):
            args = ['--prefix=%s' % self.package_folder]
            if self.options.shared:
                args.extend(['--disable-static', '-enable-shared'])
            else:
                args.extend(['--disable-shared', '--enable-static'])

            env_build = AutoToolsBuildEnvironment(self)
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            self.build_vs()
        else:
            self.build_configure()

    def package(self):
        self.copy(pattern="LICENSE", src='sources')

    def package_info(self):
        self.cpp_info.libs = ['mp3lame']
