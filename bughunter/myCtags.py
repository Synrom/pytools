#! /usr/bin/python2.7

from string import printable
from scan import scan

class Tag:
    def __init__(self,filename,pattern,lineNumber,kind):
        self.file = filename
        self.pattern = pattern
        self.lineNumber = lineNumber
        self.kind = kind
    def __str__(self):
        return self.file+" : "+str(self.lineNumber)+" : "+self.pattern+" ("+self.kind+")"
    def __getitem__(self,t):
        if t == "file":
            return self.file
        if t == "pattern":
            return self.pattern
        if t == "lineNumber":
            return self.lineNumber
        if t == "kind":
            return self.kind

def getscope(filename,lineNumber):
    while True:
        try:
            with open(filename,"r") as f:
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
                                    return 0
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
                                    return nline
                        else:
                            if i+(len(com)-1) < len(line) and line[i:i+len(com)] == com:
                                i += len(com) - 1
                                com = ""
                        i += 1
                    nline += 1
                    i =0
            return 0
        except OSError:
            continue
        except IOError:
            continue


def getline(c,i):
    line = ""
    id = i
    while id >= 0 and c[id] != '\n':
        line = c[id] + line
        id -= 1
    iu = i + 1
    while iu < len(c) and c[iu] != '\n':
        line += c[iu]
        iu += 1
    return line

class CTags:
    def __init__(self,filename,log=0):
        with open(filename,"r") as f:
            self.tagfile = f.read()
        print "oeffnen geht"
        while True:
            try:
                with open(filename,"r") as f:
                    self.tagfile = f.read()
                break
            except OSError:
                continue
            except IOError:
                continue
        print "hab die Datei"
        self.log = log
        self.lineNumber = -1
    def scanner(self):
        print "in scanner"
        scan = {}
        last = ""
        length = len(self.tagfile)
        print length
        print "beginne for"
        i = 0
        while i < length:
            if self.tagfile[i] == "\n":
                if i + 2 >= length:
                    continue
                if self.tagfile[i+1:i+3] != last:
                    if last == "zz":
                        print self.tagfile[i+1:i+3]
                        break
                    last = self.tagfile[i+1:i+3]
                    if self.tagfile[i+1:i+3] not in scan:
                        scan.update({self.tagfile[i+1:i+3]:i+1})
                        print scan
                        print float(i)/float(length)
                    else:
                        print "Fehler mit "+self.tagfile[i+1:i+3]
            i += 1
        print "I am out"
        print scan
        for s in scan:
            print s+" -> "+str(scan[s])
            print getline(self.tagfile,scan[s])
        with open("scan.py","w") as f:
            f.write(str(scan))


    def tags(self):
        for line in self.tagfile.split("\n")[7+self.log:]:
            if "\t" not in line:
                yield ()
                continue
            line = line.replace("\n","").split("\t")
            if line[1][-2:] not in [".h",".c"]:
                yield ()
                continue
            if line[3] not in ["variable","function"]:
                yield ()
                continue
            yield Tag(line[1],line[2],int(line[4][line[4].find(":") + 1:],10),line[3])
    def get_funcs_by_file(self,fname):
        content = self.tagfile
        i = content.find(fname)
        while i != -1:
            line = getline(content,i).split("\t")
            if line[1] == fname:
                if line[3] == "function":
                    self.lineNumber =  int(line[4][line[4].find(":") + 1:],10)
                    yield Tag(line[1],line[2],self.lineNumber,line[3])
            content = content[i + 1:]
            i = content.find(fname)
    def find_func_by_name(self,fname):
        #print "searching for "+fname
        searcher = fname[:2]
        global scan
        if searcher not in scan:
            #print "........................................."
            #print searcher+" ist einfach nicht in scan"
            return
        i = scan[searcher]
        while i < len(self.tagfile):
            if self.tagfile[i] == "\n":
                if self.tagfile[i+1] != fname[0] or self.tagfile[i+2] > fname[1]:
                    return
                if self.tagfile[i+1:i+1+len(fname)] == fname:
                    line = getline(self.tagfile,i+1)
                    line = line.split("\t")
                    if len(line) >= 5:
                        if line[3] == "function":
                            if line[1][-2:] in [".c",".h"]:
                                yield Tag(line[1],line[2], int(line[4][line[4].find(":") + 1:],10),line[3])
            i += 1
                
    def function_line(self,filename,line_number,direction):
        content = self.tagfile
        i = content.find(filename)
        while i != -1:
            line = getline(content,i).split("\t")
            if len(line) >= 5:
                if line[3] == "function":
                    number = int(line[4][line[4].find(":") + 1:],10)
                    if number < line_number:
                        scope = getscope(direction+"/"+filename, number)
                        if scope >= line_number:
                            return Tag(line[1],line[2],number,line[3])
            content = content[i+1:]
            i = content.find(filename)
        #print "found no function scope for "+filename+" at "+str(line_number)

if "__main__" == __name__:
    tags = CTags("/home/synrom/lego/linux/tags")
    tags.scanner()

