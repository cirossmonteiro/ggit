import sys

from ggit import *

cmd, args = sys.argv[1], sys.argv[2:]

if cmd == "init":
    Ggit.init()

elif cmd == "branch":
    with open(".ggit/branches", 'r') as fh:
        for line in fh.readlines():
            ls = line.split(" ")
            branch, commit = ls[0], ls[1] if len(ls) == 2 else None
            print(branch)

elif cmd == "add":
    if len(args) == 0:
        raise Exception("At least ONE argument must be provided.")
    Ggit.add(args)


elif cmd == "commit":
    Ggit.commit()

elif cmd == "status":
    Ggit.status()
