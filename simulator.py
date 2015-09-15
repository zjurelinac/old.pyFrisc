from utils import *

import sys

# TODO: Watch for reversal of data in memory ( LE | BE )!!!

class FRISCProcessor:
    SP = '111'

    def __init__( self, mem_size, program = None ):
        self.MEM_SIZE = mem_size
        self.memory = []
        self.annotations = []
        self.registers = {}
        self.flags = {
            'TERM' : False,
            'IIF' : False
        }

        if program is not None:
            self.load_program( program )
        else:
            self.reset()

    def reset( self ):
        self.memory = [ '00000000' ] * self.MEM_SIZE
        self.annotations = [ '' ] * self.MEM_SIZE
        self.registers = {
            '000' : '0'*32,
            '001' : '0'*32,
            '010' : '0'*32,
            '011' : '0'*32,
            '100' : '0'*32,
            '101' : '0'*32,
            '110' : '0'*32,
            '111' : '0'*32,
            'PC'  : '0'*32,
            'SR'  : '0'*32
        }
        self.flags = dict.fromkeys( self.flags.keys(), False )

    def load_program( self, program ):
        self.reset()

        f = open( program, 'r' )
        ls = filter( lambda x: x[ 0 ], [ ( l[ :21 ].rstrip(), l[ 21: ] ) for l in f ] )

        tnum = 0
        for ( l, a ) in ls:
            num = l[ :8 ].strip()
            num = int( num, 16 ) if num else tnum + 4
            for i in range( 0, 4 ):
                j = 10 + 3*i
                try:
                    self.memory[ num + i ] = '{0:0>8b}'.format( int( l[ j : ( j+2 ) ], 16 ) )
                except ValueError:
                    pass
            tnum = num

            self.annotations[ num ] = a.lstrip()

    def run( self ):
        try:
            while( not self.flags[ 'TERM' ] ):
                self.run_step()
                self.show_registers()
            self.show_memory()
        except Exception as e:
            print( str( e ) )

    def run_step( self ):
        pc = self.registers[ 'PC' ]
        pci = int( pc, 2 )
        self.registers[ 'PC' ] = to32( pci + 4 )

        cmd = self.get_word_from_mem( pci )

        opcode = cmd[ 0:5 ]
        func = cmd[ 5 ]
        rd = cmd[ 6:9 ]
        rs1 = cmd[ 9:12 ]
        rs2 = cmd[ 12:15 ]
        imm = sign_extend( cmd[ 12: ] )
        cond = cmd[ 6:10 ]
        ret_type = cmd[ 30: ]

        #print( pci, 'executing:', cmd, 'opcode:', opcode )

        if opcode == '00000':       # MOVE
            if rs1 == '000':
                value = imm if func == '1' else self.registers[ rs2 ]
            else:
                if rs1[ 1 ] == '1': rd = 'SR'
                if rs2[ 1 ] == '1': value = self.registers[ 'SR' ]

            #print( 'MOVE to', rd, 'value', value )
            self.registers[ rd ] = value

        elif opcode[ 0 ] == '0':    # ALU
            arg1 = self.registers[ rs1 ]
            arg2 = self.registers[ rs2 ] if func == '0' else imm

            if opcode == '00001':   # OR
                print( 'OR' )
                self.registers[ rd ], c, v, n, z = or32( arg1, arg2 )
            elif opcode == '00010': # AND
                print( 'AND' )
                self.registers[ rd ], c, v, n, z = and32( arg1, arg2 )
            elif opcode == '00011': # XOR
                print( 'XOR' )
                self.registers[ rd ], c, v, n, z = xor32( arg1, arg2 )
            elif opcode == '00100': # ADD
                print( 'ADD' )
                self.registers[ rd ], c, v, n, z = add32( arg1, arg2 )
            elif opcode == '00101': # ADC
                print( 'ADC' )
                self.registers[ rd ], c, v, n, z = add32( arg1, arg2, self.registers[ 'SR' ][ 1 ] )
            elif opcode == '00110': # SUB
                print( 'SUB' )
                self.registers[ rd ], c, v, n, z = sub32( arg1, arg2 )
            elif opcode == '00111': # SBC
                print( 'SBC' )
                self.registers[ rd ], c, v, n, z = sub32( arg1, arg2, self.registers[ 'SR' ][ 1 ] )
            elif opcode == '01000': # ROTL
                print( 'ROTL' )
                self.registers[ rd ], c, v, n, z = rotl32( arg1, arg2 )
            elif opcode == '01001': # ROTR
                print( 'ROTR' )
                self.registers[ rd ], c, v, n, z = rotr32( arg1, arg2 )
            elif opcode == '01001': # SHL
                print( 'SHL' )
                self.registers[ rd ], c, v, n, z = shl32( arg1, arg2 )
            elif opcode == '01001': # SHR
                print( 'SHR' )
                self.registers[ rd ], c, v, n, z = shr32( arg1, arg2 )
            elif opcode == '01001': # ASHR
                print( 'ASHR' )
                self.registers[ rd ], c, v, n, z = ashr32( arg1, arg2 )
            elif opcode == '01101': # CMP
                print( 'CMP' )
                c, v, n, z = cmp32( arg1, arg2 )
            else:
                raise ValueError( 'No such ALU operation' )

            self.registers[ 'SR' ] = self.registers[ 'SR' ][ :28 ] + z + v + c + n

        elif opcode[ 0:2 ] == '10': # MEMORY
            adr = add32( self.registers[ rs1 ], imm )[ 0 ] if func == '1' else imm
            # TODO: What if negative address

            if opcode == '10010':   # LOADB
                self.registers[ rd ] = self.get_byte_from_mem( adr_num )

            elif opcode == '10011': # STOREB
                adr_num = from32( adr )
                self.set_byte_in_mem( adr_num, self.registers[ rd ] )

            elif opcode == '10100': # LOADH
                adr_num = from32( adr[ :31 ] + '0' )
                #print( 'LOADH from', adr_num, 'word', self.get_word_from_mem( adr_num ) )
                self.registers[ rd ] = self.get_halfword_from_mem( adr_num )

            elif opcode == '10101': # STOREH
                adr_num = from32( adr[ :31 ] + '0' )
                #print( 'STOREH to', adr_num, 'word', self.get_halfword_from_mem( adr_num ) )
                self.set_halfword_in_mem( adr_num, self.registers[ rd ] )

            elif opcode == '10110': # LOAD
                adr_num = from32( adr[ :30 ] + '00' )
                #print( 'LOAD from', adr_num, 'word', self.get_word_from_mem( adr_num ) )
                self.registers[ rd ] = self.get_word_from_mem( adr_num )

            elif opcode == '10111': # STORE
                adr_num = from32( adr[ :30 ] + '00' )
                #print( 'STORE to', adr_num )
                self.set_word_in_mem( adr_num, self.registers[ rd ] )

            elif opcode == '10001': # PUSH
                self.registers[ SP ] = sub32( self.registers[ SP ], to32( 4 ) )[ 0 ]
                adr_num = from32( self.registers[ SP ] )
                self.set_word_in_mem( adr_num, self.registers[ rd ] )

            elif opcode == '10000': # POP
                adr_num = from32( self.registers[ SP ] )
                self.registers[ rd ] = self.get_word_from_mem( adr_num )
                self.registers[ SP ] = add32( self.registers[ SP ], to32( 4 ) )[ 0 ]

        elif opcode[ 0:2 ] == '11': # CONTROL
            if self.test_cond( cond ):
                if opcode == '11000':   # JP
                    print( 'JP' )
                    self.registers[ 'PC' ] = imm if func == '1' else self.registers[ rs2 ]

                elif opcode == '11001': # CALL
                    print( 'CALL' )
                    self.registers[ SP ] = sub32( self.registers[ SP ], to32( 4 ) )[ 0 ]
                    self.set_word_in_mem( self.registers[ SP ], self.registers[ 'PC' ] )
                    self.registers[ 'PC' ] = imm if func == '1' else self.registers[ rs2 ]

                elif opcode == '11010': # JR
                    print( 'JR' )
                    self.registers[ 'PC' ] = add32( self.registers[ 'PC' ], imm )[ 0 ]

                elif opcode == '11011': # RET(_|I|N)
                    print( 'RETX' )
                    self.registers[ 'PC' ] = self.get_word_from_mem( self.registers[ SP ] )
                    self.registers[ SP ] = add32( self.registers[ SP ], to32( 4 ) )[ 0 ]

                    if ret_type == '01': # RETI
                        self.registers[ 'SR' ] = self.registers[ 'SR' ][ :4 ] + '1' + self.registers[ 'SR' ][ 5: ]
                    elif ret_type == '11': # RETN
                        self.flags[ 'IIF' ] = True


                elif opcode == '11111': # HALT
                    print( 'HALT' )
                    self.flags[ 'TERM' ] = True

        else:
            raise ValueError( 'Unknown opcode' )

    def get_word_from_mem( self, i ):
        return self.memory[ i+3 ] + self.memory[ i+2 ] + self.memory[ i+1 ] + self.memory[ i ]

    def get_halfword_from_mem( self, i ):
        return '0'*16 + self.memory[ i+1 ] + self.memory[ i+0 ]

    def get_byte_from_mem( self, i ):
        return '0'*24 + self.memory[ i ]

    def set_word_in_mem( self, i, w ):
        self.memory[ i+3 ] = w[ :8 ]
        self.memory[ i+2 ] = w[ 8:16 ]
        self.memory[ i+1 ] = w[ 16:24 ]
        self.memory[ i ] = w[ 24: ]

    def set_halfword_in_mem( self, i, hw ):
        self.memory[ i+1 ] = hw[ 16:24 ]
        self.memory[ i ] = hw[ 24: ]

    def set_byte_in_mem( self, i, b ):
        self.memory[ i ] = b[ 24: ]

    def test_cond( self, cond ):
        sr = self.registers[ 'SR' ]
        n, c, v, z = sr[ 31 ] == '1', sr[ 30 ] == '1', sr[ 29 ] == '1', sr[ 28 ] == '1'
        ret = True
        if cond == '0000':
            ret = True
        elif cond == '0010':
            ret = not n
        elif cond == '0110':
            ret = not v
        elif cond == '0100':
            ret = not c
        elif cond == '1000':
            ret = not z
        elif cond == '0001':
            ret = n
        elif cond == '0011':
            ret = c
        elif cond == '0101':
            ret = v
        elif cond == '0111':
            ret = z
        elif cond == '1001':
            ret = not c or z
        elif cond == '1010':
            ret = c and not z
        elif cond == '1011':
            ret = n != v
        elif cond == '1100':
            ret = n != v or z
        elif cond == '1101':
            ret = n == v
        elif cond == '1110':
            ret = n == v and not z
        else:
            raise ValueError( 'Unknown condition' )
        return ret

    def show_registers( self ):
        print( '='*40 )
        print( 'R0:', bin_to_hex( self.registers[ '000' ] ), '\t', 'R5:', bin_to_hex( self.registers[ '101' ] ) )
        print( 'R1:', bin_to_hex( self.registers[ '001' ] ), '\t', 'R6:', bin_to_hex( self.registers[ '110' ] ) )
        print( 'R2:', bin_to_hex( self.registers[ '010' ] ), '\t', 'R7:', bin_to_hex( self.registers[ '111' ] ) )
        print( 'R3:', bin_to_hex( self.registers[ '011' ] ), '\t', 'PC:', bin_to_hex( self.registers[ 'PC' ] ) )
        print( 'R4:', bin_to_hex( self.registers[ '100' ] ), '\t', 'SR:', bin_to_hex( self.registers[ 'SR' ] ) )
        print()

    def show_memory( self ):
        for i in range( 0, self.MEM_SIZE, 4 ):
            print( '# {:0>3X}'.format( i ),
                      ':\t', bin_to_hex( self.memory[ i ] ),
                             bin_to_hex( self.memory[ i+1 ] ),
                             bin_to_hex( self.memory[ i+2 ] ),
                             bin_to_hex( self.memory[ i+3 ] ), end = '\n' if (i+4) % 16 == 0 else '\t' )

if __name__ == '__main__':
    fp = FRISCProcessor( 1000, sys.argv[ 1 ] )
    print( 'starting' )
    fp.run()
