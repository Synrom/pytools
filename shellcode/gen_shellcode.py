#! /usr/bin/python2.7
import sys,random,os
import r2pipe, capstone,struct

def test_func(addr):
    global functions
    for call in functions:
        if addr == call[0]:
            return True
    return False
if len(sys.argv) < 2:
    print "usage:"
    print "python "+sys.argv[0]+" <filename>"
    exit()

compile = False
filename = sys.argv[1]
if filename.split(".")[1] == "c":
    filename_new = hex(random.randint(1,1254124124))
    os.system("gcc "+filename+" -fno-stack-protector -o "+filename_new)
    compile = True
    filename = filename_new


try:
    f_stream = open(filename,"r")
except Exception as e:
    print e
    exit()
f_stream.close()

r2 = r2pipe.open(filename)
r2.cmd("aas")
r2.cmd("s sym.main")

def test_jmp(disasm):
    instrs = ["je","jz","jne","jnz","jg","jnle","jge","jnl","jl","jnge","jle","jng",
        "ja","jnbe","jae","jnb","jb","jnae","jbe","jna","jmp","jxcz","jc","jnc","jo",
        "jno","jp","jpe","jnp","jpo","js","jns"]
    for instr in instrs:
        if instr in disasm:
            return True
    return False

functions = []
jmps = {}
syscalls = []
functions_r2_shell = []
functions_addrc = []

def find_instrs(addr):
    global r2
    global functions
    global syscalls
    r2.cmd("s "+hex(addr))
    instrs = r2.cmdj("pdfj")[ u'ops' ]
    for instr in instrs:
        if "call" in instr[ u'disasm' ]:
            if "syscall" in instr[ u'disasm' ]:
                syscalls.append(instr[ u'offset' ])
            else:
                functions.append(instr[ u'offset' ])
                addrn = instr[ u'disasm' ].split(" ")[1]
                find_instrs(addrn)
                r2.cmd("s "+hex(addr))
        if test_jmp(instr[ u'disasm' ]):
            scope = (instr[ u'jump' ] - instr[ u'offset' ]) 
            print "scope = "+str(scope)
            scope -=  instr[ u'size' ]
            print "scope = "+str(scope)
            jmps.update({instr[ u'offset' ]:[scope,0]})




r2.cmd("s sym.main")
addr = r2.cmdj("pdj 1")[0][ u'offset' ] 
find_instrs(addr)
byte = r2.cmd("pf b").split(" ")[2][1:].replace("\n","").replace("\t","")
# prefix to not crush our shellcode
#bytes = "\\x48\\x8d\\x25\\x00\\x00\\x00\\x00"
bytes = ""
vormerken = []
while byte != "xc3":
    bytes += "\\"+byte
    r2.cmd("s+ 1")
    addr = r2.cmdj("pfj d")[0][ u'offset']
    if addr in functions:
        bytes += "\\xe8"
        there = False
        call = r2.cmdj("pdj 1")[0][ u'disasm' ].split(" ")[1]
        for i in range(0,len(functions_r2_shell)):
            if functions_r2_shell[i][0] == call:
                functions_r2_shell[i][1].append(len(bytes))
                there = True
        if not there:
            functions_r2_shell.append((call,[len(bytes)]))
        bytes += "\\x00\\x00\\x00\\x00"
        addr = r2.cmdj("pdj 2")[1][ u'offset' ]
        r2.cmd("s "+hex(addr))
    if addr in syscalls:
        for jmp in jmps:
            scope = jmps[jmp][0]
            if jmp < addr:
                if jmp + scope >= addr:
                    scope += 20
            elif jmp > addr:
                if jmp + scope < addr:
                    scope -= 20
            #print "new scope = "+str(scope)
            #print "jmp = "+str(jmp)
            #print "addr = "+str(addr)
            jmps[jmp][0] = scope


        addr = r2.cmdj("pdj 2")[1][ u'offset']
        r2.cmd("s "+hex(addr))
        bytes += "\\x48\\x89\\xf8\\x48\\x89\\xf7"
        bytes += "\\x48\\x89\\xd6"
        bytes += "\\x48\\x89\\xca"
        bytes += "\\x4d\\x89\\xc2"
        bytes += "\\x4d\\x89\\xc8"
        bytes += "\\x4c\\x8b\\x4c\\x24\\x08"
        bytes += "\\x0f\\x05"
    if addr in jmps:
        jmps[addr][1] = len(bytes)
    byte = r2.cmd("pf b").split(" ")[2][1:].replace("\n","").replace("\t","")
    #if byte == "xc3" and len(tojmp) != 0:
        #r2.cmd("s "+hex(tojmp.pop()))
        #byte = r2.cmd("pf b").split(" ")[2][1:]

bytes += "\\x48\\x31\\xff"
bytes += "\\x48\\xc7\\xc0\\x3c\\x00\\x00\\x00"
bytes += "\\x0f\\x05"



for item in functions_r2_shell:
    pos = len(bytes)
    functions_addrc.append((item[0],pos))
    r2.cmd("s "+item[0])
    byte = r2.cmd("pf b").split(" ")[2][1:].replace("\n","").replace("\t","")
    while byte != "xc3":
        bytes += "\\"+byte
        r2.cmd("s+ 1")
        addr = r2.cmdj("pfj d")[0][ u'offset'] 
        if addr in functions:
            bytes += "\\xe8"
            there = False
            call = r2.cmdj("pdj 1")[0][ u'disasm' ].split(" ")[1]
            for i in range(0,len(functions_r2_shell)):
                if functions_r2_shell[i][0] == call:
                    functions_r2_shell[i][1].append(len(bytes))
                    there = True
            if not there:
                functions_r2_shell.append((call,[len(bytes)]))
            bytes += "\\x00\\x00\\x00\\x00"
            addr = r2.cmdj("pdj 2")[1][ u'offset' ]
            r2.cmd("s "+hex(addr))
        if addr in syscalls:
            for jmp in jmps:
                scope = jmps[jmp][0]
                if jmp < addr:
                    if jmp + scope >= addr:
                        scope += 20
                elif jmp > addr:
                    if jmp + scope < addr:
                        scope -= 20

            addr = r2.cmdj("pdj 2")[1][ u'offset']
            r2.cmd("s "+hex(addr))
            bytes += "\\x48\\x89\\xf8\\x48\\x89\\xf7"
            bytes += "\\x48\\x89\\xd6"
            bytes += "\\x48\\x89\\xca"
            bytes += "\\x4d\\x89\\xc2"
            bytes += "\\x4d\\x89\\xc8"
            bytes += "\\x4c\\x8b\\x4c\\x24\\x08"
            bytes += "\\x0f\\x05"
        byte = r2.cmd("pf b").split(" ")[2][1:].replace("\n","").replace("\t","")
    bytes += "\\xc3"

for item in functions_addrc:
    for item_r2 in functions_r2_shell:
        if item_r2[0] == item[0]:
            for item_code in item_r2[1]:
                pos = (item[1] - item_code) / 4
                pos -= 4
                a1 = pos & 0xff000000
                a1 = a1 >> ( 8 * 3)
                a2 = pos & 0x00ff0000
                a2 = a2 >> ( 8 * 2)
                a3 = pos & 0x0000ff00
                a3 = a3 >> 8
                a4 = pos & 0x000000ff
                payload = "\\x%.2x\\x%.2x\\x%.2x\\x%.2x" % ( a4 , a3 , a2 , a1 )
                bytes = bytes[:item_code] + payload + bytes[item_code+len(payload):] 

for jmp in jmps:
    pos = jmps[jmp][1] + 4
    scope = jmps[jmp][0]
    if scope < 128 and scope > -128:
        b = struct.unpack("B",struct.pack("b",scope))[0]
        b = "\\x%.2x" % (b)
        bytes = bytes[:pos] + b + bytes[pos + 4:]
    else:
        b = struct.unpack("I",struct.pack("i",scope))[0]
        b1 = "\\x%.2x" %  ( 0x000000ff & b ) 
        b2 = "\\x%.2x" %  (( 0x0000ff00 & b ) / 255 )
        b3 = "\\x%.2x" %  (( 0x00ff0000 & b ) / (255 ** 2) )
        b4 = "\\x%.2x" %  (( 0xff000000 & b ) / (255 ** 3) )
        bytes = bytes[:pos] + b1 + b2 + b3 + b4 + bytes[pos + 16:]



plus = 0
number = "\\x%.2x" % ((len(bytes)+plus) & 0x000000ff)
number += "\\x%.2x"% (((len(bytes)+plus) & 0x0000ff00) / (255 ** 1))
number += "\\x%.2x"% (((len(bytes)+plus) & 0x00ff0000) / (255 ** 2))
number += "\\x%.2x"% (((len(bytes)+plus) & 0xff000000) / (255 ** 3))


bytes = "\\x48\\x81\\xec"+ number + bytes

length = len(bytes)
a = 10 * 4
if a > length:
    a = length
print "shellcode =  \"" + bytes[:a] + "\""

for i in range(a,len(bytes),10*4):
    if i + 10 *4 > length:
        print "shellcode += \"" + bytes[i:] + "\""
        break
    print "shellcode += \"" + bytes[i:(i+10*4)] + "\""

if compile:
    os.system("rm "+filename)
