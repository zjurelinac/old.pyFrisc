                       ;===========================================
                       ; 		external units memory locations  
                       ;===========================================
                       
                       ; GPIO SWITCH
                       ; working in interrupt mode
                       IOSW_CTRL		EQU	0FFFF0000
                       IOSW_DATA		EQU	0FFFF0004
                       ;IOSW_IACK		EQU	0FFFF0008
                       ;IOSW_IEND		EQU	0FFFF000C
                       
                       ; GPIO BUTTON
                       ; working in interrupt mode
                       IOBTN_CTRL		EQU	0FFFFE000
                       IOBTN_DATA		EQU	0FFFFE004
                       ;IOBTN_IACK		EQU	0FFFFE008
                       ;IOBTN_IEND		EQU	0FFFFE00C
                       
                       ; RTC1
                       ; ignored in main program, only used for linking to the R
                       RTC1_DATA		EQU	0FFFF0100
                       RTC1_CTRL		EQU	0FFFF0104
                       
                       ; RTC2
                       ; used in interrupt mode for timing hundredths of a secon
                       RTC2_DATA		EQU	0FFFF0200
                       RTC2_CTRL		EQU	0FFFF0204
                       RTC2_IACK		EQU	0FFFF0208
                       RTC2_IEND		EQU	0FFFF020C
                       
                       ; GPIO LED
                       ; setting bits mode
                       IOLED_CTRL		EQU	0FFFFD000
                       IOLED_DATA		EQU	0FFFFD004
                       
                       ; LCD
                       LCD_DATA		EQU	0FFFFF000
                       LCD_CTRL		EQU	0FFFFF004
                       LCD_STAT		EQU	0FFFFF008
                       
                       ;===========================================
                       ;			Start of the program
                       ;===========================================
                       		ORG 	0
00000000  00 10 80 07  		MOVE 	1000, SP
00000004  0C 00 00 C4  		JP 		MAIN
00000008  00 02 00 00  		DW 		200
                       		
                       
                       ;===========================================
                       ;		Initialization of external units
                       ;===========================================
0000000C  9C 05 00 B0  MAIN	LOAD 	R0, (BTN_CTRL)
00000010  00 E0 0F B8  		STORE 	R0, (IOBTN_CTRL)
                       		
00000014  02 00 00 04  		MOVE	2, R0
00000018  00 D0 0F B8  		STORE 	R0, (IOLED_CTRL)
                       		
0000001C  01 00 00 04  		MOVE 	1, R0
00000020  04 D0 0F B8  		STORE 	R0, (IOLED_DATA)
                       		
00000024  04 E0 0F B0  WAITS 	LOAD 	R0, (IOBTN_DATA)
00000028  04 00 00 14  		AND 	R0, 4, R0
0000002C  24 00 C0 C5  		JP_Z 	WAITS		
                       
00000030  A0 05 00 B0  RSETUP 	LOAD 	R0, (SW_CTRL)
00000034  00 00 0F B8  		STORE 	R0, (IOSW_CTRL)
                       		
00000038  64 00 00 04  		MOVE 	%D 100, R0
0000003C  00 01 0F B8  		STORE 	R0, (RTC1_DATA)
                       		
00000040  A3 02 00 04  		MOVE 	%D 675, R0
00000044  00 02 0F B8  		STORE 	R0, (RTC2_DATA)
                       		
00000048  10 00 10 04  		MOVE 	10, SR
                       		
0000004C  03 00 00 04  		MOVE 	3, R0 			; 	later attempt nonmasking
00000050  04 02 0F B8  		STORE 	R0, (RTC2_CTRL)
                       		
00000054  01 00 00 04  		MOVE  	1, R0
00000058  04 01 0F B8  		STORE 	R0, (RTC1_CTRL)
                       
                       
                       
0000005C  04 00 0F B3  WAITE 	LOAD 	R6, (IOSW_DATA)
                       
00000060  B8 05 80 B0  		LOAD 	R1, (STATUS)
00000064  00 00 02 01  		MOVE 	R1, R2
                       		
00000068  00 00 80 05  		MOVE 	0, R3
                       		
0000006C  00 00 00 06  LOOP		MOVE 	0, R4
00000070  00 00 80 06  			MOVE 	0, R5
00000074  01 00 60 5F  			SHR		R6, 1, R6
00000078  00 00 40 2E  			ADC		R4, 0, R4			; 	R4 is the current bit of SWITCH
0000007C  01 00 20 5D  			SHR		R2, 1, R2
00000080  00 00 D0 2E  			ADC		R5, 0, R5 			; 	R5 is the current bit of STATUS
                       			
00000084  00 00 4A 68  			CMP		R4, R5 				; 	if SWITCH 1 and STATUS 0, new swimm
00000088  D8 00 40 C6  			JP_ULE 	SKIP 				;	else skip
                       
0000008C  01 00 00 04  			MOVE 	1, R0
00000090  00 00 06 50  			SHL 	R0, R3, R0
00000094  00 00 82 08  			OR 		R0, R1, R1
00000098  B8 05 80 B8  			STORE 	R1, (STATUS)
0000009C  04 D0 8F B8  			STORE 	R1, (IOLED_DATA)
                       
000000A0  00 00 80 88  			PUSH  	R1
000000A4  00 00 00 89  			PUSH 	R2
000000A8  00 00 80 89  			PUSH 	R3
000000AC  00 00 00 8A  			PUSH 	R4
000000B0  00 00 06 00  			MOVE 	R3, R0
000000B4  BC 02 00 CC  			CALL 	STRDATA
000000B8  30 05 00 CC  			CALL 	PASSDISP
000000BC  00 00 00 82  			POP 	R4
000000C0  00 00 80 81  			POP		R3
000000C4  00 00 00 81  			POP		R2
000000C8  00 00 80 80  			POP 	R1 
                       
000000CC  BC 05 00 B0  			LOAD 	R0, (NUM_FIN)
000000D0  01 00 00 24  			ADD 	R0, 1, R0
000000D4  BC 05 00 B8  			STORE 	R0, (NUM_FIN)
                       SKIP	
000000D8  01 00 B0 25  			ADD 	R3, 1, R3
000000DC  08 00 30 6C  			CMP 	R3, 8
000000E0  6C 00 00 C6  			JP_NZ 	LOOP		
                       
000000E4  04 07 00 B0  		LOAD 	R0, (TIMELOCK)
000000E8  01 00 00 6C  		CMP 	R0, 1
000000EC  FC 00 00 C6  		JP_NZ 	NEXT
                       
000000F0  28 03 00 CC  		CALL 	TIMEDISP
000000F4  00 00 00 04  		MOVE 	0, R0
000000F8  04 07 00 B8  		STORE 	R0, (TIMELOCK)
                       
000000FC  FF 00 10 6C  NEXT	CMP 	R1, 0FF
00000100  5C 00 00 C6  		JP_NE 	WAITE
                       
00000104  00 00 10 04  RESULTS	MOVE 	0, SR
00000108  00 00 00 04  		MOVE 	0, R0
0000010C  04 02 0F B8  		STORE 	R0, (RTC2_CTRL)
                       
00000110  8C 03 00 CC  		CALL 	RESDISP
00000114  00 00 00 F8  		HALT
                       
                       ;===========================================
                       ;  Masking interrupt processing - RTC2 only
                       ;===========================================
                       		ORG 	200
                       MIPROC
00000200  00 00 00 88  		PUSH 	R0
00000204  00 00 80 88  		PUSH 	R1
00000208  00 00 00 89  		PUSH 	R2
0000020C  00 00 80 89  		PUSH 	R3
00000210  00 00 20 00  		MOVE 	SR, R0
00000214  00 00 00 88  		PUSH 	R0
                       		
00000218  08 02 0F B8  		STORE 	R0, (RTC2_IACK)
                       		
0000021C  A4 05 00 B0  		LOAD 	R0, (TIME_H0)
00000220  01 00 00 24  		ADD 	R0, 1, R0
00000224  0A 00 00 6C  		CMP 	R0, 0A
00000228  78 02 00 C6  		JP_NE 	STRH0
                       		
0000022C  00 00 00 04  		MOVE 	0, R0
00000230  A8 05 80 B0  		LOAD 	R1, (TIME_H1)
00000234  01 00 90 24  		ADD 	R1, 1, R1
00000238  0A 00 10 6C  		CMP 	R1, 0A
0000023C  74 02 00 C6  		JP_NE 	STRH1
                       		
00000240  00 00 80 04  		MOVE 	0, R1
00000244  AC 05 00 B1  		LOAD 	R2, (TIME_S0)
00000248  01 00 20 25  		ADD 	R2, 1, R2
0000024C  0A 00 20 6C  		CMP 	R2, 0A
00000250  70 02 00 C6  		JP_NE 	STRS0
                       		
00000254  00 00 00 05  		MOVE 	0, R2
00000258  B0 05 80 B1  		LOAD 	R3, (TIME_S1)
0000025C  01 00 B0 25  		ADD		R3, 1, R3
00000260  0A 00 30 6C  		CMP 	R3, 0A
00000264  6C 02 00 C6  		JP_NE 	STRS1
                       		
00000268  00 00 80 05  		MOVE 	0, R3
                       
0000026C  B0 05 80 B9  STRS1 	STORE 	R3, (TIME_S1)
00000270  AC 05 00 B9  STRS0 	STORE 	R2, (TIME_S0)
00000274  A8 05 80 B8  STRH1 	STORE 	R1, (TIME_H1)
00000278  A4 05 00 B8  STRH0	STORE 	R0, (TIME_H0)
                       		
0000027C  01 00 00 04  		MOVE 	1, R0
00000280  04 07 00 B8  		STORE 	R0, (TIMELOCK)
                       
00000284  B4 05 00 B0  		LOAD 	R0, (TIME_TOT)
00000288  01 00 00 24  		ADD 	R0, 1, R0
0000028C  B4 05 00 B8  		STORE 	R0, (TIME_TOT)
                       
00000290  BC 05 80 B0  		LOAD 	R1, (NUM_FIN)
00000294  00 00 10 6C  		CMP 	R1, 0
00000298  9C 02 C0 C5  		JP_Z 	NOLED
                       		
0000029C  0C 02 0F B8  NOLED 	STORE 	R0, (RTC2_IEND)
                       	
000002A0  00 00 00 80  		POP 	R0
000002A4  00 00 10 00  		MOVE 	R0, SR
000002A8  00 00 80 81  		POP		R3
000002AC  00 00 00 81  		POP 	R2
000002B0  00 00 80 80  		POP 	R1
000002B4  00 00 00 80  		POP 	R0
000002B8  01 00 00 D8  		RETI
                       		
                       ;===========================================
                       ; 			Store contestant data
                       ;===========================================
                       STRDATA 	; 	lane num in R0
000002BC  00 00 80 8A  		PUSH 	R5
000002C0  00 00 00 8B  		PUSH 	R6
                       
000002C4  B0 05 80 B0  		LOAD 	R1, (TIME_S1)
000002C8  AC 05 00 B1  		LOAD 	R2, (TIME_S0)
000002CC  A8 05 80 B1  		LOAD 	R3, (TIME_H1)
000002D0  A4 05 00 B2  		LOAD 	R4, (TIME_H0)
                       
000002D4  BC 05 80 B2  		LOAD 	R5, (NUM_FIN)
000002D8  03 00 50 6C  		CMP 	R5, 3
000002DC  04 03 C0 C5  		JP_EQ 	ENDSTR
                       		
000002E0  02 00 D0 56  		SHL 	R5, 2, R5
000002E4  F0 05 50 BC  		STORE 	R0, (R5+CLANE) 
                       
000002E8  02 00 D0 56  		SHL 	R5, 2, R5
000002EC  C0 05 00 07  		MOVE 	CTIME, R6
000002F0  00 00 DC 22  		ADD 	R5, R6, R5
                       
000002F4  00 00 D0 BC  		STORE 	R1, (R5)
000002F8  04 00 50 BD  		STORE 	R2, (R5+4)
000002FC  08 00 D0 BD  		STORE 	R3, (R5+8)
00000300  0C 00 50 BE  		STORE 	R4, (R5+0C)
                       		
00000304  00 00 00 83  ENDSTR	POP 	R6
00000308  00 00 80 82  		POP 	R5
0000030C  00 00 00 D8  		RET
                       
                       ;===========================================
                       ; 			LCD wait procedure
                       ;===========================================
                       LCDWAIT	
00000310  00 00 00 88  		PUSH 	R0
00000314  08 F0 0F B0  WAITL 	LOAD 	R0, (LCD_STAT)
00000318  00 00 00 6C  		CMP 	R0, 0
0000031C  14 03 C0 C5  		JP_Z 	WAITL		
00000320  00 00 00 80  		POP 	R0
00000324  00 00 00 D8  		RET
                       
                       ;===========================================
                       ; 			LCD write only time
                       ;===========================================
                       TIMEDISP
00000328  00 00 00 88  		PUSH 	R0
                       		
0000032C  00 80 00 04  		MOVE 	%B 1000000000000000, R0
00000330  10 03 00 CC  		CALL 	LCDWAIT
00000334  04 F0 0F B8  		STORE 	R0, (LCD_CTRL)
                       		
00000338  B0 05 00 B0  		LOAD 	R0, (TIME_S1)
0000033C  30 00 00 24  		ADD 	R0, 30, R0
00000340  10 03 00 CC  		CALL 	LCDWAIT
00000344  00 F0 0F 98  		STOREB 	R0, (LCD_DATA)
                       		
00000348  AC 05 00 B0  		LOAD 	R0, (TIME_S0)
0000034C  30 00 00 24  		ADD 	R0, 30, R0
00000350  10 03 00 CC  		CALL 	LCDWAIT
00000354  00 F0 0F 98  		STOREB	R0, (LCD_DATA)
                       		
00000358  FC 06 00 B0  		LOAD 	R0, (ASCII_COL)
0000035C  10 03 00 CC  		CALL 	LCDWAIT
00000360  00 F0 0F 98  		STOREB 	R0, (LCD_DATA)
                       		
00000364  A8 05 00 B0  		LOAD 	R0, (TIME_H1)
00000368  30 00 00 24  		ADD 	R0, 30, R0
0000036C  10 03 00 CC  		CALL 	LCDWAIT
00000370  00 F0 0F 98  		STOREB 	R0, (LCD_DATA)
                       		
00000374  A4 05 00 B0  		LOAD 	R0, (TIME_H0)
00000378  30 00 00 24  		ADD 	R0, 30, R0
0000037C  10 03 00 CC  		CALL 	LCDWAIT
00000380  00 F0 0F 98  		STOREB 	R0, (LCD_DATA)
                       		
00000384  00 00 00 80  		POP 	R0
00000388  00 00 00 D8  		RET
                       
                       ;===========================================
                       ; 			LCD display the results
                       ;===========================================
                       RESDISP
0000038C  00 00 00 88  		PUSH 	R0
00000390  00 00 80 88  		PUSH 	R1
00000394  00 00 00 89  		PUSH 	R2
00000398  00 00 80 89  		PUSH 	R3
                       		
0000039C  02 80 00 04  		MOVE 	%B 1000000000000010, R0
000003A0  10 03 00 CC  		CALL 	LCDWAIT
000003A4  04 F0 0F B8  		STORE 	R0, (LCD_CTRL)
                       
000003A8  F0 05 80 B0  		LOAD 	R1, (CLANE0)
000003AC  10 03 00 CC  		CALL 	LCDWAIT
000003B0  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
000003B4  00 80 00 04  		MOVE 	%B 1000000000000000, R0
000003B8  10 03 00 CC  		CALL 	LCDWAIT
000003BC  04 F0 0F B8  		STORE 	R0, (LCD_CTRL)
                       
000003C0  F0 05 80 B0  		LOAD 	R1, (CLANE0)
000003C4  31 00 90 24  		ADD 	R1, 31, R1
000003C8  10 03 00 CC  		CALL 	LCDWAIT
000003CC  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
000003D0  00 07 80 B0  		LOAD 	R1, (ASCII_SP)
000003D4  10 03 00 CC  		CALL 	LCDWAIT
000003D8  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
000003DC  C0 05 00 05  		MOVE 	CTIME0, R2
000003E0  00 00 A0 B4  		LOAD 	R1, (R2)
000003E4  30 00 90 24  		ADD 	R1, 30, R1
000003E8  10 03 00 CC  		CALL 	LCDWAIT
000003EC  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
000003F0  04 00 A0 B4  		LOAD 	R1, (R2+4)
000003F4  30 00 90 24  		ADD 	R1, 30, R1
000003F8  10 03 00 CC  		CALL 	LCDWAIT
000003FC  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
00000400  FC 06 80 B0  		LOAD 	R1, (ASCII_COL)
00000404  10 03 00 CC  		CALL 	LCDWAIT
00000408  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
0000040C  08 00 A0 B4  		LOAD 	R1, (R2+8)
00000410  30 00 90 24  		ADD 	R1, 30, R1
00000414  10 03 00 CC  		CALL 	LCDWAIT
00000418  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
0000041C  0C 00 A0 B4  		LOAD 	R1, (R2+0C)
00000420  30 00 90 24  		ADD 	R1, 30, R1
00000424  10 03 00 CC  		CALL 	LCDWAIT
00000428  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
                       		
                       ; 	SECOND SWIMMER
0000042C  00 C0 00 04  		MOVE 	0C000, R0
00000430  10 03 00 CC  		CALL 	LCDWAIT
00000434  04 F0 0F B8  		STORE 	R0, (LCD_CTRL)
                       
00000438  D0 05 00 05  		MOVE 	CTIME1, R2
                       
0000043C  F4 05 80 B0  		LOAD 	R1, (CLANE1)
00000440  31 00 90 24  		ADD 	R1, 31, R1
00000444  10 03 00 CC  		CALL 	LCDWAIT
                       
00000448  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
0000044C  00 07 80 B0  		LOAD 	R1, (ASCII_SP)
00000450  10 03 00 CC  		CALL 	LCDWAIT
00000454  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
00000458  00 00 A0 B4  		LOAD 	R1, (R2)
0000045C  10 03 00 CC  		CALL 	LCDWAIT
00000460  30 00 90 24  		ADD 	R1, 30, R1
00000464  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
00000468  04 00 A0 B4  		LOAD 	R1, (R2+4)
0000046C  30 00 90 24  		ADD 	R1, 30, R1
00000470  10 03 00 CC  		CALL 	LCDWAIT
00000474  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
00000478  FC 06 80 B0  		LOAD 	R1, (ASCII_COL)
0000047C  10 03 00 CC  		CALL 	LCDWAIT
00000480  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
00000484  08 00 A0 B4  		LOAD 	R1, (R2+8)
00000488  30 00 90 24  		ADD 	R1, 30, R1
0000048C  10 03 00 CC  		CALL 	LCDWAIT
00000490  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
00000494  0C 00 A0 B4  		LOAD 	R1, (R2+0C)
00000498  30 00 90 24  		ADD 	R1, 30, R1
0000049C  10 03 00 CC  		CALL 	LCDWAIT
000004A0  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
                       ; THIRD SWIMMER
                       
000004A4  00 C8 00 04  		MOVE 	0C800, R0
000004A8  10 03 00 CC  		CALL 	LCDWAIT
000004AC  04 F0 0F B8  		STORE 	R0, (LCD_CTRL)
                       
000004B0  E0 05 00 05  		MOVE 	CTIME2, R2
000004B4  F8 05 80 B0  		LOAD 	R1, (CLANE2)
000004B8  31 00 90 24  		ADD 	R1, 31, R1
000004BC  10 03 00 CC  		CALL 	LCDWAIT
000004C0  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
000004C4  00 07 80 B0  		LOAD 	R1, (ASCII_SP)
000004C8  10 03 00 CC  		CALL 	LCDWAIT
000004CC  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
000004D0  00 00 A0 B4  		LOAD 	R1, (R2)
000004D4  30 00 90 24  		ADD 	R1, 30, R1
000004D8  10 03 00 CC  		CALL 	LCDWAIT
000004DC  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
000004E0  04 00 A0 B4  		LOAD 	R1, (R2+4)
000004E4  30 00 90 24  		ADD 	R1, 30, R1
000004E8  10 03 00 CC  		CALL 	LCDWAIT
000004EC  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
000004F0  FC 06 80 B0  		LOAD 	R1, (ASCII_COL)
000004F4  10 03 00 CC  		CALL 	LCDWAIT
000004F8  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
000004FC  08 00 A0 B4  		LOAD 	R1, (R2+8)
00000500  30 00 90 24  		ADD 	R1, 30, R1
00000504  10 03 00 CC  		CALL 	LCDWAIT
00000508  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
0000050C  0C 00 A0 B4  		LOAD 	R1, (R2+0C)
00000510  30 00 90 24  		ADD 	R1, 30, R1
00000514  10 03 00 CC  		CALL 	LCDWAIT
00000518  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
                       
0000051C  00 00 80 81  		POP 	R3
00000520  00 00 00 81  		POP 	R2
00000524  00 00 80 80  		POP 	R1
00000528  00 00 00 80  		POP		R0
0000052C  00 00 00 D8  		RET
                       		
                       ;===========================================
                       ; 			LCD display the pass
                       ;===========================================
                       PASSDISP 	; 	R1-R4 time, R0 lane
00000530  00 00 80 8A  		PUSH 	R5
                       
00000534  00 C0 80 06  		MOVE 	0C000, R5
00000538  10 03 00 CC  		CALL 	LCDWAIT
0000053C  04 F0 8F BA  		STORE 	R5, (LCD_CTRL)
                       
00000540  31 00 00 24  		ADD 	R0, 31, R0
00000544  10 03 00 CC  		CALL 	LCDWAIT
00000548  00 F0 0F 98  		STOREB 	R0, (LCD_DATA)
                       
0000054C  00 07 80 B2  		LOAD 	R5, (ASCII_SP)
00000550  10 03 00 CC  		CALL 	LCDWAIT
00000554  00 F0 8F 9A  		STOREB 	R5, (LCD_DATA)
                       
00000558  FC 06 80 B2  		LOAD 	R5, (ASCII_COL)
                       
0000055C  30 00 90 24  		ADD 	R1, 30, R1
00000560  30 00 20 25  		ADD 	R2, 30, R2
00000564  30 00 B0 25  		ADD 	R3, 30, R3
00000568  30 00 40 26  		ADD 	R4, 30, R4
                       
0000056C  10 03 00 CC  		CALL 	LCDWAIT
00000570  00 F0 8F 98  		STOREB 	R1, (LCD_DATA)
00000574  10 03 00 CC  		CALL 	LCDWAIT
00000578  00 F0 0F 99  		STOREB 	R2, (LCD_DATA)
0000057C  10 03 00 CC  		CALL 	LCDWAIT
00000580  00 F0 8F 9A  		STOREB 	R5, (LCD_DATA)
00000584  10 03 00 CC  		CALL 	LCDWAIT
00000588  00 F0 8F 99  		STOREB 	R3, (LCD_DATA)
0000058C  10 03 00 CC  		CALL 	LCDWAIT
00000590  00 F0 0F 9A  		STOREB 	R4, (LCD_DATA)
                       
00000594  00 00 80 82  		POP 	R5
00000598  00 00 00 D8  		RET
                       
                       ;===========================================
                       ; 			Variable storage space
                       ;===========================================
                       
0000059C  03 00 00 00  BTN_CTRL 	DW 	3
000005A0  03 00 00 00  SW_CTRL		DW 	3
                       
000005A4  00 00 00 00  TIME_H0 	DW 	0
000005A8  00 00 00 00  TIME_H1 	DW 	0
000005AC  00 00 00 00  TIME_S0 	DW 	0
000005B0  00 00 00 00  TIME_S1 	DW 	0
000005B4  00 00 00 00  TIME_TOT 	DW 	0
                       
000005B8  00 00 00 00  STATUS 		DW 	0
000005BC  00 00 00 00  NUM_FIN 	DW 	0
                       
                       CTIME
000005C0  00 00 00 00  CTIME0 		DW 	0, 0, 0, 0
          00 00 00 00
          00 00 00 00
          00 00 00 00
000005D0  00 00 00 00  CTIME1 		DW 	0, 0, 0, 0
          00 00 00 00
          00 00 00 00
          00 00 00 00
000005E0  00 00 00 00  CTIME2		DW 	0, 0, 0, 0
          00 00 00 00
          00 00 00 00
          00 00 00 00
                       
                       CLANE
000005F0  00 00 00 00  CLANE0 		DW 	0
000005F4  00 00 00 00  CLANE1 		DW 	0
000005F8  00 00 00 00  CLANE2 		DW 	0
                       
                       TAMPONZONE  DS 	100
                       
000006FC  3A 00 00 00  ASCII_COL 	DW 	3A
00000700  20 00 00 00  ASCII_SP 	DW 	20
                       
00000704  00 00 00 00  TIMELOCK 	DW 	0
