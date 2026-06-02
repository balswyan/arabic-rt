# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Tiny CLI: bake/un-bake Arabic from the command line.

    python examples/demo.py "مرحبا بالعالم"
"""
import sys
import arabic_rt as ar


def main(argv):
    text = argv[1] if len(argv) > 1 else "مرحبا بالعالم"
    baked = ar.fix(text, ar.GAME)
    print("input  :", text)
    print("shaped :", ar.shape(text))
    print("baked  :", baked)
    print("unbaked:", ar.unfix(baked))


if __name__ == "__main__":
    main(sys.argv)
