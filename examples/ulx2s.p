                       ;
                       ;
                       ;   ____                _
                       ;  |  _ \ ___  __ _  __| |_ __ ___   ___
                       ;  | |_) / _ \/ _  |/ _  |  _   _ \ / _ \
                       ;  |  _ |  __/ (_| | (_| | | | | | |  __/
                       ;  |_| \_\___|\__,_|\__,_|_| |_| |_|\___| - seriously, re
                       ;
                       ; Version 0.9:
                       ; This project is still in development,
                       ; please report any encountered bugs or ideas to FER mail
                       ;
                       ; - all changes of code will be remembered even after clo
                       ;   to reset to this demonstration simply delete all cont
                       ; - some useful editor shortcuts:
                       ;
                       ;    * Ctrl + Enter             - assemble code
                       ;    * Ctrl + K (or Ctrl + \)   - toggle comments on sele
                       ;    * Tab                      - indent selected (curren
                       ;    * Shift + Tab              - unindent selected (curr
                       ;
                       ; - you can find sample code along with comments on speci
                       ;   ULX2S boards below, for information on how to transfe
                       ;   code please click links on the bottom right
                       ;
                       
                       
                       
                       ; SP initialization is not required for ULX2S since boot-
                       ; set it to correct location.
                       		ORG 0
00000000  00 10 80 07          MOVE 1000, SP
00000004  00 01 00 C4          JP MAIN
                       
                       
                       
                       ; This sample program will fill first 16 (dec.) locations
                       ; displayed on LCD on E2LP board (or printed to the termi
                       ; numbers from 0 to F.
                       
                       		ORG 100
00000100  00 00 00 04  MAIN    MOVE 0, R0
00000104  2C 02 80 04  		MOVE LCDDATA, R1
00000108  10 00 00 6C  LOOP    CMP R0, 10
0000010C  20 01 C0 C5  		JP_EQ ENDMAIN
00000110  00 00 10 BC  		STORE R0, (R1)
00000114  01 00 00 24  		ADD R0, 1, R0
00000118  04 00 90 24  		ADD R1, 4, R1
0000011C  08 01 00 C4  		JP LOOP
                       
00000120  94 01 00 CC  ENDMAIN CALL PRINTDATA		; PRINTDATA_ULX for ULX2S
00000124  00 00 00 F8  		HALT
                       
                       
                       
                       ; Print data to RS232 on ULX2S
                       ; It will output data from first PRINTCOUNT positions sta
                       ; to the connected terminal. It can be called multiple ti
                       ; print current values at LCDDATA.
                       ;
                       ; Based on examples on http://www.nxlab.fer.hr/dl/frisc.h
                       PUTCHAR         EQU 3FE4
                       PUTHEX_W        EQU 3FEC
                       PRINTCOUNT      EQU 10; How many locations to print start
                       
00000128  00 00 00 88  PRINTDATA_ULX   PUSH R0
0000012C  00 00 00 8A  				PUSH R4
00000130  00 00 80 8A  				PUSH R5
00000134  00 00 00 8B  				PUSH R6
00000138  00 00 80 06  				MOVE 0, R5
0000013C  2C 02 00 07  				MOVE LCDDATA, R6
                       
00000140  10 00 50 6C  PRINTLOOP_ULX   CMP R5, PRINTCOUNT
00000144  70 01 C0 C5  				JP_EQ ENDPRINTDATA
00000148  00 00 60 B6  				LOAD R4, (R6)
0000014C  00 00 08 00  				MOVE R4, R0; print word at current position
00000150  EC 3F 00 CC  				CALL PUTHEX_W
00000154  0D 00 00 04  				MOVE 0D, R0
00000158  E4 3F 00 CC  				CALL PUTCHAR; print CR
0000015C  0A 00 00 04  				MOVE 0A, R0
00000160  E4 3F 00 CC  				CALL PUTCHAR; print LF
00000164  01 00 D0 26  				ADD R5, 1, R5
00000168  04 00 60 27  				ADD R6, 4, R6
0000016C  40 01 00 C4  				JP PRINTLOOP_ULX
                       
00000170  0D 00 00 04  ENDPRINTDATA    MOVE 0D, R0; Print blank line at the end.
00000174  E4 3F 00 CC  				CALL PUTCHAR; print CR
00000178  0A 00 00 04  				MOVE 0A, R0
0000017C  E4 3F 00 CC  				CALL PUTCHAR; print LF
00000180  00 00 00 83  						POP R6
00000184  00 00 80 82  				POP R5
00000188  00 00 00 82  				POP R4
0000018C  00 00 00 80  				POP R0
00000190  00 00 00 D8  				RET
                       
                       
                       
                       ; Print data to LCD on E2LP
                       ; There will be displayed 4 memory locations, first on to
                       ; right. You can set offset (in increments by 4) by chang
                       ; down to up position. It can't be called multiple times 
                       ; loop print registers at given offset and update offset 
                       ;
                       ; Copyright FER 2015, print_loop_v3.txt
                       ; http://www.fer.unizg.hr/_download/repository/arh_e2lp.z
00000194  03 00 00 04  PRINTDATA       MOVE %B 011, R0
00000198  00 00 0F B8  				STORE R0, (%H FFFF0000) ; set GPIO for SW - input mod
0000019C  04 00 0F B0  				LOAD R0, (%H FFFF0004) ; read status of SW
000001A0  04 00 00 54  				SHL R0, 4, R0
000001A4  2C 02 80 04  				MOVE LCDDATA, R1
000001A8  00 00 02 21  				ADD R0, R1, R2
000001AC  04 00 80 05  				MOVE 4, R3
000001B0  C8 01 00 CC  PRINTLOOP       CALL LCDWRITE
000001B4  04 00 20 25  				ADD R2, 4, R2
000001B8  01 00 B0 35  				SUB R3, 1, R3
000001BC  00 00 30 6C  				CMP R3, 0
000001C0  B0 01 00 C6  				JP_NE PRINTLOOP
000001C4  94 01 00 C4  				JP PRINTDATA
                       
000001C8  08 F0 0F B0  LCDWRITE        LOAD R0, (%H FFFFF008)
000001CC  00 00 00 6C  				CMP R0, 0
000001D0  F4 FF CF D5  				JR_EQ LCDWRITE
000001D4  01 00 00 04  				MOVE 1, R0
000001D8  04 F0 0F 98  				STOREB R0, (%H FFFFF004)
000001DC  28 02 00 B0  				LOAD R0, (LCDCURS)
000001E0  01 00 00 24  				ADD R0, 1, R0
000001E4  28 02 00 B8  				STORE R0, (LCDCURS)
000001E8  03 00 00 6C  				CMP R0, 3
000001EC  10 02 C0 C5  				JP_EQ ROW2
000001F0  06 00 00 6C  				CMP R0, 6
000001F4  FC 01 C0 C5  				JP_EQ ROW1
000001F8  1C 02 00 C4  				JP NOMOVE
000001FC  80 00 00 04  ROW1            MOVE %B 10000000, R0
00000200  05 F0 0F 98  				STOREB R0, (%H FFFFF005)
00000204  00 00 00 04  				MOVE 0, R0
00000208  28 02 00 B8  				STORE R0, (LCDCURS)
0000020C  B8 FF 0F D4  				JR LCDWRITE
00000210  C0 00 00 04  ROW2            MOVE %B 11000000, R0
00000214  05 F0 0F 98  				STOREB R0, (%H FFFFF005)
00000218  AC FF 0F D4  				JR LCDWRITE
0000021C  00 00 20 B4  NOMOVE          LOAD R0, (R2)
00000220  00 F0 0F B8  				STORE R0, (%H FFFFF000)
00000224  00 00 00 D8  				RET
                       
00000228  00 00 00 00  LCDCURS   		DW %H 00000000
                       LCDDATA   		DS %D 1024
                       	
