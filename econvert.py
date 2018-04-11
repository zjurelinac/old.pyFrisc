#! /usr/bin/env python3

import os
import sys


def convert(pfile):
    efile = pfile.rsplit('.', maxsplit=1)[0] + '.e'

    last = -4

    with open(pfile, 'r') as p:
        with open(efile, 'w') as e:
            for line in p:
                pass


if __name__ == '__main__':
    convert(sys.argv[1])
