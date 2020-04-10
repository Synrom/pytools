#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>

int main(){
	char ar[] = "Hallo";
	for(int i = 0;i < 5;i++)
		syscall(SYS_write,0,&ar[i],1);
	return 0;
}
