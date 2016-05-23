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
                       
                       ;----- IO UNITS LOCATIONS ------------------------------------------------------
                       
                       ; LogiCORE IP AXI UART LITE
                       ;  	BASEADDR = 0x00002000
                       IO_UART_READ_REG 		EQU 00002000
                       IO_UART_WRITE_REG 		EQU 00002004
                       IO_UART_STAT_REG 		EQU 00002008
                       IO_UART_CTRL_REG 		EQU 0000200C
                       
                       
                       ;===============================================================================
                       ; 	2. DEFAULT START SEQUENCE
                       ;===============================================================================
                       				ORG 0
00000000  00 40 80 07  _OS_INIT		MOVE 4000, SP
00000004  04 02 00 C4  				JP _OS_MAIN
                       
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
                       
                       _INT_HANDLER 	ORG 100
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
00000100  00 00 00 88  				PUSH R0
00000104  00 00 20 00  				MOVE SR, R0
00000108  00 00 00 88  				PUSH R0
0000010C  00 00 80 88  				PUSH R1
00000110  00 00 00 89  				PUSH R2
00000114  00 00 80 89  				PUSH R3
00000118  00 00 00 8A  				PUSH R4
                       				
0000011C  08 09 80 05  _START_1		MOVE INT_CB_DEF_START_ADDR, R3
00000120  04 09 00 B2  				LOAD R4, (INT_CB_DEF_CNT_ADDR)
00000124  00 00 40 6C  				CMP R4, 0
00000128  54 01 C0 C5  				JP_Z _ENDLOOP_1
                       
0000012C  00 00 30 B4  _LOOP_1			LOAD R0, (R3)
00000130  04 00 B0 B4  				LOAD R1, (R3+4)
00000134  08 00 30 B5  				LOAD R2, (R3+8)
                       
00000138  00 00 00 B4  				LOAD R0, (R0)
0000013C  00 00 02 10  				AND R0, R1, R0
00000140  48 01 C0 C5  				JP_Z _LOOP_1_CONT 	; IO unit inactive
00000144  00 00 04 C8  				CALL (R2)
                       
00000148  16 00 B0 25  _LOOP_1_CONT	ADD R3, IO_CB_DEF_SIZE, R3
0000014C  01 00 40 36  				SUB R4, 1, R4
00000150  2C 01 00 C6  				JP_NZ _LOOP_1
                       _ENDLOOP_1		
00000154  00 00 00 82  				POP R4
00000158  00 00 80 81  				POP R3
0000015C  00 00 00 81  				POP R2
00000160  00 00 80 80  				POP R1
00000164  00 00 00 80  				POP R0
00000168  00 00 10 00  				MOVE R0, SR
0000016C  00 00 00 80  				POP R0
00000170  01 00 00 D8  				RETI
                       
                       
                       ;===============================================================================
                       ; 	5. OPERATING SYSTEM MAIN FUNCTION
                       ;===============================================================================
                       				ORG 200
00000200  00 01 00 CC  				CALL _INT_HANDLER
                       
00000204  08 20 00 04  _OS_MAIN		MOVE 2008, R0
00000208  04 00 80 04  				MOVE 4, R1
0000020C  00 10 00 05  				MOVE 1000, R2
00000210  00 04 00 CC  				CALL REG_INT_CB
                       
00000214  08 30 00 04  				MOVE 3008, R0
00000218  04 00 80 04  				MOVE 4, R1
0000021C  50 10 00 05  				MOVE 1050, R2
00000220  00 04 00 CC  				CALL REG_INT_CB
                       
00000224  07 00 80 04  				MOVE 7, R1
00000228  08 20 80 B8  				STORE R1, (2008)
0000022C  00 01 00 CC  				CALL _INT_HANDLER
                       				
00000230  00 00 00 F8  _OS_LOOP		HALT
                       
                       
                       ;===============================================================================
                       ; 	6. SYSTEM CALLS DEFINITION
                       ;===============================================================================
                       
                       REG_NMI_CB 		ORG 300
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
00000300  00 00 80 89  				PUSH R3
00000304  00 05 80 B1  				LOAD R3, (NMI_CB_DEF_CNT_ADDR)
00000308  04 00 B0 55  				SHL R3, IO_CB_DEF_SIZE_LG, R3 		; R3 := offset from start address
0000030C  04 05 B0 25  				ADD R3, NMI_CB_DEF_START_ADDR, R3
00000310  00 00 30 BC  				STORE R0, (R3)
00000314  04 00 B0 BC  				STORE R1, (R3+4)
00000318  08 00 30 BD  				STORE R2, (R3+8)
0000031C  00 05 80 B1  				LOAD R3, (NMI_CB_DEF_CNT_ADDR)
00000320  01 00 B0 25  				ADD R3, 1, R3
00000324  00 05 80 B9  				STORE R3, (NMI_CB_DEF_CNT_ADDR)
00000328  00 00 80 81  				POP R3
0000032C  00 00 00 D8  				RET
                       
                       
                       REG_INT_CB 		ORG 400
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
00000400  00 00 80 89  				PUSH R3
00000404  04 09 80 B1  				LOAD R3, (INT_CB_DEF_CNT_ADDR)
00000408  04 00 B0 55  				SHL R3, IO_CB_DEF_SIZE_LG, R3 		; R3 := offset from start address
0000040C  08 09 B0 25  				ADD R3, INT_CB_DEF_START_ADDR, R3
00000410  00 00 30 BC  				STORE R0, (R3)
00000414  04 00 B0 BC  				STORE R1, (R3+4)
00000418  08 00 30 BD  				STORE R2, (R3+8)
0000041C  04 09 80 B1  				LOAD R3, (INT_CB_DEF_CNT_ADDR)
00000420  01 00 B0 25  				ADD R3, 1, R3
00000424  04 09 80 B9  				STORE R3, (INT_CB_DEF_CNT_ADDR)
00000428  00 00 80 81  				POP R3
0000042C  00 00 00 D8  				RET
                       
                       ;===============================================================================
                       ; 	7. AUXILLIARY FUNCTIONS
                       ;===============================================================================
                       
                       ;===============================================================================
                       ; 	8. OS MEMORY SPACE
                       ;===============================================================================
                       						ORG 500
00000500  00 00 00 00  NMI_CB_DEF_CNT_ADDR 	DW 0
                       NMI_CB_DEF_START_ADDR 	DS 400
                       
00000904  00 00 00 00  INT_CB_DEF_CNT_ADDR 	DW 0
                       INT_CB_DEF_START_ADDR 	DS 400
                       
                       
                       ;===============================================================================
                       ; 	9. User space programs
                       ;===============================================================================
                       	
                       TEST_CB_1 		ORG 1000
00001000  34 12 00 07  				MOVE 1234, R6
00001004  00 00 00 D8  				RET
                       
                       TEST_CB_1 		ORG 1050
00001050  78 56 00 07  				MOVE 5678, R6
00001054  00 00 00 D8  				RET
