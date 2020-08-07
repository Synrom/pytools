#! /usr/bin/python2.7

from os import listdir
from os.path import isdir,isfile 


files =  155257

def doit(path):
    global files
    for file in listdir(path):
        if isfile(path+"/"+file) and file[-2:] in [".c",".h"]:
            files += 1
        elif isdir(path+"/"+file):
            doit(path+"/"+file)


lines = 0
with open("bughunter3.log","r") as f:
    for line in f.readlines():
        if line != "":
            lines += 1

print lines
print float(lines) / float(files)
