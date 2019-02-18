#!/usr/bin/python 3

""" This creates a docstrings.tsv file.

The file can be opened in Excel to check and make sure that argument docstring values are consistent
across modules. """

# import modules.
import glob
import os

# get Python files.
py_files = glob.glob("../placissimo/**", recursive=True)
py_files = [f for f in py_files if f.endswith(".py") if f != os.path.basename(__file__)]

# capture argument docstrings.
args = []
for pyf in py_files:
    
    with open(pyf) as f:
        
        temp = []
        capture = False
        
        for line in f.readlines():
            if line.strip().startswith("Args:"):
                capture = True
            if line.strip() == "":
                capture = False
            if capture:
                temp.append(line)

    temp2 = ""
    for t in temp:
        if t.strip().startswith("-"):
            if temp2 != "":
                args.append((temp2, os.path.basename(pyf)))
            temp2 = ""
        if not t.strip().startswith("Args:") and not t.strip().startswith('"""'):
            temp2 += t.strip() + " "

# write to file.
with open("docstrings.tsv", "w") as f:
    for arg in args:
        line = "'{}'\t'{}'\n".format(arg[0], arg[1])
        f.write(line)
