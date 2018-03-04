from json import dump
from yaml import load
from sys import argv

with open(argv[1]) as f:
    d = load(f)

with open(argv[2], 'w') as f:
    dump(d, f)
