all:
	yasm -felf64 pr.asm
	ld pr.o -o pr
	objdump -D -M intel pr
