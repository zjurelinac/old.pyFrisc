from collections import deque
from copy import deepcopy
from math import log10
from gi.repository import Gtk, Gio, Gdk, Pango

class Editor( Gtk.ScrolledWindow ):

    editor_view = Gtk.TextView()
    editor_buffer = Gtk.TextBuffer()

    line_numbers_view = Gtk.TextView()
    line_numbers_buffer = Gtk.TextBuffer()

    undo_stack = None
    redo_stack = None
    last_change = None
    suspend_change = False

    def __init__( self, parent, config ):
        Gtk.ScrolledWindow.__init__( self )

        self.parent = parent

        self.set_hexpand( True )
        self.set_vexpand( True )

        self.editor_view.set_buffer( self.editor_buffer )
        self.editor_view.set_name( 'editor' )

        tabs = Pango.TabArray.new( 1, True )
        tabs.set_tab( 0, Pango.TabAlign.LEFT, 32 )
        self.editor_view.set_tabs( tabs )

        self.line_numbers_view.set_buffer( self.line_numbers_buffer )
        self.line_numbers_view.set_name( 'line-numbers' )
        self.line_numbers_buffer.set_text( '0' )

        self.init_interface()

        self.editor_buffer.connect( 'insert-text', self.on_insert )
        self.editor_buffer.connect( 'delete-range', self.on_delete )
        self.editor_buffer.connect( 'changed', self.on_change )

        self.undo_stack = deque( maxlen = config[ 'max_undos' ] )
        self.redo_stack = deque( maxlen = config[ 'max_undos' ] )

    # GUI operations
    def init_interface( self ):
        grid = Gtk.Grid()

        self.line_numbers_view.set_vexpand( True )
        self.line_numbers_view.set_editable( False )
        self.line_numbers_view.set_cursor_visible( False )
        self.line_numbers_view.set_margin_top( 10 )
        self.line_numbers_view.set_margin_bottom( 10 )

        self.line_numbers_view.props.left_margin = 10
        self.line_numbers_view.props.right_margin = 10
        self.line_numbers_view.props.pixels_above_lines = 3
        self.line_numbers_view.props.pixels_below_lines = 3

        box = Gtk.Grid()
        box.set_vexpand( True )
        box.set_name( 'gutter-box' )
        box.attach( self.line_numbers_view, 0, 0, 1, 1 )

        self.editor_view.set_hexpand( True )
        self.editor_view.set_vexpand( True )
        self.editor_view.set_margin_top( 10 )
        self.editor_view.set_margin_bottom( 10 )

        self.editor_view.props.left_margin = 25
        self.editor_view.props.right_margin = 10
        self.editor_view.props.pixels_above_lines = 3
        self.editor_view.props.pixels_below_lines = 3

        grid.set_name( 'editor-grid' )
        grid.attach( box, 0, 0, 1, 1 )
        grid.attach( self.editor_view, 1, 0, 1, 1 )

        self.add( grid )

    def show_line_numbers( self ):
        n = self.editor_buffer.get_line_count()
        w = int( log10( n ) ) + 1
        s = '\n'.join( [ ( '{: >' + str( w ) + '}' ).format( i ) for i in range( 0, n ) ] )
        self.line_numbers_buffer.set_text( s )

    # Contents operations
    def get_contents( self ):
        start, end = self.editor_buffer.get_bounds()
        return self.editor_buffer.get_text( start, end, False )

    def set_contents( self, text ):
        self.suspend_change = True
        self.clear_tags()
        self.editor_buffer.set_text( text )
        self.suspend_change = False
        self.show_line_numbers()

    def is_content_changed( self ):
        return self.editor_buffer.get_modified()

    def clear_tags( self ):
        start, end = self.editor_buffer.get_bounds()
        self.editor_buffer.remove_all_tags( start, end )

    # Undo and redo operations
    def make_undo( self ):
        if not self.undo_stack: return

        change = self.undo_stack.pop()
        start = self.decode_iter( change[ 'start' ] )

        self.suspend_change = True

        if change[ 'type' ] == 'insert':
            end = self.decode_iter( change[ 'end' ] )
            self.editor_buffer.delete( start, end )
        else:
            self.editor_buffer.insert( start, change[ 'content' ], change[ 'length' ] )

        self.suspend_change = False
        self.show_line_numbers()

        self.redo_stack.append( change )

    def make_redo( self ):
        if not self.redo_stack: return

        change = self.redo_stack.pop()
        start = self.decode_iter( change[ 'start' ] )

        self.suspend_change = True

        if change[ 'type' ] == 'insert':
            self.editor_buffer.insert( start, change[ 'content' ], change[ 'length' ] )
        else:
            end = self.decode_iter( change[ 'end' ] )
            self.editor_buffer.delete( start, end )

        self.suspend_change = False

        self.show_line_numbers()

        self.undo_stack.append( change )

    # File operations
    def load_from_file( self, filename ):
        with open( filename, 'r' ) as f:
            self.set_contents( f.read() )
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.editor_buffer.set_modified( False )

    def save_to_file( self, filename ):
        with open( filename, 'w' ) as f:
            f.write( self.get_contents() )
            self.editor_buffer.set_modified( False )

    def create_new_file( self ):
        self.suspend_change = True

        self.clear_tags()
        self.editor_buffer.set_text( '' )
        self.undo_stack.clear()
        self.redo_stack.clear()

        self.suspend_change = False

        self.editor_buffer.set_modified( False )
        self.show_line_numbers()

    # Highlight operation
    def line_highlight( self, num ):
        pass

    def highlight_all( self ):
        pass

    # Events
    def on_change( self, buffer ):
        if self.suspend_change: return

        self.parent.on_editor_contents_changed()

        if self.last_change[ 'type' ] == 'insert':
            self.last_change[ 'end' ] = self.encode_iter( self.editor_buffer.get_iter_at_mark(
                self.editor_buffer.get_insert() ) )

        self.undo_stack.append( deepcopy( self.last_change ) )
        self.show_line_numbers()

    def on_insert( self, buffer, iter, content, length ):
        self.last_change = { 'type' : 'insert', 'start' : self.encode_iter( iter ),
            'content' : content, 'length' : length }

    def on_delete( self, buffer, start, end ):
        content = buffer.get_text( start, end, False )
        self.last_change = { 'type' : 'delete', 'start' : self.encode_iter( start ),
            'content' : content, 'length' : len( content ), 'end' : self.encode_iter( end ) }


    # Helpers
    def encode_iter( self, iter ):
        return ( iter.get_line(), iter.get_line_offset() )

    def decode_iter( self, enc_iter ):
        a, b = enc_iter
        return self.editor_buffer.get_iter_at_line_offset( a, b )
