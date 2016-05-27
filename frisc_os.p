                       ;###############################################################################
                       ;#	FRISC OS v0.1
                       ;#	--------------------------------------------------------------------------	
                       ;#	Author:			Zvonimir Jurelinac
                       ;#	Description:	A basic bootloader and operating system for FRISC
                       ;#					processing system implemented on Zynq ZedBoard.
                       ;# 					 
                       ;#	TODO: 			¤ Allow callback priorities
                       ;#					¤ Rethink callbacks, perhaps useless
                       ;#					¤ RESET handler
                       ;# 					¤ UART handlers
                       ;#
                       ;#	Code sections:
                       ;#	--------------------------------------------------------------------------
                       ;#	1. CONSTANTS DEFINITION
                       ;#	2. DEFAULT START SEQUENCE
                       ;#	3. NON-MASKING INTERRUPT HANDLER
                       ;#	4. MASKING INTERRUPT HANDLER
                       ;#	5. OPERATING SYSTEM MAIN FUNCTION
                       ;#	6. SYSTEM CALLS DEFINITION
                       ;#	7. AUXILLIARY FUNCTIONS
                       ;#	8. OS MEMORY SPACE
                       ;###############################################################################
                       
                       ;===============================================================================
                       ; 	1. CONSTANTS DEFINITION
                       ;===============================================================================
                       
                       ;----- IMPORTANT OS MEMORY LOCATIONS -------------------------------------------
                       ; NMI_CB_DEF_CNT_ADDR 		Address of NMI callback def. counter - how many callbacks already defined
                       ; NMI_CB_DEF_START_ADDR 	Starting address for NMI callback definitions
                       ; INT_CB_DEF_CNT_ADDR 		Address of INT callback def. counter - how many callbacks already defined
                       ; INT_CB_DEF_START_ADDR 	Starting address for INT callback definitions
                       
                       ;----- VARIOUS DEFINITIONS -----------------------------------------------------
                       IO_CB_DEF_SIZE 			EQU 16 		; 	Single IO callback definition size
                       									; 	IO callback definition contains:
                       									; 		IO_UNIT_SR_ADDR - IO unit's status register address
                       									; 		IO_UNIT_SR_MASK - Status register interrupt AND mask
                       									; 		IO_UNIT_CB_ADDR - Starting address of callback procedure
                       IO_CB_DEF_SIZE_LG 		EQU 4 		; 	Log2(IO_CB_DEF_SIZE)
                       
                       ;# ----- IO UNITS LOCATIONS ------------------------------------------------------
                       ;# Internal FRISC units are located on addresses from FFFF0000 to FFFFFFFF
                       ;# AXI-connected units are located on addressess from FFF00000 to FFFF0000
                       
                       ; LogiCORE IP AXI UART LITE
                       IO_UART_READ_REG 		EQU 0FFF00000
                       IO_UART_WRITE_REG 		EQU 0FFF00004
                       IO_UART_STAT_REG 		EQU 0FFF00008
                       IO_UART_CTRL_REG 		EQU 0FFF0000C
                       
                       IO_LEDS_WRITE_REG 		EQU 0FFF01000
                       ; IO_SW_READ_REG 		EQU 0FFF02000
                       
                       ;===============================================================================
                       ; 	2. DEFAULT START SEQUENCE
                       ;===============================================================================
                       				ORG 0
00000000  00 40 80 07  _OS_START		MOVE 4000, SP
00000004  84 00 00 C4  				JP _OS_INIT
                       
                       				ORG 8
00000008  00 01 00 00  				DW 100
                       
                       
                       ;===============================================================================
                       ; 	3. NON-MASKING INTERRUPT HANDLER
                       ;===============================================================================
                       				
                       _NMI_HANDLER	ORG 0C
0000000C  03 00 00 D8  				RETN
                       
                       
                       ;===============================================================================
                       ; 	4. MASKING INTERRUPT HANDLER
                       ;===============================================================================
                       
                       _INT_HANDLER 	ORG 10
                       ;############################################################################### 	
                       ;# 	Masking interrupts handler - detects which unit caused the interrupt and 
                       ;# 	calls the corresponding callback
                       ;# 	 ::  	Nothing
                       ;# 	 =>  	Nothing
                       ;# 			
                       ;#			R0 - IO_UNIT_SR_ADDR, IO_UNIT_SR_VALUE
                       ;# 			R1 - IO_UNIT_SR_MASK
                       ;# 			R2 - IO_UNIT_CB_ADDR
                       ;# 			R3 - IO CB address pointer
                       ;# 			R4 - Callbacks counter
                       ;###############################################################################
00000010  00 00 00 88  				PUSH R0
00000014  00 00 20 00  				MOVE SR, R0
00000018  00 00 00 88  				PUSH R0
0000001C  00 00 80 88  				PUSH R1
00000020  00 00 00 89  				PUSH R2
00000024  00 00 80 89  				PUSH R3
00000028  00 00 00 8A  				PUSH R4
                       				
0000002C  1C 02 80 05  _START_1		MOVE INT_CB_DEF_START_ADDR, R3
00000030  18 02 00 B2  				LOAD R4, (INT_CB_DEF_CNT_ADDR)
00000034  00 00 40 6C  				CMP R4, 0
00000038  64 00 C0 C5  				JP_Z _ENDLOOP_1
                       
0000003C  00 00 30 B4  _LOOP_1			LOAD R0, (R3)
00000040  04 00 B0 B4  				LOAD R1, (R3+4)
00000044  08 00 30 B5  				LOAD R2, (R3+8)
                       
00000048  00 00 00 B4  				LOAD R0, (R0)
0000004C  00 00 02 10  				AND R0, R1, R0
00000050  58 00 C0 C5  				JP_Z _LOOP_1_CONT 	; IO unit inactive
00000054  00 00 04 C8  				CALL (R2)
                       
00000058  16 00 B0 25  _LOOP_1_CONT	ADD R3, IO_CB_DEF_SIZE, R3
0000005C  01 00 40 36  				SUB R4, 1, R4
00000060  3C 00 00 C6  				JP_NZ _LOOP_1
                       _ENDLOOP_1		
00000064  00 00 00 82  				POP R4
00000068  00 00 80 81  				POP R3
0000006C  00 00 00 81  				POP R2
00000070  00 00 80 80  				POP R1
00000074  00 00 00 80  				POP R0
00000078  00 00 10 00  				MOVE R0, SR
0000007C  00 00 00 80  				POP R0
00000080  01 00 00 D8  				RETI
                       
                       
                       ;===============================================================================
                       ; 	5. OPERATING SYSTEM MAIN FUNCTION
                       ;===============================================================================
                       				; ORG XYZ
                       				; CALL _INT_HANDLER
                       
                       _OS_INIT		; Handler setup testing
00000084  08 20 00 04  				MOVE 2008, R0
00000088  01 00 80 04  				MOVE 1, R1
0000008C  00 10 00 05  				MOVE 1000, R2
00000090  E4 00 00 CC  				CALL REG_INT_CB
                       
00000094  08 30 00 04  				MOVE 3008, R0
00000098  01 00 80 04  				MOVE 1, R1
0000009C  50 10 00 05  				MOVE 1050, R2
000000A0  E4 00 00 CC  				CALL REG_INT_CB
                       
                       				; Handler call testing
000000A4  07 00 80 04  				MOVE 7, R1
000000A8  08 20 80 B8  				STORE R1, (2008)
000000AC  10 00 00 CC  				CALL _INT_HANDLER
                       				
000000B0  00 00 00 F8  _OS_LOOP		HALT
                       
                       
                       ;===============================================================================
                       ; 	6. SYSTEM CALLS DEFINITION
                       ;===============================================================================
                       
                       REG_NMI_CB 		; ORG XYZ
                       ;###############################################################################
                       ;# 	Register a handler for IO interrupt unit (non-masking interrupts)
                       ;#
                       ;#   :: 	IO_UNIT_SR_ADDR (R0) 	- IO unit's status register address
                       ;# 			IO_UNIT_SR_MASK (R1) 	- Status register interrupt AND mask
                       ;# 			IO_UNIT_CB_ADDR (R2) 	- Starting callback address
                       ;# 	 => 	Nothing
                       ;# 	
                       ;# 			R3 - address pointers
                       ;###############################################################################
000000B4  00 00 80 89  				PUSH R3
000000B8  14 01 80 B1  				LOAD R3, (NMI_CB_DEF_CNT_ADDR)
000000BC  04 00 B0 55  				SHL R3, IO_CB_DEF_SIZE_LG, R3 		; R3 := offset from start address
000000C0  18 01 B0 25  				ADD R3, NMI_CB_DEF_START_ADDR, R3
000000C4  00 00 30 BC  				STORE R0, (R3)
000000C8  04 00 B0 BC  				STORE R1, (R3+4)
000000CC  08 00 30 BD  				STORE R2, (R3+8)
000000D0  14 01 80 B1  				LOAD R3, (NMI_CB_DEF_CNT_ADDR)
000000D4  01 00 B0 25  				ADD R3, 1, R3
000000D8  14 01 80 B9  				STORE R3, (NMI_CB_DEF_CNT_ADDR)
000000DC  00 00 80 81  				POP R3
000000E0  00 00 00 D8  				RET
                       
                       
                       REG_INT_CB 		; ORG XYZ
                       ;###############################################################################
                       ;# 	Register a handler for IO interrupt unit (masking interrupts)
                       ;#
                       ;#   :: 	IO_UNIT_SR_ADDR (R0) 	- IO unit's status register address
                       ;# 			IO_UNIT_SR_MASK (R1) 	- Status register interrupt AND mask
                       ;# 			IO_UNIT_CB_ADDR (R2) 	- Starting callback address
                       ;# 	 => 	Nothing
                       ;# 	
                       ;# 			R3 - address pointers
                       ;###############################################################################
000000E4  00 00 80 89  				PUSH R3
000000E8  18 02 80 B1  				LOAD R3, (INT_CB_DEF_CNT_ADDR)
000000EC  04 00 B0 55  				SHL R3, IO_CB_DEF_SIZE_LG, R3 		; R3 := offset from start address
000000F0  1C 02 B0 25  				ADD R3, INT_CB_DEF_START_ADDR, R3
000000F4  00 00 30 BC  				STORE R0, (R3)
000000F8  04 00 B0 BC  				STORE R1, (R3+4)
000000FC  08 00 30 BD  				STORE R2, (R3+8)
00000100  18 02 80 B1  				LOAD R3, (INT_CB_DEF_CNT_ADDR)
00000104  01 00 B0 25  				ADD R3, 1, R3
00000108  18 02 80 B9  				STORE R3, (INT_CB_DEF_CNT_ADDR)
0000010C  00 00 80 81  				POP R3
00000110  00 00 00 D8  				RET
                       
                       ;===============================================================================
                       ; 	7. AUXILLIARY FUNCTIONS
                       ;===============================================================================
                       
                       ;===============================================================================
                       ; 	8. OS MEMORY SPACE
                       ;===============================================================================
                       						; ORG XYZ
00000114  00 00 00 00  NMI_CB_DEF_CNT_ADDR 	DW 0
                       NMI_CB_DEF_START_ADDR 	DS 100
                       
00000218  00 00 00 00  INT_CB_DEF_CNT_ADDR 	DW 0
                       INT_CB_DEF_START_ADDR 	DS 100
                       
                       
                       ;===============================================================================
                       ; 	9. USER SPACE PROGRAMS
                       ;===============================================================================
                       				
                       				ORG 500
                       	
                       TEST_CB_1 		; ORG XYZ
00000500  34 12 00 07  				MOVE 1234, R6
00000504  00 00 00 D8  				RET
                       
                       TEST_CB_1 		; ORG XYZ
00000508  78 56 00 07  				MOVE 5678, R6
0000050C  00 00 00 D8  				RET
