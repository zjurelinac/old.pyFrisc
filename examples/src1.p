                       ; An example FRISC assembler code
                       
                       	ORG 0
00000000  00 10 80 07  	MOVE 1000, SP
00000004  00 01 00 B0  	LOAD R0, (100)
00000008  01 00 00 24  	ADD R0, 1, R0
0000000C  00 01 00 B8  	STORE R0, (100)
00000010  00 00 00 F8  	HALT
                       
                       	ORG 100
                       	; some sort of a data definition should go here
