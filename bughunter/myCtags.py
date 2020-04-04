#! /usr/bin/python2.7

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

def getline(c,i):
    line = ""
    id = i
    while c[id] != '\n' and id >= 0:
        line = c[id] + line
        id -= 1
    iu = i + 1
    while c[iu] != '\n' and iu < len(c):
        line += c[iu]
        iu += 1
    return line

class CTags:
    def __init__(self,filename):
        with open(filename,"r") as f:
            self.tagfile = f.read()
        self.lineNumber = -1
    def tags(self):
        for line in self.tagfile.split("\n")[7:]:
            if "\t" not in line:
                continue
            line = line.replace("\n","").split("\t")
            if line[1][-2:] not in [".h",".c"]:
                continue
            if line[3] not in ["variable","function"]:
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
        content = self.tagfile
        i = content.find(fname)
        while i != -1:
            line = getline(content,i).split("\t")
            if len(line) >= 5:
                if line[3] == "function":
                    if line[1][-2:] in [".c",".h"]:
                        yield Tag(line[1],line[2], int(line[4][line[4].find(":") + 1:],10),line[3])
            content = content[i+1:]
            i = content.find(fname)

