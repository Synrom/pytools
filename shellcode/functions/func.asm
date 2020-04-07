section .text

global _start

_start:
	call	t
	int	0x90
	int	0x90
	int	0x90
	int	0x90
	int	0x90
t:
	mov	rax,0x3c
	xor	rdi,rdi
	syscall
