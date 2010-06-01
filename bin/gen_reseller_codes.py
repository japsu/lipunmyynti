#!/usr/bin/env python
# vim: shiftwidth=4 expandtab
# encoding: utf-8

from tracon.shirt_control.pdf import generate
import sys

def main(args):
    num_tshirts, output_filename = args
    num_tshirts = int(num_tshirts)

    generate(num_tshirts, output_filename)

if __name__ == "__main__":
    main(sys.argv[1:])
