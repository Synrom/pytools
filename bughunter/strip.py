#! /usr/bin/python2.7

def strip_comments(content):
    content = content.replace("\\","")
    com = ""
    ncontent = ""
    i = 0
    while i < len(content) - 1:
        if com == "":
            if content[i:i + 2] == "//":
                com = "\n"
            elif content[i:i + 2] == "/*":
                com = "*/"
            elif content[i] in "\"'":
                com = content[i]
                ncontent += content[i]
            else:
                ncontent += content[i]
        else:
            if content[i:i + len(com)] == com:
                i += len(com) - 1
                if com in "\"'":
                    ncontent += content[i]
                com = ""
        i += 1
    if i < len(content) and (com == "" or (com in "\"'" and content[i] == com)):
        ncontent += content[i]
    return ncontent

def strip_calls(content):
    ncontent = ""
    com = 0
    i = 0
    while i < len(content):
        if com == 0:
            ncontent += content[i]
        if content[i] == "(":
            com += 1
        if content[i] == ")":
            com -= 1
            if com == 0:
                ncontent += content[i]
        i += 1
    return ncontent


