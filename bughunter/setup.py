#! /usr/bin/python2.7

import os

def doit(path):
    for file in os.listdir(path):
        if os.path.isfile(path+"/"+file):
            if file[-2:] not in [".c",".h"]:
                continue
            with open("bughunter2.log","a") as f:
                f.write(path+"/"+file+"\n")
        elif os.path.isdir(path+"/"+file):
            doit(path+"/"+file)

#doit("/home/synrom/lego/linux")


def test(t):
    with open("bughunter3.log","r") as f:
        for line in f.readlines():
            if t == line:
                return False
    return True

with open("bughunter4.log","w") as f:
    f.write("")
with open("bughunter2.log","r") as f1:
    for line1 in f1.readlines():
        if test(line1):
            with open("bughunter4.log","a") as f2:
                f2.write(line1)
