import yaml
import time

from gi.repository import Gtk, Gio, Gdk, Pango
from simulator import FRISCProcessor
from utils import *

# TODO: Search / go to line custom function
class SimulatorView( Gtk.Grid ):

    memoryModel = Gtk.ListStore( str, str, str, int, str )
    program = ''
    memoryState = []
    flags = { 'paused' : False, 'stopped' : True }

    def __init__( self, parent, console, config ):
        Gtk.Grid.__init__( self )

        self.parent = parent
        self.console = console

        self.set_name( 'simulator-grid' )

        self.simulator = FRISCProcessor( 65536 // 4 )     # TODO: Increase later, or on demand - place in settings

        self.init_options()
        self.init_goto_line()
        self.init_memory_display()
        self.init_registers_display()

    def init_options( self ):
        optionsBox = Gtk.ButtonBox()
        optionsBox.set_orientation( Gtk.Orientation.VERTICAL )
        optionsBox.set_layout( Gtk.ButtonBoxStyle.START )

        optionsBox.set_name( 'options-box' )
        optionsBox.set_margin_left( 20 )
        optionsBox.set_margin_right( 20 )

        reloadButton = Gtk.Button( 'Reload' )
        icon = Gio.ThemedIcon( name = "reload" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        reloadButton.set_image( image )
        reloadButton.set_always_show_image( True )
        reloadButton.set_alignment( 0.0, 0.5 )

        runButton = Gtk.Button( 'Run' )
        icon = Gio.ThemedIcon( name = "media-playback-start" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        runButton.set_image( image )
        runButton.set_always_show_image( True )
        runButton.set_alignment( 0.0, 0.5 )

        stepButton = Gtk.Button( 'Step' )
        icon = Gio.ThemedIcon( name = "next" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        stepButton.set_image( image )
        stepButton.set_always_show_image( True )
        stepButton.set_alignment( 0.0, 0.5 )

        pauseButton = Gtk.Button( 'Pause' )
        icon = Gio.ThemedIcon( name = "media-playback-pause" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        pauseButton.set_image( image )
        pauseButton.set_always_show_image( True )
        pauseButton.set_alignment( 0.0, 0.5 )

        stopButton = Gtk.Button( 'Stop' )
        icon = Gio.ThemedIcon( name = "media-playback-stop" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        stopButton.set_image( image )
        stopButton.set_always_show_image( True )
        stopButton.set_alignment( 0.0, 0.5 )

        reloadButton.connect( 'clicked', self.on_reload_click )
        runButton.connect( 'clicked', self.on_run_click )
        stepButton.connect( 'clicked', self.on_step_click )
        pauseButton.connect( 'clicked', self.on_pause_click )
        stopButton.connect( 'clicked', self.on_stop_click )

        self.reloadButton = reloadButton
        self.runButton = runButton
        self.stepButton = stepButton
        self.pauseButton = pauseButton
        self.stopButton = stopButton

        optionsBox.pack_start( reloadButton, True, True, 0 )
        optionsBox.pack_start( runButton, True, True, 0 )
        optionsBox.pack_start( stepButton, True, True, 0 )
        optionsBox.pack_start( pauseButton, True, True, 0 )
        optionsBox.pack_start( stopButton, True, True, 0 )

        self.attach( optionsBox, 0, 1, 1, 2 )

    def init_memory_display( self ):
        self.memoryView = Gtk.TreeView( self.memoryModel )
        self.memoryView.set_name( 'memory-view' )
        self.memoryView.connect( 'row-activated', self.on_row_dblclick )
        self.memoryView.set_headers_visible( False )

        self.memorySelection = self.memoryView.get_selection()

        self.memoryView.set_search_column( 1 )
        self.memoryView.set_search_entry( self.searchEntry )
        self.memoryView.set_enable_search( True )

        rendererBrkPt = Gtk.CellRendererText()
        rendererBrkPt.set_padding( 10, 5 )
        rendererBrkPt.props.foreground = '#F83F4C'
        self.memoryView.append_column( Gtk.TreeViewColumn( 'Breakpoint', rendererBrkPt, text = 0 ) )

        rendererAdr = Gtk.CellRendererText()
        rendererAdr.set_padding( 10, 5 )
        rendererAdr.props.font = 'bold'
        self.memoryView.append_column( Gtk.TreeViewColumn( 'Address', rendererAdr, text = 1 ) )

        rendererContX = Gtk.CellRendererText()
        rendererContX.set_padding( 20, 5 )
        self.memoryView.append_column( Gtk.TreeViewColumn( 'Contents (HEX)', rendererContX, text = 2 ) )

        rendererContD = Gtk.CellRendererText()
        rendererContD.set_padding( 20, 5 )
        self.memoryView.append_column( Gtk.TreeViewColumn( 'Contents (DEC)', rendererContD, text = 3 ) )

        rendererAnn = Gtk.CellRendererText()
        rendererAnn.set_padding( 10, 5 )
        rendererAnn.props.foreground = '#888'
        rendererAnn.props.font = 'bold'
        self.memoryView.append_column( Gtk.TreeViewColumn( 'Source Code', rendererAnn, text = 4 ) )

        scrollBox = Gtk.ScrolledWindow()
        scrollBox.set_hexpand( True )
        scrollBox.set_vexpand( True )
        scrollBox.add( self.memoryView )

        self.attach( scrollBox, 1, 1, 1, 1 )

    def init_registers_display( self ):
        registerGrid = Gtk.Grid()
        registerGrid.set_margin_left( 20 )
        registerGrid.set_margin_right( 20 )
        registerGrid.set_name( 'register-grid' )
        self.registerDisplays = []

        for i in range( 0, 10 ):
            box = Gtk.HBox()
            box.set_name( 'register-box' )

            if i == 8:
                box.set_name( 'pc-box' )

            box.set_margin_bottom( 1 )

            label = Gtk.Label( self.simulator.get_register( i ) )
            label.set_name( 'register-value' )
            self.registerDisplays.append( label )

            name = Gtk.Label( FRISCProcessor.get_register_name( i ) )
            name.set_name( 'register-name' )
            name.set_width_chars( 5 )

            box.pack_start( name, True, True, 0 )
            box.pack_start( self.registerDisplays[ i ], True, True, 0 )
            registerGrid.attach( box, 0, i, 1, 1 )

        self.attach( registerGrid, 2, 1, 1, 2 )

    def init_goto_line( self ):
        box = Gtk.Box()
        box.set_orientation( Gtk.Orientation.HORIZONTAL )
        box.set_border_width( 10 )

        label = Gtk.Label( 'Go to line:' )
        label.set_name( 'goto-label' )
        self.searchEntry = Gtk.SearchEntry()
        self.searchEntry.set_text( '00000000' )
        self.searchEntry.connect( 'search-changed', self.on_search )

        box.pack_start( label, False, False, 0 )
        box.pack_start( self.searchEntry, True, True, 0 )

        self.attach( box, 1, 0, 1, 1 )


    def load_simulator( self, file ):
        self.program = file
        self.simulator.load_program( file )
        self.memoryModel.clear()
        self.memoryState = []

        for i in range( 0, self.simulator.MEM_SIZE // 4 ):
            self.memoryState.append( {
                'line' : '{:0>8X}'.format( 4*i ),
                'contents' : self.simulator.get_word_from_mem( 4*i ),
                'breakpoint' : False,
                'annotation' : self.simulator.annotations[ 4*i ] } )

        for l in self.memoryState:
            self.memoryModel.append( self.get_memory_model_values( l ) )


    def on_reload_click( self, element ):
        pass

    def on_run_click( self, element ):
        if self.is_paused(): self.flags[ 'paused' ] = False

        self.runButton.set_sensitive( False )
        self.pauseButton.set_sensitive( True )

        while not self.is_breakpoint() and not self.is_paused() and self.run_step():
            while Gtk.events_pending():
                Gtk.main_iteration()
            time.sleep( 0.25 )
            print('iteration')

        self.runButton.set_sensitive( True )

    def on_step_click( self, element ):
        self.run_step()

    def on_pause_click( self, element ):
        self.flags[ 'paused' ] = True
        self.pauseButton.set_sensitive( False )
        self.runButton.set_sensitive( True )

    def on_stop_click( self, element ):
        pass

    def on_row_dblclick( self, t, p, c ):
        i = int( p.to_string() )
        self.toggle_breakpoint( p, i )

    def on_search( self, element ):
        return True

    def run_step( self ):
        ret = True

        try:
            self.simulator.run_step()

            self.update_registers()
            self.select_active_row()

            if self.simulator.last_changed_address != -1:
                self.update_memory( self.simulator.last_changed_address )
                self.simulator.last_changed_address = -1

        except Exception as e:
            self.console.show_message( str( e ), 'error' )
            # TODO: What to do on error?
            ret = False

        return ret

    def clear_simulator( self ):
        pass

    def update_memory( self, i ):
        c = self.memoryState[ i ][ 'contents' ] = self.simulator.get_word_from_mem( 4*( i // 4 ) )
        it = self.memoryModel.get_iter_from_string( str( i // 4 ) )
        self.memoryModel.set( it, [ 2, 3 ], [ bin_to_pretty_hex( c ), from32( c ) ] )

    def update_registers( self ):
        for i in range( 0, 10 ):
            self.registerDisplays[ i ].set_text( self.simulator.get_register( i ) )

    def select_active_row( self ):
        pc = self.simulator.get_program_counter()
        it = self.memoryModel.get_iter_from_string( str( pc // 4 - 1 ) )
        self.memorySelection.select_iter( it )

    def toggle_breakpoint( self, p, i ):
        self.memoryState[ i ][ 'breakpoint' ] = not self.memoryState[ i ][ 'breakpoint' ]
        self.memoryModel.set_value( self.memoryModel.get_iter( p ), 0,
            get_breakpoint_symbol( self.memoryState[ i ][ 'breakpoint' ] ) )

    def is_breakpoint( self ):
        return self.memoryState[ self.simulator.get_program_counter() // 4 ][ 'breakpoint' ]

    def is_paused( self ):
        return self.flags[ 'paused' ]

    def get_memory_model_values( self, l ):
        return [ get_breakpoint_symbol( l[ 'breakpoint' ] ), l[ 'line' ],
            bin_to_pretty_hex( l[ 'contents' ] ), from32( l[ 'contents' ]),
            l[ 'annotation' ] ]
