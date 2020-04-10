#! /usr/bin/python2.7

#from pwn import *

#context.terminal = ["tmux","split","-h"]

from shellcode import shellcode




print len(shellcode)

#ps = process("./loader")

#gdb.attach(ps)


#ps.sendline(shellcode)

with open("shellcode.bin","wb") as f:
    f.write(shellcode)
