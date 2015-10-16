import yaml
import os.path

from gi.repository import Gtk, Gio, Gdk, Pango
from editor import Editor
from console import Console
from assembler import assemble
from simulator_view import SimulatorView

class pyFriscApplication( Gtk.Application ):

    config = {}

    window = None
    hb = Gtk.HeaderBar()
    paned = Gtk.Paned()
    tabs = Gtk.Notebook()
    menu = Gtk.Menu()

    def __init__( self ):
        Gtk.Application.__init__( self, application_id = "org.pyFrisc.IDE" )
        self.connect( "activate", self.on_activate )

        self.load_config()

        self.editor = Editor( self, self.config )
        self.console = Console( self, self.config )
        self.simulator = SimulatorView( self, self.console, self.config )

    # GUI operations
    def init_header( self ):
        self.hb.set_show_close_button( True )
        self.hb.props.title = self.config[ 'file_name' ]
        self.hb.props.subtitle = "PyFrisc FRISC Assembler IDE"
        self.window.set_titlebar( self.hb )

        lbox = Gtk.Box( spacing = 5 )
        openButton = Gtk.Button( "Open" )
        saveButton = Gtk.Button()
        saveButton.set_tooltip_text( 'Save file' )
        saveAsButton = Gtk.Button()
        saveAsButton.set_tooltip_text( 'Save as...' )
        newButton = Gtk.Button()
        newButton.set_tooltip_text( 'Create a new file' )

        openButton.connect( 'clicked', self.on_open_click )
        newButton.connect( 'clicked', self.on_new_click )
        saveButton.connect( 'clicked', self.on_save_click )

        icon = Gio.ThemedIcon( name = "document-new" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        newButton.add( image )

        icon = Gio.ThemedIcon( name = "document-save-symbolic" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        saveButton.add( image )

        lbox.pack_start( openButton, True, True, 0 )
        lbox.pack_start( newButton, True, True, 0 )
        lbox.pack_start( saveButton, True, True, 0 )

        self.hb.pack_start( lbox )

        rbox = Gtk.Box( spacing = 5 )
        assembleButton = Gtk.Button()
        assembleButton.set_tooltip_text( 'Assemble source' )
        runButton = Gtk.Button()
        runButton.set_tooltip_text( 'Run simulation' )
        runButton.set_sensitive( False )

        self.assembleButton = assembleButton
        self.runButton = runButton

        optionsButton = Gtk.MenuButton()
        optionsButton.set_tooltip_text( 'Options' )

        optionsButton.set_popup( self.menu )

        icon = Gio.ThemedIcon( name = "system-run" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        assembleButton.add( image )

        icon = Gio.ThemedIcon( name = "media-playback-start" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        runButton.add( image )

        icon = Gio.ThemedIcon( name = "view-list-details" )
        image = Gtk.Image.new_from_gicon( icon, Gtk.IconSize.BUTTON )
        optionsButton.add( image )
        optionsButton.set_relief( Gtk.ReliefStyle.NONE )

        assembleButton.connect( 'clicked', self.on_assemble_click )
        runButton.connect( 'clicked', self.on_run_click )

        rbox.pack_start( assembleButton, True, True, 0 )
        rbox.pack_start( runButton, True, True, 0 )
        rbox.pack_start( optionsButton, True, True, 0 )

        self.hb.pack_end( rbox )

    def init_menu( self ):
        self.add_menu_item( 'New', 'Ctrl-N', self.on_new_click )
        self.add_menu_item( 'Open', 'Ctrl-O', self.on_open_click )
        self.menu.append( Gtk.SeparatorMenuItem() )
        self.add_menu_item( 'Reload', 'Ctrl-R', self.on_reload_click )
        self.add_menu_item( 'Save', 'Ctrl-S', self.on_save_click )
        self.add_menu_item( 'Save As...', 'Ctrl-Shift-S', self.on_save_as_click )
        self.menu.append( Gtk.SeparatorMenuItem() )
        self.add_menu_item( 'Undo', 'Ctrl-Z', self.on_undo )
        self.add_menu_item( 'Redo', 'Ctrl-Y', self.on_redo )
        #self.menu.append( Gtk.SeparatorMenuItem() )
        #self.add_menu_item( 'Find...', 'Ctrl-F', self.on_find_click )
        #self.add_menu_item( 'Search and Replace...', 'Ctrl-H', self.on_search_replace_click )
        self.menu.append( Gtk.SeparatorMenuItem() )
        self.add_menu_item( 'Settings', '', self.on_settings_click )
        self.menu.append( Gtk.SeparatorMenuItem() )
        self.add_menu_item( 'About', '', self.on_about_click )
        self.menu.set_name( 'main-menu' )
        self.menu.show_all()
        self.menu.set_halign( Gtk.Align.END )


    def init_contents( self ):
        l1 = Gtk.Label( 'Source' )
        l1.set_name( 'tab-label' )
        self.tabs.append_page( self.editor, l1 )

        l2 = Gtk.Label( 'Simulator')
        l2.set_name( 'tab-label' )
        self.tabs.append_page( self.simulator, l2 )

        self.tabs.set_name( 'views' )
        self.tabs.connect( 'switch-page', self.on_tab_change )

        self.paned.set_orientation( Gtk.Orientation.VERTICAL )
        self.paned.add1( self.tabs )
        self.paned.add2( self.console )
        self.paned.set_position( 450 )

        self.window.add( self.paned )

    def add_menu_item( self, text, shortcut, handler = None, icon = None ):
        mi = Gtk.MenuItem()
        g = Gtk.Grid()
        l = Gtk.Label( text )
        s = Gtk.Label( shortcut )

        l.set_hexpand( True )
        l.set_halign( Gtk.Align.START )
        l.set_name( 'menu-item-name' )
        s.set_name( 'menu-item-shortcut' )

        g.set_column_spacing( 40 )
        g.attach( l, 0, 0, 1, 1 )
        g.attach( s, 1, 0, 1, 1 )

        mi.add( g )

        if handler:
            mi.connect( 'activate', handler )

        self.menu.append( mi )

    # Application events
    def on_activate( self, data ):
        self.window = Gtk.ApplicationWindow( title = "pyFRISC IDE", type = Gtk.WindowType.TOPLEVEL )
        self.window.set_name( 'app-window' )
        self.window.set_border_width( 4 )
        self.window.set_default_size( 1080, 700 )
        self.window.set_icon_from_file( 'resources/icon.png' )

        self.window.connect( 'delete-event', self.on_quit )
        self.window.connect( 'key-press-event', self.on_keypress )
        #self.window.connect( 'check-resize', self.on_resize )

        self.init_menu()
        self.init_header()
        self.init_contents()

        self.add_window( self.window )

        style_provider = Gtk.CssProvider()
        style_provider.load_from_path( './resources/styles.css' )

        Gtk.StyleContext.add_provider_for_screen( Gdk.Screen.get_default(), style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION )

        self.window.show_all()
        self.console.show_message( 'pyFRISC IDE started.', 'info' )
        self.initial_open()

    def on_quit( self, window, event ):
        if self.editor.is_content_changed():
            self.show_ask_save_changes_dialog()

        self.store_config()

    # TODO: Change console size on maximize only
    def on_state_change( self, element, window ):
        w, h = self.window.get_size()
        print( w, h )
        self.paned.set_position( h - 300 )
        #print( element, window )

    # Button events
    def on_open_click( self, element ):
        self.open_file()

    def on_new_click( self, element ):
        self.new_file()

    def on_save_click( self, element ):
        self.save_file()

    def on_save_as_click( self, element ):
        self.save_file_as()

    def on_assemble_click( self, element ):
        if not self.config[ 'file_exists' ] or self.editor.is_content_changed():
            self.show_ask_save_changes_dialog()

        self.console.show_message( 'Assembling...' )
        ret, success = assemble( self.config[ 'file_name' ] )
        self.console.show_message( ret, 'success' if success else 'error' )
        if success:
            self.assembleButton.set_sensitive( False )
            self.runButton.set_sensitive( True )

    def on_run_click( self, element ):
        self.run_simulator()

    def on_about_click( self, element ):
        self.show_about_dialog()

    def on_settings_click( self, element ):
        pass

    def on_reload_click( self, element ):
        self.reload_file()

    def on_undo( self, element ):
        self.editor.make_undo()

    def on_redo( self, element ):
        self.editor.make_redo()

    def on_find_click( self, element ):
        pass

    def on_search_replace_click( self, element ):
        pass

    # Other events
    def on_tab_change( self, notebook, page, page_num ):
        old_active_label = notebook.get_tab_label( notebook.get_nth_page( self.config[ 'tab_index' ] ) )
        new_active_label = notebook.get_tab_label( page )
        old_active_label.set_name( 'tab-label' )
        new_active_label.set_name( 'tab-label-active' )
        self.config[ 'tab_index' ] = page_num

    def on_keypress( self, widget, event ):
        if event.state & Gdk.ModifierType.CONTROL_MASK:
            if event.state & Gdk.ModifierType.SHIFT_MASK:
                if event.keyval == ord( 'Z' ):
                    self.editor.make_redo()
                elif event.keyval == ord( 'S' ):
                    self.save_file_as()
            else:
                if event.keyval == ord( 'z' ):
                    self.editor.make_undo()
                elif event.keyval == ord( 'y' ):
                    self.editor.make_redo()
                elif event.keyval == ord( 's' ):
                    self.save_file()
                elif event.keyval == ord( 'n' ):
                    self.new_file()
                elif event.keyval == ord( 'o' ):
                    self.open_file()
                elif event.keyval == ord( 'r' ):
                    self.reload_file()

    def on_editor_contents_changed( self ):
        self.hb.props.title = '*' + self.config[ 'file_name' ]
        self.runButton.set_sensitive( False )
        self.assembleButton.set_sensitive( True )

    # Simulator operations
    def run_simulator( self ):
        asm_file = self.config[ 'file_name' ]
        mc_file = asm_file.rsplit( '.', maxsplit = 1 )[ 0 ] + '.p'
        self.simulator.load_simulator( mc_file )
        self.tabs.set_current_page( 1 )
        self.console.show_message( 'Frisc simulator loaded.', 'info' )

    # def terminate_simulator( self ):
    #     pass

    # File operations
    def new_file( self ):
        if self.editor.is_content_changed():
            self.show_ask_save_changes_dialog()

        self.editor.create_new_file()
        self.config[ 'file_name' ] = 'Untitled'
        self.config[ 'file_exists' ] = False
        self.hb.props.title = 'Untitled'
        self.console.show_message( 'New file created.' )
        self.runButton.set_sensitive( False )

    def save_file( self ):
        if not self.config[ 'file_exists' ]:
            self.save_file_as()
        else:
            self.editor.save_to_file( self.config[ 'file_name' ] )
            self.console.show_message( 'File {} successfully saved.'.format(
                self.config[ 'file_name' ] ) )
            self.hb.props.title = self.config[ 'file_name' ]

    def save_file_as( self ):
        dialog = self.get_save_as_dialog()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.editor.save_to_file( filename )
            self.config[ 'file_name' ] = filename
            self.config[ 'file_exists' ] = True
            self.hb.props.title = filename
            self.console.show_message( 'File {} successfully saved.'.format(
                self.config[ 'file_name' ] ) )

        dialog.destroy()

    def open_file( self ):
        if self.editor.is_content_changed():
            self.show_ask_save_changes_dialog()

        dialog = self.get_open_dialog()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()
            self.editor.load_from_file( filename )
            self.config[ 'file_name' ] = filename
            self.config[ 'file_exists' ] = True
            self.hb.props.title = filename
            self.console.show_message( 'File {} loaded.'.format(
                self.config[ 'file_name' ] ) )
            self.assembleButton.set_sensitive( True )
            self.runButton.set_sensitive( False )

        dialog.destroy()

    def reload_file( self ):
        self.editor.load_from_file( self.config[ 'file_name' ] )
        self.console.show_message( 'File {} reloaded.'.format(
            self.config[ 'file_name' ] ) )

    def initial_open( self ):
        if self.config[ 'file_exists' ]:
            self.editor.load_from_file( self.config[ 'file_name' ] )
            self.console.show_message( 'File {} loaded.'.format(
                self.config[ 'file_name' ] ) )

    # Config operations
    def load_config( self ):
        with open( 'config/config.yaml', 'r' ) as f:
            self.config = yaml.load( f.read() )

    def store_config( self ):
        with open( 'config/config.yaml', 'w' ) as f:
            f.write( yaml.dump( self.config ) )

    # Dialog operations
    def get_save_as_dialog( self ):
        return Gtk.FileChooserDialog( 'Save file as', self.window,
            Gtk.FileChooserAction.SAVE,
            ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK ) )


    def get_open_dialog( self ):
        dialog = Gtk.FileChooserDialog( "Please choose a file", self.window,
            Gtk.FileChooserAction.OPEN,
            ( Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK ) )

        f1 = Gtk.FileFilter()
        f1.set_name( 'FRISC assembly source code' )
        f1.add_pattern( '*.a' )

        dialog.add_filter( f1 )

        f1 = Gtk.FileFilter()
        f1.set_name( 'Plain text file' )
        f1.add_mime_type( 'text/plain' )

        dialog.add_filter( f1 )

        f1 = Gtk.FileFilter()
        f1.set_name( 'Any files' )
        f1.add_pattern( '*' )

        dialog.add_filter( f1 )

        return dialog

    def show_ask_save_changes_dialog( self ):
        if self.config[ 'file_exists' ]:
            msg1 = 'Save changes to ' + self.config[ 'file_name' ] + '?'
            msg2 = 'If you don\'t save this file, all the changes will be lost.'
        else:
            msg1 = 'Save contents of Untitled?'
            msg2 = 'The contents of this file aren\'t saved yet.'

        dialog = Gtk.MessageDialog( self.window, 0, Gtk.MessageType.WARNING,
            Gtk.ButtonsType.YES_NO, msg1 )

        dialog.format_secondary_text( msg2 )
        dialog.set_name( 'save-dialog' )

        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            if self.config[ 'file_exists' ]:
                self.save_file()
            else:
                self.save_file_as()

        dialog.destroy()

    def show_settings_dialog( self ):
        pass

    def show_about_dialog( self ):
        dialog = Gtk.Dialog( 'About', self.window, 0 )

        dialog.set_name( 'about-dialog' )
        dialog.set_default_size( 500, 200 )

        dialog.add_button( 'Close', Gtk.ResponseType.OK )

        content_area = dialog.get_content_area()

        grid = Gtk.Grid()
        grid.set_name( 'about-grid' )

        image = Gtk.Image.new_from_file( 'resources/large.png' )
        image.set_name( 'about-image' )
        grid.attach( image, 0, 0, 1, 1 )

        box = Gtk.VBox()

        title = Gtk.Label( 'pyFrisc IDE' )
        title.set_name( 'about-title' )
        title.set_halign( Gtk.Align.START )
        box.pack_start( title, False, False, 0 )

        author = Gtk.Label( 'Zvonimir Jurelinac, 2015.' )
        author.set_name( 'about-author' )
        author.set_halign( Gtk.Align.START )
        box.pack_start( author, False, False, 0 )

        descr = Gtk.Label()
        descr.set_markup( '''<b>pyFrisc IDE</b> is an <i>integrated development environment</i> for
programming FRISC processors. It comes with a text editor,
code assembler and FRISC simulator.''' )
        descr.set_name( 'about-descr' )
        descr.set_halign( Gtk.Align.START )
        box.pack_start( descr, False, False, 0 )

        discl = Gtk.Label()
        discl.set_markup( 'FRISC is a simple RISC processor developed at <b>FER, University of Zagreb.</b>' )
        discl.set_name( 'about-discl' )
        discl.set_halign( Gtk.Align.START )
        box.pack_start( discl, False, False, 0 )

        grid.attach( box, 1, 0, 1, 1 )

        content_area.add( grid )

        dialog.show_all()
        dialog.run()
        dialog.destroy()


app = pyFriscApplication()
app.run( None )
