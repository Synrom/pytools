section .text

global _start

_start:
	mov	rax,rdi
	mov	rdi,rsi
	mov	rsi,rdx
	mov	rdx,rcx
	mov	r10,r8
	mov	r8,r9
	mov	r9,QWORD[rsp+0x8]
	syscall
	
