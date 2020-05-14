#! /usr/bin/python2.7



def testit(data):
    for c in data:
        if c == "\t":
            return True
        elif c != " ":
            return False
    return True

with open("ergebnisse","r") as f:
    for line in f.readlines():
        if "found something" in line:
            continue
        line = line.split(" ")
        while "" in line:
            line = line.remove("")
        if len(line) < 6:
            continue
        filename = line[1]
        linenumber = int(line[-1],10)
        call = line[3]
        with open(filename,"r") as f:
            print "--------- "+filename+" --------- at "+str(linenumber)
            print "call "+call
            content = f.read()
            content = content.split("\n")
            content = content[:linenumber]
            toprint = ""
            for i in range(0,len(content)):
                if testit(content[len(content) - (i + 1)]):
                    toprint = content[len(content) - (i + 1)] + "\n" + toprint
                else:
                    break
            print toprint
