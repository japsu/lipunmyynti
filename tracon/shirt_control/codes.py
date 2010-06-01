# encoding: utf-8
# vim: shiftwidth=4 expandtab

from random import randint

NUM_LENGTH=6

def generate_code():
    return str(randint(10**(NUM_LENGTH-1), 10**NUM_LENGTH-1))
