#!/usr/bin/env python
# vim: shiftwidth=4 expandtab
# encoding: utf-8

from tracon.control_slips.pdf import interleave
import sys

def main(args):
    output, backside, body = args
    interleave(output, backside, body)

if __name__ == "__main__":
    main(sys.argv[1:])

