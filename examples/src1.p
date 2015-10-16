                       ; An example FRISC assembler code
                       
                       	ORG 0
00000000  00 10 80 07  	MOVE 1000, SP
00000004  20 00 00 B0  	LOAD R0, (20)
00000008  01 00 00 24  	ADD R0, 1, R0
0000000C  20 00 00 B8  	STORE R0, (20)
00000010  00 00 00 F8  	HALT
                       
                       	ORG 20
                       	; some sort of a data definition should go here
00000020  17 00 00 00  	DW 17
