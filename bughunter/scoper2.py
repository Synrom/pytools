#! /usr/bin/python2.7
import myCtags
from functions import *
from strip import *
from scoper import *
from signal import signal



done = []

def signal_handler(a,b):
    print "starting logging ..."
    while True:
        try:
            with open("bughunter3.log","w") as f:
                for do in done:
                    f.write(do+"\n")
            print "done"
            return
        except IOError:
            continue
        except OSError:
            continue

signal(1,signal_handler)

def test_call2(call,pos):
    com = ""
    c = 0
    status = 1
    i = pos
    paras = ""
    length = len(call)
    while status == 1 and i < length:
        if com == "":
            if call[i:i+2] in ["/*","//"]:
                if call[i:i+2] == "/*":
                    com = "*/"
                else:
                    com = "\n"
                i += 1
            elif call[i] in "\"'":
                com = call[i]
            elif c > 0:
                paras += call[i]
            else:
                if call[i] != "(" and call[i] != " ":
                    return False
            if call[i] == "(":
                c += 1
            elif call[i] == ")":
                c -= 1
                if c == 0:
                    status = 0
        else:
            if call[i:i+len(com)] == com:
                i +=  len(com) - 1
                com = ""
        i += 1
    status = 1
    while status == 1 and i < length:
        if com == "":
            if i + 1 < len(call) and call[i:i+2] in ["/*","//"]:
                if call[i:i+2] == "/*":
                    com = "*/"
                else:
                    com = "\n"
                i += 1
            elif call[i] not in " \n\t":
                break
        else:
            if call[i:i+len(com)] == com:
                i += len(com) - 1
                com = ""
        i += 1
    if  i >= length or call[i] == "{":
        return False
    return paras[:-1]


def find_calls_by_file2(tags,filename,base,searchfile):
    while True:
        try:
            with open(filename,"r") as f:
                content = f.read()
                break
        except IOError:
            continue
        except OSError:
            continue
    i = 0
    com = ""
    lines = 1
    while i < len(content):
        if content[i] == "\n":
            lines += 1
        if com == "":
            if i < len(content) - 1 and content[i:i+2] in ["/*","//"]:
                if content[i:i+2] == "/*":
                    com = "*/"
                else:
                    com = "\n"
                i += 1
            elif content[i] in ["'",'"']:
                com = content[i]
            elif content[i] == "(":
                p = i-1
                while p >= 0 and content[p] in " \n\t":
                    p -= 1
                if content[p] in "qwqertzuiopasdfghjklyxcvbnm1234567890QWERTZUIOPASDFGHJKLYXCVBNM_":
                    patterns = test_call2(content,i)
                else:
                    i += 1
                    continue
                if patterns == False:
                    i += 1
                    continue
                fname = ""
                while p >= 0 and content[p] in "qwqertzuiopasdfghjklyxcvbnm1234567890QWERTZUIOPASDFGHJKLYXCVBNM_":
                    fname = content[p] + fname
                    p -= 1
                if fname in ["return","if","while","for","switch","case"]:
                    i += 1
                    continue
                status = 0
                for funcit in tags.find_func_by_name(fname):
                    func = find_func_by_tag(funcit,"/home/synrom/lego/linux")
                    if func == ():
                        #print "found a call of "+fname+" in "+filename
                        status = 1
                        break
                    if func[1] == fname:
                        break
                else:
                    i += 1
                    continue
                if status == 1:
                    i += 1
                    continue
                #print "found a call of "+fname+" with ints in "+filename
                patterns = strip_calls(strip_comments(patterns))
                patterns = patterns.replace("\n","")
                patterns = patterns.replace("\t","")
                patterns = patterns.replace(" ","")
                patterns = patterns.split(",")
                for parameter in func[2]:
                    if parameter == 0:
                        continue
                    if func[2][parameter] == "":
                        continue
                    if len(patterns) <= parameter - 1:
                        continue
                    pattern = patterns[parameter - 1] 
                    if "->" in pattern:
                        continue
                    pattern = split_op(pattern)
                    while "" in pattern:
                        pattern.remove("")
                    for p in pattern:
                        if p[:2] == "()":
                            p = p[2:]
                        if "(" in p:
                            ptype = find_type_by_funcname(p[:p.find("(")],tags,base)
                        else:
                            ptype = find_type_by_varname(p,filename,lines,tags,searchfile)
                        ptype = ptype.replace("const","")
                        ftype = func[2][parameter][0].replace("const","")
                        if ptype in ["unsignedint","signedint","int"]:
                            if ptype != ftype:
                                if ptype in ["signedint","int"] and ftype == "unsignedint":
                                    print " ------------------ found something ------------------"
                                    print "1: "+filename+" -> "+func[1]+" at "+str(lines)
                                elif ptype == "unsignedint" and ftype in ["signedint","int"]:
                                    print " ------------------ found something ------------------"
                                    print "2: "+filename+" -> "+func[1]+" at "+str(lines)
                                else:
                                    pass
                                    #print "ptype = "+str(ptype)
                                    #print "func[2][parameter] = "+str(func[2][parameter])
                            else:
                                pass
                                #print "ptype = "+str(ptype)
                                #print "func[2][parameter] = "+str(func[2][parameter])

        else:
            if i + (len(com) - 1) < len(content):
                if content[i:i+len(com)] == com:
                    com = ""
                    i += 1
        i += 1
    global done
    done.append(filename)
    #while True:
    #    try:
    #        with open("bughunter3.log","a") as f:
    #            f.write(filename+"\n")
    #        break
    #    except IOError:
    #        pass
    #    except OSError:
    #        pass
from os.path import isdir,isfile
from os import listdir

import threading

class FileHandler(threading.Thread):
    def __init__(self,tags,filename,direction,searchfile):
        threading.Thread.__init__(self)
        self.tags = tags
        self.filename = filename
        self.direction = direction
        self.searchfile = searchfile
    def run(self):
        find_calls_by_file2(self.tags,self.filename,self.direction,self.searchfile) 
def find_calls_by_dir2(direction,tags,searchdir):
    while True:
        try:
            with open("bughunter2.log","r") as f:
                for file in f.readlines():
                    file = file.replace("\n","")
                    if not isfile(file):
                        print file+" is not a file"
                        continue
                    searchfile = file[file.find(searchdir)+len(searchdir):]
                    handler = FileHandler(tags,file,direction,searchfile)
                    handler.start()
                    #find_calls_by_file2(tags,file,direction,searchfile)
            return
        except IOError:
            continue
        except OSError:
            continue


tags = myCtags.CTags("/home/synrom/lego/linux/tags")
find_calls_by_dir2("/home/synrom/lego/linux",tags,"/home/synrom/lego/linux/")
