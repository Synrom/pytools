#! /usr/bin/python2.7

import os
import sys
from myCtags import CTags,getline
from functions import function_scope
from scoper import test_call
from strip import strip_calls, strip_comments

def find_func_by_tag_for_finder(e,direction):
    patterns = strip_comments(e.pattern[2:-2].split(";")[0])
    fname = patterns.split("(")[0].split(" ")
    while "" in fname:
        fname.remove("")
    fname = fname[-1]
    fname = fname.replace("*","")
    return (e.file,fname, e.lineNumber  ) 

#TODO: function_scope selber umschreiben damit der Funktionsname zurueckgegeben wird

r = 0


def find_calls_by_file(func,filename,tags,direction,grad):
    if func == ():
        return
    if func[1] == "":
        return 
    global r
    #print "find calls by file:"
    #print "func = "+str(func)
    #print "filename = "+str(filename)
    #print "tags = "+str(tags)
    #print "direction = "+str(direction)
    #print "grad = "+str(grad)
    lines = 1
    while True:
        try:
            with open(filename,"r") as f:
                content = f.read()
            break
        except OSError:
            continue
        except IOError:
            continue
    call = content.find(func[1])
    lines += content[:call].count("\n")
    while call != -1:
        if content[call - 1] in "qwertzuiopasdfghjklyxcvbnm1234567890_QWERTZUIOPASDFGHJKLYXCVBNM":
            content = content[call + 1:]
            call = content.find(func[1])
            lines += content[:call].count("\n")
            continue
        patterns = test_call(content[call:],func[1])
        if patterns != False:
            nfilename = filename[filename.find(direction)+len(direction)+1:]
            #print "nfilename = "+nfilename
            calling_function = tags.function_line(nfilename,lines,direction)
            if calling_function != None:
                calling_function = find_func_by_tag_for_finder(calling_function,direction)[1]
                print "\t" * grad+calling_function
                if r == 1:
                    for funcit in tags.find_func_by_name(calling_function):
                        tag = find_func_by_tag_for_finder(funcit,direction)
                        find_calls_by_dir(tag,tags,direction,direction,grad+1)
        content = content[call + 1:]
        call = content.find(func[1])
        lines += content[:call].count("\n")


tags = CTags("/home/synrom/lego/linux/tags")

import threading

class CallFinder(threading.Thread):
    def __init__(self,func,filename,tags,direction,grad):
        self.func = func
        self.filename = filename
        self.tags = tags
        self.direction = direction
        self.grad = grad
        threading.Thread.__init__(self)
    def run(self):
        find_calls_by_file(self.func,
            self.filename,self.tags,self.direction,self.grad)
        
        
        


def find_calls_by_dir(func,tags,filename,direction,grad):
    #print "find calls by dir:"
    #print "func = "+str(func)
    #print "filename = "+str(filename)
    #print "tags = "+str(tags)
    #print "direction = "+str(direction)
    for file in os.listdir(filename):
        if os.path.isdir(filename+"/"+file):
            find_calls_by_dir(func,tags,filename+"/"+file,direction,grad)
        elif os.path.isfile(filename+"/"+file):
            if file[-2:] not in [".c",".h"]:
                continue
            #sys.stdout.write("searching in "+filename+"/"+file+" ...")
            #sys.stdout.flush()
            findit = CallFinder(func,filename+"/"+file,tags,direction,grad)
            findit.start()
            #find_calls_by_file(func,filename+"/"+file,tags,direction,grad)
            #sys.stdout.write("done\n")
            #sys.stdout.flush()

direction_glob = "/home/synrom/lego/linux"
for func in tags.find_func_by_name("__get_free_pages"):
    tag = find_func_by_tag_for_finder(func,direction_glob)
    print tag[1]
    find_calls_by_dir(tag,tags,direction_glob,direction_glob,1)
