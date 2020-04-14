#! /usr/bin/python2.7
from urllib2 import urlopen
import sys

search = raw_input("search> ").lower()

iss_num = 1
phi_num = 1

list_1 = []

def count(page,search):
    if " " not in search:
        return page.count(search)
    searchs = search.split(" ")
    results = []
    for s in searchs:
        results.append( page.count(s) )
    mul = len(results) - results.count(0)
    res = 0
    for r in results:
        res += r
    return res * mul

while True:
    try:
        sys.stdout.write("\rissue "+hex(iss_num)+" Phile "+hex(phi_num))
        sys.stdout.flush()
        page = urlopen("http://www.phrack.org/archives/issues/"+str(iss_num)+"/"+str(phi_num)+".txt").read().lower()
        if search.split(" ")[0] in page:
            list_1.append( (count(page,search),iss_num,phi_num) )
    except Exception as e:
        if phi_num == 1:
            break
        else:
            phi_num = 1
            iss_num += 1
            continue
    phi_num += 1

sys.stdout.write("\rsearch is over\n")
sys.stdout.flush()

list_1.sort()

for i in list_1:
    print "issue "+str(i[1])+" Phile "+str(i[2])



        

