from math import ceil, log

# Unicode symbols for inactive and active breakpoints
def get_breakpoint_symbol( b ):
    return '●' if b else '○'

# Reverse string

def rev_str( s ):
    return ''.join( reversed( s ) )

# Bin-hex conversions

def bin_to_hex( x ):
    return ( '{:0>' + str( len( x ) // 4 ) + 'X}' ).format( int( x, 2 ) )

def bin_to_pretty_hex( x ):
    a = bin_to_hex( x )
    s = ''
    for i in range( 0, len( a ), 2 ):
        s += a[ i:i+2 ] + ' '
    return s[ : -1 ]

# Two's complement of a number

def compl2( x, w ):
    if x == '0'*w: return x
    return ( '{:0>' + str( w ) + 'b}' ).format( 2**w - int( x, 2 ) )

# Test whether number x can fit into b bits
def fits_into( x, b ):
    return x == 0 or int( log( x, 2 ) ) < b

# Takes an integer, returns a 20-bit binary string
def extend20( x ):
    if abs( x ) > 2**32:
        raise ValueError( 'Number larger than 32 bits.' )
    y = '{:0>32b}'.format( abs( x ) )
    if x < 0:
        y = compl2( y, 32 )

    p = y.find( '1' if y[ 0 ] == '0' else '0' )
    if p > -1 and p <= 12:
        raise ValueError( 'Number too large to fit into 20 bits.' )
    else:
        return y[ 12: ]

# Extends 20-bit binary string to 32-bit string
def sign_extend( x ):
    return ( '0' * 12 if x[ 0 ] == '0' else '1' * 12 ) + x

# Takes a binary string, returns an integer
def from32( x ):
    return ( int( x, 2 ) if x[ 0 ] == '0' else -1*int( compl2( x, 32 ), 2 ) )

# Takes an int, returns a 32-bit binary string
def to32( x ):
    s = '{0:0>32b}'.format( abs( x ) )
    return compl2( s, 32 ) if x < 0 else s

# Takes a binary list or string, returns a bool
def is_zero( x ):
    return '{0:b}'.format( not bool( list( filter( lambda x: x == '1', x ) ) ) )

# ALU helpers
def add_bin( a, b, c ):
    z = int( a, 2 ) + int( b, 2 ) + int( c, 2 )
    return '{0:b}'.format( z % 2 ), '{0:b}'.format( z // 2 )

def xor_bin( a, b ):
    return '0' if a == b else '1'

def sub_bin( a, b, c ):
    z = int( a, 2 ) - int( b, 2 ) - int( c, 2 )
    if z >= 0: return str( z ), '0'
    elif z == -1: return '1', '1'
    else: return '0', '1'

# ALU operations
def add32( x, y, carry = '0' ):
    lx, ly, lc, ls = list( x ), list( y ), [ '0' ]*32, [ '0' ]*32
    for i in range( 31, -1, -1 ):
        ls[ i ], lc[ i ] = add_bin( lx[ i ], ly[ i ], lc[ i+1 ] if i < 31 else carry )
    return ''.join( ls ), lc[ 0 ], xor_bin( lc[ 0 ], lc[ 1 ] ), ls[ 0 ], is_zero( ls )


def sub32( x, y, carry = '0' ):
    lx, ly, lc, ls = list( x ), list( y ), [ '0' ]*32, [ '0' ]*32
    for i in range( 31, -1, -1 ):
        ls[ i ], lc[ i ] = sub_bin( lx[ i ], ly[ i ], lc[ i+1 ] if i < 31 else carry )
    return ''.join( ls ), lc[ 0 ], xor_bin( lc[ 0 ], lc[ 1 ] ), ls[ 0 ], is_zero( ls )

def cmp32( x, y ):
    return sub32( x, y )[ 1: ]

def and32( x, y ):
    lx, ly, lr = list( x ), list( y ), [ '0' ]*32
    for i in range( 0, 32 ):
        lr[ i ] = '1' if lx[ i ] == '1' and ly[ i ] == '1' else '0'
    return ''.join( lr ), '0', '0', lr[ 0 ], is_zero( lr )

def or32( x, y ):
    lx, ly, lr = list( x ), list( y ), [ '0' ]*32
    for i in range( 0, 32 ):
        lr[ i ] = '1' if lx[ i ] == '1' or ly[ i ] == '1' else '0'
    return ''.join( lr ), '0', '0', lr[ 0 ], is_zero( lr )

def xor32( x, y ):
    lx, ly, lr = list( x ), list( y ), [ '0' ]*32
    for i in range( 0, 32 ):
        lr[ i ] = '1' if lx[ i ] != ly[ i ] else '0'
    return ''.join( lr ), '0', '0', lr[ 0 ], is_zero( lr )

def shl32( x, y ):
    iy = from32( y )
    if iy < 0: return shr32( x, compl2( y, 32 ) )
    z = x[ iy: ] + '0'*iy if iy < 32 else '0'*32
    return z, x[ iy-1 ] if iy > 0 else '0', '0', z[ 0 ], is_zero( z )

def shr32( x, y ):
    iy = from32( y )
    if iy < 0: return shl32( x, compl2( y, 32 ) )
    z = '0' * iy + x[ :(32-iy) ] if iy < 32 else '0'*32
    return z, x[ 32-iy ] if iy > 0 else '0', '0', z[ 0 ], is_zero( z )

def ashr32( x, y ):
    iy = from32( y )
    if iy < 0: return shl32( x, compl2( y, 32 ) )
    z = x[ 0 ] * iy + x[ :(32-iy) ] if iy < 32 else x[ 0 ]*32
    return z, x[ 32-iy ] if iy < 33 and iy > 0 else '0', '0', z[ 0 ], is_zero( z )

def rotl32( x, y ): # TODO: bug if negative rotation
    iy = from32( y ) % 32
    if iy < 0: return rotr( x, y )
    z = x[ iy: ] + x[ :iy ]
    return z, x[ iy-1 ], '0', z[ 0 ], is_zero( z )

def rotr32( x, y ):
    iy = from32( y ) % 32
    if iy < 0: return rotl( x, y )
    z = x[ 32-iy: ] + x[ : 32-iy ]
    return z, x[ 32-iy ], '0', z[ 0 ], is_zero( z )
