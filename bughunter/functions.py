#! /usr/bin/python2.7

# ctags --fields=+n --fields=+K --fields=+S --fields=+t -R .


from myCtags import *


from strip import *

def function_scope(filename,lineNumber,direction):
    with open(direction+"/"+filename,"r") as f:
        nline = lineNumber
        com = ""
        c = 0
        status = 1
        i = 0
        for line in f.readlines()[lineNumber - 1:]:
            if nline < lineNumber:
                nline += 1
                continue
            while status == 1 and i < len(line):
                if com == "":
                    if i+1 < len(line) and line[i:i+2] in ["/*","//"]:
                        if line[i:i+2] == "/*":
                            com = "*/"
                        else:
                            com = "\n"
                        i += 1
                    elif line[i] in "\"'":
                        com  = line[i]
                    elif line[i] == "(":
                        c += 1
                    elif line[i] == ")":
                        c -= 1
                        if c == 0:
                            status = 2
                else:
                    if i+(len(com) - 1) < len(line) and line[i:i+len(com)] == com:
                        i += len(com) - 1
                        com = ""
                i += 1
            while status == 2 and i < len(line):
                if com == "":
                    if i + 1 < len(line) and line[i:i+2] in ["/*","//"]:
                        if line[i:i+2] == "/*":
                            com = "*/"
                        else:
                            com = "\n"
                        i += 1
                    elif line[i] not in " \t\n":
                        if line[i] != "{":
                            return (0,0)
                        status = 3
                        break
                else:
                    if i + (len(com) -1) < len(line) and line[i:i+len(com)] == com:
                        i += len(com) - 1
                        com = ""
                i += 1
            while status == 3 and i < len(line):
                if com == "":
                    if i+1 < len(line) and line[i:i+2] in ["/*","//"]:
                        if line[i:i+2] == "/*":
                            com = "*/"
                        else:
                            com = "\n"
                        i += 1
                    elif line[i] in "\"'":
                        com = line[i]
                    elif line[i] == "{":
                        c += 1
                    elif line[i] == "}":
                        c -= 1
                        if c == 0:
                            return (lineNumber,nline)
                else:
                    if i+(len(com)-1) < len(line) and line[i:i+len(com)] == com:
                        i += len(com) - 1
                        com = ""
                i += 1
            nline += 1
            i =0
    return (0,0)




def find_vars_by_line(line):
    struct = {}
    line = line.replace("\t","")
    patterns = strip_calls(strip_comments(line.split(";")[0])).split(",")
    ptype = patterns[0].split(" ")
    while "" in ptype:
        ptype.remove("")
    if len(ptype) < 2:
        return struct
    if "int" != ptype[0] and "int" != ptype[1]:
        return struct
    if ptype[0] in ["unsigned","signed"]:
        ptype = "".join(ptype[:2])
    else:
        ptype = "".join(ptype[:1])
    pnames = []
    patterns[0] = patterns[0][patterns[0].find("int")+3:]
    for pattern in patterns:
        if "=" not in pattern and "*" not in pattern:
            pnames.append(pattern.replace(" ",""))
        else:
            pname = pattern.split("=")[0]
            if "*" in pname:
                continue
            pnames.append(pname.replace(" ",""))
    for pname in pnames:            
        if pname not in struct:
            struct.update({pname:ptype})
    return struct

def check(ptypes):
    for i in range(1,100):
        if i not in ptypes:
            break
        if ptypes[i][0] == "unsignedint" or ptypes[i][0] == "signedint":
            return True
    return False




def find_func_by_tag(e,direction):
    patterns = strip_comments(e.pattern[2:-2].split(";")[0])
    fname = patterns.split("(")[0].split(" ")
    while "" in fname:
        fname.remove("")
    ftype = fname[:-1]
    if "*" in "".join(ftype) or fname[-1][0] == "*":
        ftype = ""
    elif "int" not in ftype:
        ftype = ""
    else:
        if "unsigned" in ftype:
            ftype = "unsignedint"
        else:
            ftype = "signedint"
    fname = fname[-1]
    fname = fname.replace("*","")
    patterns = patterns[patterns.find("(") + 1:patterns.find(")") ]
    ptypes = {}
    ptypes.update({ 0 : ftype })
    i = 1
    for pattern in patterns.split(","):
        if "*" in pattern:
            ptypes.update({i : ("","") })
            continue
        if "int " in pattern:
            pattern_name = pattern.split("int ")[1]
        else:
            pattern_name = ""
        pattern = pattern.split(" ")
        while "" in pattern:
            pattern.remove("")
        if "int" not in pattern:
            pattern = ""
        else:
            if "unsigned" in pattern:
                pattern = "unsignedint"
            else:
                pattern = "signedint"
        ptypes.update({i : (pattern,pattern_name)})
        i += 1
    if not check(ptypes):
        return ()
    return (e.file,fname, ptypes ,e.lineNumber , function_scope(e.file,e.lineNumber,direction)) 


def find_type_by_funcname(fname,tags,direction):
    for tag in tags.find_func_by_name(fname):
        func = find_func_by_tag(tag,direction)
        if func == ():
            continue
        if func[1] == fname:
            return func[2][0]

##print strip_comments("/^unsigned 	\/* asdf *\/ int ooo;$/")
##print strip_calls(strip_comments("/^unsigned int ooo = print(ha /* ) */llo,o(o,q));$/"))
##print strip_calls(strip_comments("/^unsigned int oo = print(\" ( /* // \"), l = /* // \" */ 10"))
##print strip_calls(strip_comments(' /* " */ "hallo"'))



#tags = CTags("/home/synrom/linux/tags")
#for tag in tags.get_tags_by_file("drivers/block/ps3disk.c"):
#    if tag.kind == "function":
#        print find_func_by_tag(tag)
#    elif tag.kind == "variable":
#        print find_vars_by_tag(tag)

#tags = CTags("try/tags")
#for tag in tags.tags():
#    if tag.kind == "function":
#        print find_func_by_tag(tag,"try")


#TODO Macros ersetzen
