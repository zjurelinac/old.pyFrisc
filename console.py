from gi.repository import Gtk, Gio, Gdk, Pango

class Console( Gtk.ScrolledWindow ):

    buffer = Gtk.TextBuffer()
    view = Gtk.TextView()
    tags = {}

    def __init__( self, config ):
        Gtk.ScrolledWindow.__init__( self )

        self.view.set_buffer( self.buffer )
        self.set_name( 'console-wrapper' )

        self.init_interface()

        self.tags[ 'error' ] = self.buffer.create_tag( 'error', foreground = '#FF5D38', weight = Pango.Weight.BOLD )
        self.tags[ 'info' ] = self.buffer.create_tag( 'info', foreground = '#268BD2' )
        self.tags[ 'success' ] = self.buffer.create_tag( 'success', foreground = '#BCD42A' )
        self.tags[ 'message' ] = self.buffer.create_tag( 'message', foreground = '#aaa' )

    # GUI operations
    def init_interface( self ):
        box = Gtk.Grid()

        box.set_name( 'console-box' )
        box.set_border_width( 10 )

        self.view.set_name( 'console' )
        self.view.set_editable( False )
        self.view.set_cursor_visible( False )
        self.view.props.pixels_above_lines = 3
        self.view.props.pixels_below_lines = 3

        box.attach( self.view, 0, 0, 1, 1 )
        self.add( box )

    # Console operations
    def show_message( self, text, message_type = 'message' ):
        if message_type not in self.tags:
            message_type = 'message'

        start, end = self.buffer.get_bounds()

        end_line = end.get_line() + 2

        if start.compare( end ) != 0:
            text = '\n' + text
            end_line -= 1

        self.buffer.insert( end, text, -1 )

        iter1 = self.buffer.get_iter_at_line( end_line )
        iter2 = self.buffer.get_end_iter()

        self.buffer.apply_tag_by_name( message_type, iter1, iter2 )

    def clear_all( self ):
        start, end = self.buffer.get_bounds()
        self.buffer.remove_all_tags( start, end )
        self.buffer.set_text( '' )
