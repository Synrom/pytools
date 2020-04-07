all:
	yasm -felf64 syscall.asm
	ld syscall.o -o syscall
	objdump -D -M intel syscall
