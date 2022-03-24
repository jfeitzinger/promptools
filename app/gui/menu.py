# top menu bar here. TODO: need to rework these menus as they have little to
# do with the current hierarchy of the app (not to mention no attached
# functions on most things).

import tkinter as tk
import logging

from gui.preferences import PreferencesWindow
from gui.transposer import TransposerWindow
from gui.library import LibraryWindow

class MenuBar(tk.Frame):
    """Class for Menu options."""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent.frame)

        # TODO: thin this out...
        self.parent = parent
        self.app = parent
        self.frame = parent.frame
        self.settings = self.app.settings
        self.setlist = self.app.collections.setlist
        self.data = self.app.data

        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        # PrompTools menu
        promptools_menu = tk.Menu(menu_bar)
        # promptools_menu.add_cascade(label="Preferences", menu=preferences_menu)
        # promptools_menu.add_separator()

        # workspace cascade
        workspace_menu = tk.Menu(menu_bar)
        workspace_menu.add_command(label="Save")
        workspace_menu.add_command(label="Save As...")
        workspace_menu.add_command(label="Load")
        workspace_menu.add_separator()
        workspace_menu.add_command(label="Clear") # TODO: new as well?
        workspace_menu.add_command(label="Reload")
        workspace_menu.add_separator()
        workspace_menu.add_checkbutton(label="Auto-Save On Exit")
        # reload settings, 
        workspace_menu.add_checkbutton(label="Reload At Startup")

        # setlist cascade
        setlist_submenu = tk.Menu(menu_bar)
        setlist_submenu.add_command(label="Save")
        setlist_submenu.add_command(label="Save As...")
        setlist_submenu.add_command(label="Load")
        setlist_submenu.add_separator()
        setlist_submenu.add_command(label="New")
        setlist_submenu.add_command(label="Reload")
        setlist_submenu.add_separator()
        setlist_submenu.add_checkbutton(label="Auto-Save On Exit")
        setlist_submenu.add_checkbutton(label="Save With Workspace")    

        # file menu contents
        file_menu = tk.Menu(menu_bar)
        file_menu.add_command(label="New Song")
        file_menu.add_command(label="Reload Song")
        file_menu.add_separator()

        # main functions for shuttling songs around the app!
        file_menu.add_command(label="Add Song To Pool", accelerator="Cmd+o", command=self.on_add_song_to_pool)
        self.app.bind_all("<Command-o>", lambda _: self.on_add_song_to_pool())
        file_menu.add_command(label="Add Song To Setlist", accelerator="Cmd+l", command=self.on_add_song_to_setlist)
        self.app.bind_all("<Command-l>", lambda _: self.on_add_song_to_setlist())
        file_menu.add_command(label="Load Cued To Live", accelerator="Cmd+p", command=self.on_load_cued_to_live)
        self.app.bind_all("<Command-p>", lambda event: self.on_load_cued_to_live(event))

        file_menu.add_separator()        
        file_menu.add_command(label="Import Song")
        file_menu.add_command(label="Export Song")
        file_menu.add_separator()
        # file_menu.add_cascade(label="Pool", menu=pool_menu)
        # file_menu.add_cascade(label="Setlist", menu=setlist_submenu)
        # file_menu.add_cascade(label="Workspace", menu=workspace_menu)
        # file_menu.add_separator()
        file_menu.add_command(label="Preferences", command=self.on_preferences)
        # file_menu.add_separator()
        # file_menu.add_command(label="About")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_exit)

        # text format menu
        text_menu = tk.Menu(menu_bar)
        text_menu.add_command(label='Clear Selected Style')
        text_menu.add_separator()
        text_menu.add_command(label='Bold')
        text_menu.add_command(label='Italic')
        text_menu.add_command(label='Underline')
        text_menu.add_command(label='Strikethru')
        text_menu.add_separator()
        # hide hides text from talent, appears grey in monitor
        text_menu.add_command(label='Hide') # TODO: combine into context sensitive toggle
        # show removes hide tags
        text_menu.add_command(label='Show')
        text_menu.add_separator()
        # remove all hide tags from document
        text_menu.add_command(label='Show All Text')
        text_menu.add_separator()
        text_menu.add_command(label='Clear All Style')
        text_menu.add_separator()
        # Bring up menu to configure font size & typeface.
        # text_menu.add_command(label='Text Settings')

        # tag menu
        tag_menu = tk.Menu(menu_bar)
        tag_menu.add_command(label='Clear Selected Tags')
        tag_menu.add_separator()
        tag_menu.add_command(label='BVs')
        tag_menu.add_command(label='Chord')
        tag_menu.add_command(label='Header')
        tag_menu.add_command(label='Key')
        tag_menu.add_command(label='Lyric')
        tag_menu.add_separator()
        # Operator tagged items take up space in both views but are only visible to operator
        tag_menu.add_command(label='Operator')
        tag_menu.add_separator()
        tag_menu.add_command(label='Configure Colors')
        tag_menu.add_separator()
        tag_menu.add_command(label='Clear All Tags')

        guest_menu = tk.Menu(menu_bar)
        guest_menu.add_command(label='All Guests')
        guest_menu.add_separator()
        guest_menu.add_command(label='(guests go here)')
        guest_menu.add_separator()
        guest_menu.add_command(label='Manage Guestlist')
        # special menu for variable data
        special_menu = tk.Menu(menu_bar)
        special_menu.add_command(label="City")
        special_menu.add_command(label="Date")
        special_menu.add_cascade(label="Guests", menu=guest_menu) # TODO: cascade menu of guest list.
        special_menu.add_command(label="Thanks")
        special_menu.add_command(label="Venue")

        # edit menu contents
        edit_toggle = self.settings.editor.enabled
        edit_menu = tk.Menu(menu_bar)
        edit_menu.add_checkbutton(label="Edit Mode", accelerator="Cmd+e", variable=edit_toggle, command=self.on_edit_mode) # TODO: context specific text
        edit_menu.add_separator()
        edit_menu.add_command(label="Undo")
        edit_menu.add_command(label="Redo")        
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut")
        edit_menu.add_command(label="Copy")
        edit_menu.add_command(label="Paste")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find And Replace") # TODO: popup find and replace tool

        # talent view menu
        self.talent_flag = tk.IntVar()
        talent_view_menu = tk.Menu(menu_bar)
        talent_view_menu.add_checkbutton(label="Normal", onvalue=0, variable=self.talent_flag, command=self.on_normal)
        talent_view_menu.add_checkbutton(label="Blank", onvalue=1, variable=self.talent_flag, command=self.on_blank)
        talent_view_menu.add_checkbutton(label="Freeze", onvalue=2, variable=self.talent_flag, command=self.on_freeze)
        talent_view_menu.add_checkbutton(label="Test", onvalue=3, variable=self.talent_flag, command=self.on_test)
        talent_view_menu.add_checkbutton(label="Hide", onvalue=4, variable=self.talent_flag, command=self.on_hide)
        # minimize window
        # talent_view_menu.add_separator()
        # talent_view_menu.add_command(label="Settings")
        # talent_view_menu.add_command(label="Game") # TODO: easter egg game

        # view menu contents
        view_menu = tk.Menu(menu_bar)
        view_menu.add_checkbutton(label="Talent Fullscreen", variable=self.settings.view.fullscreen)
        view_menu.add_cascade(label='Talent View', menu=talent_view_menu, command=lambda: print('opened talent view menu'))
        view_menu.add_separator()
        # dump the entire edit buffer to talent window to bypass unforseen errors in edit duplication
        view_menu.add_checkbutton(label='Push Edits To Talent') 
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Talent Follows Edit View")
        view_menu.add_checkbutton(label="Editor Follows Talent Scroll")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Show Talent Arrow")
        view_menu.add_checkbutton(label="Show Talent Colors")
        view_menu.add_checkbutton(label="Wrap Talent Text")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Lists & Helper Pane (Left)")
        view_menu.add_checkbutton(label="Details & Notes Pane (Right)")
        view_menu.add_checkbutton(label="Browser & Preview Pane (Below)")
        view_menu.add_separator()
        view_menu.add_command(label="Settings")

        # format menu contents
        format_menu = tk.Menu(menu_bar)
        format_menu.add_cascade(label='Tag', menu=tag_menu)
        format_menu.add_cascade(label='Style', menu=text_menu)
        format_menu.add_cascade(label='Special', menu=special_menu)
        format_menu.add_separator()
        format_menu.add_command(label='Sub Selected Enharmonics')
        format_menu.add_separator()
        format_menu.add_command(label='Text Size +')
        format_menu.add_command(label='Text Size -')
        format_menu.add_separator()
        format_menu.add_command(label='Clear Selected Formatting')
        format_menu.add_command(label='Clear All Formatting')
        format_menu.add_separator()
        format_menu.add_command(label="Settings")

        # library menu
        library_menu = tk.Menu(menu_bar)
        library_menu.add_command(label='Song Manager', command=lambda *args: self.open_library(tab='songs'))

        # gig menu. gig includes a list of setlists, and metadata about gig (venue, date, etc).
        # does not affect the pool
        gig_menu = tk.Menu(menu_bar)
        gig_menu.add_command(label="DUMP GIG (TEMP)", command=self.on_dump_gig)
        gig_menu.add_command(label="DUMP WORKSPACE", command=self.on_dump_workspace)
        gig_menu.add_command(label="LOAD WORKSPACE", command=self.on_load_workspace)
        gig_menu.add_command(label="Gig Name Here", state="disabled")
        gig_menu.add_separator()
        gig_menu.add_command(label="Gig Info")
        gig_menu.add_command(label="Setlists") # TODO: cascade?
        gig_menu.add_separator()
        gig_menu.add_command(label="Save")
        gig_menu.add_separator()
        gig_menu.add_command(label="Import")
        gig_menu.add_command(label="Export")
        gig_menu.add_separator()
        gig_menu.add_command(label="New")
        gig_menu.add_command(label="Reload")
        gig_menu.add_separator()
        gig_menu.add_command(label="Settings")


        # pool menu. pool is a working list of files
        pool_menu = tk.Menu(menu_bar)
        pool_menu.add_command(label="Save") # save state to db
        pool_menu.add_separator()
        pool_menu.add_command(label="Import")
        pool_menu.add_command(label="Export")
        pool_menu.add_separator()
        pool_menu.add_command(label="Clear") # reload state from db
        pool_menu.add_command(label="Reload")
        pool_menu.add_separator()
        pool_menu.add_command(label="Settings")

        # pool_menu.add_separator()
        # pool_menu.add_checkbutton(label="Auto-Save On Exit")
        # pool_menu.add_checkbutton(label="Save With Workspace")

        # setlist menu
        setlist_menu = tk.Menu(menu_bar)
        # These next two are for testing db functionality. will be removed
        setlist_menu.add_command(label="DUMP SETLIST (TEMP)", command=self.dump_setlist)
        setlist_menu.add_separator()
        setlist_menu.add_command(label="Metadata")        
        setlist_menu.add_separator()
        setlist_menu.add_command(label="Previous")
        setlist_menu.add_command(label="Next")
        setlist_menu.add_separator()
        setlist_menu.add_command(label="(Setlist songs go here)")
        setlist_menu.add_separator()

        # bookmark menu
        bookmark_menu = tk.Menu(menu_bar)
        bookmark_menu.add_command(label='Add Bookmark')
        bookmark_menu.add_separator()
        bookmark_menu.add_command(label='Previous')
        bookmark_menu.add_command(label='Next')
        bookmark_menu.add_separator()
        bookmark_menu.add_command(label='(Populate List of Bookmarks Here)')
        bookmark_menu.add_separator()
        bookmark_menu.add_command(label='Clear Bookmarks')
        bookmark_menu.add_separator()
        bookmark_menu.add_command(label='Bookmark Manager')

        # keys menu. TODO: used in two places but will need functions to act on different song objects. 
        keys_menu = tk.Menu(menu_bar)
        keys_menu.add_command(label='Default Song Key')
        keys_menu.add_separator()
        keys_menu.add_command(label='C')
        keys_menu.add_command(label='C# / Db')
        keys_menu.add_command(label='D')
        keys_menu.add_command(label='D# / Eb')
        keys_menu.add_command(label='E')
        keys_menu.add_command(label='F')
        keys_menu.add_command(label='F# / Gb')
        keys_menu.add_command(label='G')
        keys_menu.add_command(label='G# / Ab')
        keys_menu.add_command(label='A')
        keys_menu.add_command(label='A# / Bb')
        keys_menu.add_command(label='B')

        # transposer menu
        transposer_menu = tk.Menu(menu_bar)
        transposer_menu.add_command(label="Show Transposer Tool", command=self.on_transposer_open)
        transposer_menu.add_command(label="Close Transposer Tool", command=self.on_transposer_close)
        # transpose_menu.add_command(label="Persist")
        transposer_menu.add_separator()
        transposer_menu.add_checkbutton(label="Show Nashville Numbers")
        transposer_menu.add_separator()
        # transposer_menu.add_command(label="Substitute Enharmonics In Selection (A#<->Bb)")
        # transposer_menu.add_separator()
        # TODO: whichever of these you go into should raise a flag so transpose gets applied right
        transposer_menu.add_cascade(label="Transpose Current", menu=keys_menu) 
        transposer_menu.add_cascade(label="Transpose Cued", menu=keys_menu)
        transposer_menu.add_separator()


        # tool menu
        tool_menu = tk.Menu(menu_bar)
        tool_menu.add_cascade(label="Transposer", menu=transposer_menu, command=self.on_transposer_open)
        tool_menu.add_separator()
        tool_menu.add_command(label="Batch Processor", state="disabled") # launch batch file processor
        tool_menu.add_command(label="History", state="disabled")
        tool_menu.add_command(label="Debug Log", state="disabled")

        # build all the cascades last
        # menu_bar.add_cascade(label="Promptools", menu=promptools_menu)
        menu_bar.add_cascade(label="File", menu=file_menu)
        menu_bar.add_cascade(label="Edit", menu=edit_menu)
        menu_bar.add_cascade(label="Format", menu=format_menu)
        menu_bar.add_cascade(label="View", menu=view_menu)
        menu_bar.add_cascade(label="Library", menu=library_menu)
        menu_bar.add_cascade(label="Gig", menu=gig_menu)
        menu_bar.add_cascade(label="Pool", menu=pool_menu)        
        menu_bar.add_cascade(label="Setlist", menu=setlist_menu)
        menu_bar.add_cascade(label="Bookmarks", menu=bookmark_menu)
        menu_bar.add_cascade(label="Tools", menu=tool_menu)

    def open_library(self, tab:str):
        """Open Library window."""
        # TODO: implement open specific tabs
        logging.info('opened LibraryWindow from menu_bar')
        exists = self.settings.windows.library.get()
        self.app.library = LibraryWindow(self.app) if not exists else self.app.library
        self.app.library.lift() if exists else None

    def on_dump_gig(self):
        """TEMP function, dumps workspace/gig to db."""
        self.app.tools.dbmanager.dump_gig(self.app.data.gig, workspace=False)

    def on_load_gig(self):
        """TEMP function, reloads workspace/gig from db, overwriting whatever is loaded."""
        # TODO: prompt gig id
        self.app.tools.dbmanager.load_gig(gig_id=0)

    def on_dump_workspace(self):
        """Dump gig to the workspace slot."""
        self.app.tools.dbmanager.dump_gig(self.app.data.gig, workspace=True)

    def on_load_workspace(self):
        self.app.tools.dbmanager.load_gig(gig_id=0)

    def dump_setlist(self):
        """Temporary test function, dumps setlist collection to db."""
        self.app.tools.dbmanager.dump_setlist(self.app.data.setlists.live)

    def reload_setlist(self):
        """Temporary test function, recovers setlist colelction from db, overwriting current."""
        collection = self.app.data.setlist
        self.app.data.reload_collection_from_db(collection)

    def on_exit(self):
        self.app.quit_app()

    def on_talent_fullscreen(self):
        # TODO: fullscreen state can get decoupled from the checkbox, write in variable updates.
        self.app.talent.toggle_fullscreen()

    def on_preferences(self):
        if not self.app.settings.windows.preferences.get():
            PreferencesWindow(self)

    # functions for talent view cascade
    def on_normal(self):
        self.talent_flag.set(0)
        self.app.talent.deiconify()

    def on_blank(self):
        self.talent_flag.set(1)
        self.app.talent.deiconify()

    def on_freeze(self):
        self.talent_flag.set(2)
        # self.app.talent.deiconify()

    def on_test(self):
        self.talent_flag.set(3)
        self.app.talent.deiconify()

    def on_hide(self):
        self.talent_flag.set(4)
        self.app.talent.withdraw()

    def on_transposer_open(self):
        if not self.settings.windows.transposer.get():
            self.settings.windows.transposer.set(True)
            self.transposer_window = TransposerWindow(self)

    def on_transposer_close(self):
        # disable all transposition settings when closing, but leave nashville.
        if self.settings.windows.transposer.get():
            self.transposer_window.quit_window()

    def on_add_song_to_pool(self):
        """Add current monitor contents to pool."""
        live_song = self.app.deck.live
        if not live_song:
            return 
        self.app.data.gig.add_song_to_pool(live_song)

    def on_add_song_to_setlist(self):
        """Add current monitor contets to setlist."""
        live_song = self.app.deck.live
        if not live_song:
            return

        self.app.data.gig.live_setlist.add(live_song)

    def on_load_cued_to_live(self, event):
        app = self.app

        # TODO: warn that you can't load a new song
        # with this shortcut in edit mode.
        if app.deck.cued and not app.settings.editor.enabled.get():
            app.tools.loader.load_cued_to_live(event)

    def on_edit_mode(self, keyboard=False):
        """Toggles edit mode."""
        # TODO: can probably roll this and just look at event

        editable = self.settings.editor.enabled
        monitor = self.app.monitor
        running = self.settings.scroll.running

        # if the call originates from the keyboard, manually toggle.
        if keyboard:
            if editable.get():
                editable.set(False)
            else:
                editable.set(True)

        if editable.get():
            # enable
            monitor.config(highlightcolor="yellow", highlightbackground="#6E5D00")
            monitor.text.config(state="normal")
            running.set(False)
        else:
            # disable
            monitor.config(highlightcolor="light green", highlightbackground="dark grey")
            monitor.text.config(state="disabled")








"""
CHANGE ENTRY NAME: https://stackoverflow.com/questions/20369754/update-label-of-tkinter-menubar-item


"""