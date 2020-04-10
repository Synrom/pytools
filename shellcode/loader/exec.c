#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>



int main(int argc,char **argv){
	int len = atoi(argv[1]);
	printf("length = %d\n",len);
	int fd = open("shellcode.bin",O_RDONLY);
	if(fd == -1){
		printf("coudlnt open shellcode.bin\n");
		return -1;
	}
	char *addr = mmap(NULL,len,PROT_EXEC,MAP_PRIVATE,fd,0);
	if (addr == MAP_FAILED){
		printf("failed while mapping...\n");
		return -1;
	}
	(( void (*) ()) addr)();
	return 0;
}
