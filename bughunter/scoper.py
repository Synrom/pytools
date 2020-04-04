#! /usr/bin/python2.7
from os.path import isdir,isfile
from os import listdir
from strip import strip_comments,strip_calls
from myCtags import *
from functions import *


def test_call(call,fname):
    if call[:len(fname)] != fname:
        return False
    com = ""
    c = 0
    status = 1
    i = len(fname)
    paras = ""
    while status == 1:
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
    while status == 1:
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
    if call[i] == "{":
        return False
    return paras[:-1]

def split_op(pattern):
    if "+" in pattern:
        return pattern.split("+")
    if "-" in pattern:
        return pattern.split("-")
    if "*" in pattern:
        return pattern.split("*")
    if "/" in pattern:
        return pattern.split("/")
    if "^" in pattern:
        return pattern.split("^")
    if "<<" in pattern:
        return pattern.split("<<")
    if ">>" in pattern:
        return pattern.split(">>")
    if "~" in pattern:
        return pattern.split("~")
    if "&" in pattern:
        return pattern.split("&")
    if "|" in pattern:
        return pattern.split("|")
    return [pattern]

def find_type_by_varname(var,fname,lineNumber,tags,searchfile):
    if var == "":
        return {}
    with open(fname,"r") as f:
        content = f.read()
    call = content.find(var)
    status = 1
    if var in "unsigned int":
        status = 0
        counter = 0
    while call != -1:
        if call+len(var) < len(content):
            if content[call+len(var)] in " =,;":
                line = getline(content,call)
                line = line.replace("\t","")
                if "int" in strip_calls(strip_comments(line)).split(" "):
                    variables = find_vars_by_line(line)
                    if var in variables:
                        return variables[var]
            if status == 0:
                if content[call+len(var)] in "qwertzuiopasdfghjklyxcvbnm1234567890_QWERTZUIOPASDFGHJKLYXCVBNM":
                    call = content[call+1:].find(var) + call + 1
                    continue
        content = content[call+1:]
        call = content.find(var)
    for func in tags.get_funcs_by_file(searchfile):
        sfunc = fname
        sfunc = sfunc[:sfunc.find(searchfile)]
        func = find_func_by_tag(func,sfunc)
        if func == ():
            continue
        if lineNumber >= func[3] and lineNumber <= func[4][1]:
            for i in func[2]:
                if i == 0:
                    continue
                if var == func[2][i][1]:
                    return func[2][i][0]
    return {}


def find_calls_by_file(func,filename,tags,direction,searchfile):
    if func[1] == "":
        return 
    lines = 1
    with open(filename,"r") as f:
        content = f.read()
    call = content.find(func[1])
    lines += content[:call].count("\n")
    while call != -1:
        if content[call - 1] in "qwertzuiopasdfghjklyxcvbnm1234567890_QWERTZUIOPASDFGHJKLYXCVBNM":
            content = content[call + 1:]
            call = content.find(func[1])
            lines += content[:call].count("\n")
            continue
        patterns = test_call(content[call:],func[1])
        if patterns:
            print "found a call of "+func[1]+" in "+filename+" at "+str(lines)
            patterns = strip_calls(strip_comments(patterns))
            patterns = patterns.split(",")
            for parameter in func[2]:
                if parameter == 0:
                    continue
                if  func[2][parameter] == "":
                    continue
                if len(patterns) <= parameter - 1:
                    continue
                pattern = patterns[parameter - 1]
                if "->" in pattern:
                    continue
                pattern = pattern.replace(" ","")
                pattern = split_op(pattern)
                while "" in pattern:
                    pattern.remove("")
                for p in pattern:
                    if p[:2] == "()":
                        p = p[2:]
                    if "(" in p:
                        ptype = find_type_by_funcname(p[:p.find("(")],tags,direction)
                    else:
                        ptype = find_type_by_varname(p,filename,lines,tags,searchfile)
                    if ptype in ["unsignedint","signedint","int"]:
                        if ptype != func[2][parameter]:
                            if ptype in ["signedint","int"] and func[2][parameter][0] == "unsignedint":
                                print filename+" -> "+func[1]
                            elif ptype == "unsignedint" and func[2][parameter][0] in ["signedint","int"]:
                                print filename+" -> "+func[1]
                            else:
                                pass
                                print "ptype = "+str(ptype)
                                print "func[2][parameter] = "+str(func[2][parameter])
                        else:
                            pass
                            print "ptype = "+str(ptype)
                            print "func[2][parameter] = "+str(func[2][parameter])

        content = content[call + 1:]
        call = content.find(func[1])
        lines += content[:call].count("\n")

def find_calls_by_dir(func,directon,tags,searchdir):
    for file in listdir(directon):
        if isfile(directon+"/"+file) and file[-2:] in [".c",".h"]:
            #print "searching in "+directon+"/"+file
            searchfile = directon+"/"+file
            searchfile = searchfile[searchfile.find(searchdir)+len(searchdir):]
            find_calls_by_file(func,directon+"/"+file,tags,directon,searchfile)
        elif isdir(directon+"/"+file):
            find_calls_by_dir(func,directon+"/"+file,tags,searchdir)
    
tags = CTags("/home/synrom/linux/tags")
for tag in tags.tags():
    if tag.kind == "function":
        func = find_func_by_tag(tag,"/home/synrom/linux")
        if func != ():
            if "DEFINE" in func[1]:
                continue
            print "search for function "+func[1]
            find_calls_by_dir(func,"/home/synrom/linux",tags,"/home/synrom/linux/")
     
    
    
