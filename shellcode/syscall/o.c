#include <unistd.h>
#include <sys/syscall.h>

int main(){
	char ar[20] = "asdfasdf\n";
	syscall(SYS_write,1,ar,9);
	return 0;
}
