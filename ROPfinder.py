#! /usr/bin/python2.7

from r2pipe import open
from sys import argv

if len(argv) < 2:
    print "usage:"
    print "\t"+argv[0]+" <filename>"
    exit(1)


r2 = open(argv[1])

r2.cmd("s entry0")

laddr = 0x0
caddr = 0x1
cmds = 3
condition = ""


def controll(ds):
    global condition
    global cmds
    for i in range(0,cmds):
        try:
            if condition in ds[i][u'disasm']:
                return True
        except KeyError:
            break
    return False



while caddr != laddr:
    ds = r2.cmdj("pdj "+str(cmds))
    laddr = caddr
    caddr = ds[0][u'offset']
    try:
        if "ret" in ds[cmds - 1][u'disasm']:
            if controll(ds):
                print " ----------------- "+hex(caddr)+" ------------------"
                for i in range(0,cmds):
                    print ds[i][u'disasm']
                print "----------------------------------------------------"
                print
    except KeyError:
        pass
    r2.cmd("s +1")


