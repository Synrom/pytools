#! /usr/bin/python2.7

from sys import stdout
import datetime

start_num = 1950
year = datetime.datetime.now().year



def gen_pwds(since,words,depth=1):
    if len(words) == depth:
        for word in words:
            if word in since:
                continue
            yield since+word
            if word.upper() != word:
                yield since+word.upper()
            if word.lower() != word:
                yield since+word.lower()
    else:
        for word in words:
            if word in since:
                continue
            yield since+word
            if word.upper() != word:
                yield since+word.upper()
            if word.lower() != word:
                yield since+word.lower()
            for pwd in gen_pwds(since+word,words,depth + 1):
                yield pwd

def gen_dates():
    for m in range(1,13):
        if m <= 7 and m % 2 == 0:
            o = 30
        elif m <= 7:
            o = 31
        elif m % 2 == 0:
            o = 31
        else:
            o = 30
        for d in range(1,o+1):
            yield "%.2d%.2d" % (d,m)

def gen_num(pwd):
    global start_num
    global year
    for i in range(1,10):
        num1 = ""
        for n in range(0,i):
            num1 += str(n)
        yield pwd + num1
        yield num1 + pwd
        if i < 2:
            continue
        num2 = ""
        for n in range(1,i):
            num2 += str(n)
        yield num2 + pwd
        yield pwd + num2
    for num in range(start_num,year+1):
        yield pwd + str(num)
        yield pwd + str(num-(num/100 * 100))
        yield str(num) + pwd
        yield str(num-(num/100 * 100)) + pwd
    for date in gen_dates():
        yield pwd + date
        yield date + pwd

since_str = raw_input("set the start year(1950)>")
    
try:
    since = int(since_str,10)
except ValueError:
    pass

print "year from "+str(since)+" to "+str(year)

filename = raw_input("wordlist filename(wordlist)>")
if filename == "":
    filename = "wordlist"

print "write everything into "+filename

words = []

word = raw_input("info >")
while word != "":
    words.append(word)
    word = raw_input("info >")

with open(filename,"w") as f:
    for pwd in gen_pwds("",words):
        f.write(pwd+"\n")
        for pwd_num in gen_num(pwd):
            f.write(pwd_num+"\n")
