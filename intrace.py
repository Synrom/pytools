#! /usr/bin/python2.7

import r2pipe
import sys

if len(sys.argv) < 3:
    print "usage:"
    print "\t"+sys.argv[0]+" <file>  <function>"
    exit()


name = sys.argv[2]
r2 = r2pipe.open(sys.argv[1])

r2.cmd("ood")
r2.cmd("db main")
rep = r2.cmd("dc")
print "main"

length = len(r2.cmdj("dbtj"))

while "Process finished" not in rep:
    dis = r2.cmdj("pdj 2@rip")
    if "call" not in dis[0][ u'disasm' ] or "0x" in dis[0][ u'disasm' ]:
        rep = r2.cmd("dcc")
        continue
    if "imp" in dis[0][ u'disasm' ]:
        addr = dis[1][ u'offset' ]
        r2.cmd("db "+str(addr))
        r2.cmd("dc")
        r2.cmd("db- "+str(addr))
        continue
    fname = dis[0][ u'disasm' ].split("call")[1].replace(" ","")
    if fname == name:
        print "--------------------- "+name+" ---------------------"
        exit()

    length = len(r2.cmdj("dbtj"))
    if length < 2:
        exit()
    print "  " * length + fname
    rep = r2.cmd("dcc")
    





