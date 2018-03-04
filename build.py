#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default
from bincrafters import build_shared
import os


def add_build_requires(builds):
    if os.getenv('MINGW_CONFIGURATIONS', ''):
        return map(add_required_installers, builds)
    else:
        return builds


def add_required_installers(build):
    installers = ['mingw_installer/1.0@conan/stable', 'msys2_installer/latest@bincrafters/stable']
    build.build_requires.update({"*": installers})
    return build


if __name__ == "__main__":

    builder = build_template_default.get_builder()

    builder.items = add_build_requires(builder.items)

    builder.run()
