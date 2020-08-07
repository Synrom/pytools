#! /usr/bin/python2.7

lines = 0

with open("/home/synrom/lego/linux/tags","r") as f:
    for line in f.readlines():
        lines += 1

with open("bughunter.log","r") as f:
    o = int(f.readline(),10)

print lines
print float(o)/float(lines)
