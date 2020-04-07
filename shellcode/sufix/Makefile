all:
	yasm -felf64 sr.asm
	ld sr.o -o sr
	objdump -D -M intel sr
