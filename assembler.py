from itertools import chain
from math import ceil, log
from utils import *

import os.path
import re
import sys
import yaml

data = dict()
labels = dict()
memory = []
maxnum = 0

def show_error( s ):
    return s, False

def round_to_word( i ):
    return int( int( i/data[ 'consts' ][ 'words_per_line' ] + 1 ) * data[ 'consts' ][ 'words_per_line' ]
        if i%data[ 'consts' ][ 'words_per_line' ] != 0 else i )

def args_len( args ):
    n = 0
    while args:
        _, args = parse_constant( args )
        n += 1
    return n

def place_in_mem( res, n ):
    for i in range( 0, data[ 'consts' ][ 'words_per_line' ] ):
        memory[ n ] = res[ data[ 'consts' ][ 'word_size' ]*i : data[ 'consts' ][ 'word_size' ]*(i+1) ]
        n += 1

def to_little_endian( x, n ):
    i = 0
    arr = []
    for i in range( 0, n ):
        arr.append( x[ data[ 'consts' ][ 'word_size' ]*i : data[ 'consts' ][ 'word_size' ]*(i+1) ] )
    return ''.join( reversed( arr ) )

def parse_constant( args, leftovers = True ):
    if not args:
        raise ValueError( 'Nothing to parse.' )
    if args[ 0 ][ 0 ] == '%':
        r = int( args[ 1 ], data[ 'consts' ][ 'base_code' ][ args[ 0 ][ 1 ] ] )
        a = args[ 2: ] if len( args ) > 2 else []

    elif args[ 0 ][ 0 ].isdigit():
        r = int( args[ 0 ], data[ 'consts' ][ 'default_base' ] )
        a = args[ 1: ] if len( args ) > 1 else []

    elif args[ 0 ][ 0 ] == '-':
        r = -int( args[ 1 ] , data[ 'consts' ][ 'default_base' ] )
        a = args[ 2: ] if len( args ) > 2 else []

    elif args[ 0 ] in labels:
        r = labels[ args[ 0 ] ]
        a = args[ 1: ] if len( args ) > 1 else []

    else:
        raise ValueError( 'Unknown arguments, cannot parse.' )

    if abs( r ) > 2**32:
        raise ValueError( 'Constant larger than 32 bits.' )

    if not leftovers:
        if a: raise ValueError( 'Extra symbols in line.' )
        else: return r
    else:
        return [ r, a ]

def parse_reg( arg ):
    return data[ 'codes' ][ 'REG' ][ arg ]

def parse_src2( args ):
    try:
        res = parse_reg( args[ 0 ] ), args[ 1: ]
    except KeyError:
        res = parse_constant( args, True )
        res[ 0 ] = extend20( res[ 0 ] )
    return res

def parse_aluop( cmd, args ):
    src1 = parse_reg( args[ 0 ] )
    src2, args = parse_src2( args[ 1: ] )
    dest = parse_reg( args[ 0 ] )
    result = to_little_endian( data[ 'codes' ][ 'ALU' ][ cmd ] + ( '0' if len( src2 ) == 3 else '1' )
        + dest + src1 + src2 + ( '0'*17 if len( src2 ) != 20 else '' ), data[ 'consts' ][ 'words_per_line' ] )
    return result

def parse_memop( cmd, args ):
    reg = parse_reg( args[ 0 ] )
    result = data[ 'codes' ][ 'MEM' ][ cmd ]
    if args[ 1 ] != '(':
        raise ValueError
    try:
        loc = parse_reg( args[ 2 ] )
        shift = 0
        sign = '+'
        if args[ 3 ] != ')':
            sign = args[ 3 ]
            shift, args = parse_constant( args[ 4: ], True )
            if len( args ) != 1 and args[ 0 ] != ')':
                raise ValueError( 'Incorrect command form.' )
        shift = extend20( ( -1 if sign == '-' else 1 ) * shift )
        result += '1' + reg + loc + shift

    except KeyError:
        if args[ 2 ] in labels:
            loc = labels[ args[ 2 ] ]
            if args[ 3 ] != ')':
                raise ValueError( 'Incorrect absolute addressing.' )
        else:
            loc, args = parse_constant( args[ 2: ], True )
            if len( args ) != 1 and args[ 0 ] != '=':
                raise ValueError( 'Incorrect command form.' )

        loc = extend20( loc )
        result += '0' + reg + '000' + loc

    result = to_little_endian( result, data[ 'consts' ][ 'words_per_line' ] )
    return result

def parse_stackop( cmd, args ):
    dest = parse_reg( args[ 0 ] )
    result = to_little_endian( data[ 'codes' ][ 'STACK' ][ cmd ] + '0' + dest + '0'*23, data[ 'consts' ][ 'words_per_line' ] )
    return result

def parse_ctrlop( cmd, args ):
    if args[ 0 ] == '_':
        flag = args[ 1 ]
        args = args[ 2: ] if len( args ) > 2 else []
    else: flag = '$'

    if args[ 0 ] == '(':
        op = '0'
        loc = parse_reg( args[ 1 ] ) + '0'*17
    else:
        op = '1'
        loc = extend20( parse_constant( args, False ) )

    result = to_little_endian( data[ 'codes' ][ 'CTRL' ][ cmd ] + op + data[ 'codes' ][ 'COND' ][ flag ]
        + '00' + loc, data[ 'consts' ][ 'words_per_line' ] )
    return result

def parse_retop( cmd, args ):
    flag = args[ 1 ] if args and args[ 0 ] == '_' else '$'
    result = to_little_endian( data[ 'codes' ][ 'RET' ][ cmd ] + '0' + data[ 'codes' ][ 'COND' ][ flag ]
        + 20*'0' + data[ 'codes' ][ 'RET_CODE' ][ cmd ], data[ 'consts' ][ 'words_per_line' ] )
    return result

def parse_moveop( cmd, args ):
    a = '0'
    src = '000'
    srcSR = False
    dest = '000'
    destSR = False

    if args[ 0 ] == 'SR':
       args = args[ 1: ]
       srcSR = True
    elif args[ 0 ] in data[ 'codes' ][ 'REG' ]:
        src = parse_reg( args[ 0 ] )
        args = args[ 1: ]
    else:
        a = '1'
        src, args = parse_constant( args, True )
        src = extend20( src )

    if args[ 0 ] != 'SR':
        dest = parse_reg( args[ 0 ] )
    else:
        destSR = True

    result = to_little_endian( data[ 'codes' ][ 'MOVE' ] + a + dest + '0' + '{:b}{:b}'.format( srcSR, destSR )
        + src + ( '0'*17 if len( src ) == 3 else '' ), data[ 'consts' ][ 'words_per_line' ] )

    return result

def parse_jr( cmd, args, n ):
    if args[ 0 ] == '_':
        flag = args[ 1 ]
        args = args[ 2: ] if len( args ) > 2 else []
    else: flag = '$'

    # TODO: Beware, if label, that's ok, if a bare number, NOT OK, won't jump N places forward but to address N
    offset = parse_constant( args, False )
    result = to_little_endian( data[ 'codes' ][ 'JR' ] + '1' + data[ 'codes' ][ 'COND' ][ flag ] + '00'
        + extend20( offset - n - 4 ), data[ 'consts' ][ 'words_per_line' ] )
    return result

def parse_cmp( cmd, args ):
    src1 = parse_reg( args[ 0 ] )
    src2, args = parse_src2( args[ 1: ] )
    result = to_little_endian( data[ 'codes' ][ 'CMP' ] + ( '0' if len( src2 ) == 3 else '1' )
        + '000' + src1 + src2 + ( '0'*17 if len( src2 ) != 20 else '' ), data[ 'consts' ][ 'words_per_line' ] )
    return result

def define_data( cmd, args, n ):
    size = data[ 'consts' ][ 'define_data' ][ cmd ]*data[ 'consts' ][ 'word_size' ]
    p = []
    while args:
        x, args = parse_constant( args )
        if not fits_into( x, size ):
            raise ValueError( 'Cannot place data in memory, {} is too big for {} bits.'.format( x, size ) )
        t = to_little_endian( ( '{:0>' + str( size ) + 'b}' ).format( x ), size // data[ 'consts' ][ 'word_size' ] )
        p.append( t )

        for i in range( 0, size ):
            y = t[ data[ 'consts' ][ 'word_size' ]*i : data[ 'consts' ][ 'word_size' ]*(i+1) ]
            memory[ n ] = y
            n += 1

    return p

def define_space( cmd, args, n ):
    len = parse_constant( args, False )
    for i in range( 0, len ):
        memory[ n+i ] = '0'*data[ 'consts' ][ 'word_size' ]
    return [ '0'*data[ 'consts' ][ 'line_size' ] ]* ceil( len/data[ 'consts' ][ 'words_per_line' ] )

def parse_lines( ls ):
    lines = []
    num = 0
    for l in ls:
        res = { 'original' : l }
        sl = l.upper().split( ';', maxsplit = 1 )[ 0 ]
        if sl:
            res[ 'blank' ] = False
            if sl[ 0 ].isspace(): lab = ''
            else:
                t = sl.split( maxsplit = 1 )
                lab = t[ 0 ]
                sl = t[ 1 ] if len( t ) > 1 else ''
            ls = re.split( data[ 'consts' ][ 'separators' ], sl.strip() )
            res[ 'cmd' ] = ls[ 0 ]
            res[ 'args' ] = [ x for x in ls[ 1: ] if x ] if len( ls ) > 1 else []

            if not res[ 'cmd' ]: res[ 'blank' ] = True

            if res[ 'cmd' ] == data[ 'consts' ][ 'origin_cmd' ]:
                nnum = round_to_word( parse_constant( res[ 'args' ] )[ 0 ] )
                if nnum < num:
                    raise ValueError( res[ 'original' ] + ' :: Impossible origin, location too small' )
                num = nnum
                if lab: labels[ lab ] = num
                res[ 'blank' ] = True

            elif res[ 'cmd' ] == data[ 'consts' ][ 'equals_cmd' ]:
                if lab: labels[ lab ] = parse_constant( res[ 'args' ] )[ 0 ]
                res[ 'blank' ] = True

            elif res[ 'cmd' ] in data[ 'consts' ][ 'define_data' ]:
                if lab: labels[ lab ] = num
                res[ 'num' ] = num
                num += round_to_word( args_len( res[ 'args' ] )*data[ 'consts' ][ 'define_data' ][ res[ 'cmd' ] ] )

            elif res[ 'cmd' ] == data[ 'consts' ][ 'define_space' ]:
                if lab: labels[ lab ] = num
                res[ 'num' ] = num
                num += round_to_word( parse_constant( res[ 'args' ] )[ 0 ] )

            elif res[ 'cmd' ]:
                if lab: labels[ lab ] = num
                res[ 'num' ] = num
                num += data[ 'consts' ][ 'words_per_line' ]

            else:
                if lab: labels[ lab ] = num

            if 'num' not in res:
                res[ 'num' ] = -1
        else:
            res[ 'blank' ] = True
            res[ 'num' ] = -1
        lines.append( res )

    if num >= data[ 'consts' ][ 'max_memory' ]:
        raise ValueError( 'Too much memory used' )

    global maxnum
    maxnum = num

    return lines

def assemble( f ):
    """ Assembles the contents of a file f

        This function takes a name f of a file containing FRISC assembler code,
        and translates it into machine code.

        Two new files are created:
            1. readable file containing the machine code together with it's source
            2. binary file containing only the machine code
    """
    print( 'Assembling file', f )
    global data, memory, maxnum
    data = yaml.load( open( 'config/definitions/frisc.lang.yaml', 'r' ).read() )
    memory = [ '00000000' ] * data[ 'consts' ][ 'max_memory' ]

    try:
        pls = parse_lines( open( f ).read().splitlines() )
    except Exception as e:
        return show_error( 'An error occurred in first pass: ' + str( e ) )

    adr_len = data[ 'consts' ][ 'line_size' ] // 4
    prt_len = len( bin_to_pretty_hex( '0' * data[ 'consts' ][ 'line_size' ] ) )

    path = os.path.abspath( f )
    base = path.rsplit( '.', maxsplit = 1 )[ 0 ]

    pfile = open( base + '.p', 'w' )
    efile = open( base + '.e', 'wb' )


    j = 1
    for p in pls:
        if not p[ 'blank' ]:
            try:
                multiple = False
                if p[ 'cmd' ] == 'END':
                    break
                elif p[ 'cmd' ] in data[ 'codes' ][ 'ALU' ]:
                    p[ 'parsed' ] = parse_aluop( p[ 'cmd' ], p[ 'args' ] )
                    place_in_mem( p[ 'parsed' ], p[ 'num' ] )
                elif p[ 'cmd' ] in data[ 'codes' ][ 'MEM' ]:
                    p[ 'parsed' ] = parse_memop( p[ 'cmd' ], p[ 'args' ] )
                    place_in_mem( p[ 'parsed' ], p[ 'num' ] )
                elif p[ 'cmd' ] in data[ 'codes' ][ 'STACK' ]:
                    p[ 'parsed' ] = parse_stackop( p[ 'cmd' ], p[ 'args' ] )
                    place_in_mem( p[ 'parsed' ], p[ 'num' ] )
                elif p[ 'cmd' ] in data[ 'codes' ][ 'CTRL' ]:
                    p[ 'parsed' ] = parse_ctrlop( p[ 'cmd' ], p[ 'args' ] )
                    place_in_mem( p[ 'parsed' ], p[ 'num' ] )
                elif p[ 'cmd' ] in data[ 'codes' ][ 'RET' ]:
                    p[ 'parsed' ] = parse_retop( p[ 'cmd' ], p[ 'args' ] )
                    place_in_mem( p[ 'parsed' ], p[ 'num' ] )
                elif p[ 'cmd' ] == 'MOVE':
                    p[ 'parsed' ] = parse_moveop( p[ 'cmd' ], p[ 'args' ] )
                    place_in_mem( p[ 'parsed' ], p[ 'num' ] )
                elif p[ 'cmd' ] == 'CMP':
                    p[ 'parsed' ] = parse_cmp( p[ 'cmd' ], p[ 'args' ] )
                    place_in_mem( p[ 'parsed' ], p[ 'num' ] )
                elif p[ 'cmd' ] == 'JR':
                    p[ 'parsed' ] = parse_jr( p[ 'cmd' ], p[ 'args' ], p[ 'num' ] )
                    place_in_mem( p[ 'parsed' ], p[ 'num' ] )
                elif p[ 'cmd' ] in data[ 'consts' ][ 'define_data' ]:
                    p[ 'parsed' ] = define_data( p[ 'cmd' ], p[ 'args' ], p[ 'num' ] )
                    multiple = True
                elif p[ 'cmd' ] == data[ 'consts' ][ 'define_space' ]:
                    p[ 'blank' ] = True
                else:
                    print( p )
                    raise ValueError( 'Unknown command' )
            except Exception as e:
                return show_error( 'An error occurred in second pass on line ' + str( j )
                    + ':' + p[ 'original' ] + ' :: ' + str( e ) )

        if p[ 'blank' ]:
            pfile.write(( ' ' * ( adr_len + prt_len + 4 ) +  p[ 'original' ] )
                [ :data[ 'consts' ][ 'max_source_line_length' ] ] + '\n')
        else:
            if multiple:
                pfile.write(( ('{:0>' + str( adr_len ) + 'X}  ' ).format( p[ 'num' ] ) +
                    bin_to_pretty_hex( p[ 'parsed' ][ 0 ] ) + '  ' + p[ 'original' ] )
                    [ :data[ 'consts' ][ 'max_source_line_length' ] ] + '\n')
                for i in p[ 'parsed' ][ 1: ]:
                    pfile.write( ' '*( adr_len + 2 ) + bin_to_pretty_hex( i ) + '\n' )
            else:
                pfile.write(( ('{:0>' + str( adr_len ) + 'X}  ' ).format( p[ 'num' ] ) +
                    bin_to_pretty_hex( p[ 'parsed' ] ) + '  ' + p[ 'original' ] )
                    [ :data[ 'consts' ][ 'max_source_line_length' ] ] + '\n')

        j += 1

    pfile.close()
    efile.close()

    return 'Source successfully assembled.', True

if __name__ == "__main__":
    print( assemble( sys.argv[ 1 ] ) )
