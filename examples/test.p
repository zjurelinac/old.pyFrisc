                       ; A very short code
                       	ORG 0
00000000  00 10 80 07  	MOVE 1000, SP
00000004  02 00 00 24  	ADD R0, 2, R0
00000008  02 00 00 24  	ADD R0, 2, R0
0000000C  02 00 00 24  	ADD R0, 2, R0
00000010  02 00 00 24  	ADD R0, 2, R0
00000014  00 00 00 F8  	HALT
                       
                       	ORG 24
00000024  01 00 00 24  	ADD R0, 1, R0
                       
                       	ORG 0FFF0
0000FFF0  02 00 00 00  	DW 2