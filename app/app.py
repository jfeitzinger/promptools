import tkinter as tk
from tkinter import messagebox
import logging

# allows drag-n-drop, was a bit sketchy last time i used it. not using for now.
# import tkinterDnD as tkd

# app settings
from common.settings import Settings

# helper tools TODO: unroll tools.tools
from tools.tools import AppTools
from tools.data import AppData
from tools.cache import Cache
from tools.deck import SongDeck

# gui components
from gui.collections import CollectionsSuite
from gui.browser import BrowserSuite
from gui.talent import TalentWindow
from gui.monitor import TalentMonitor
from gui.preview import Preview
from gui.bigbutton import PromptButton
from gui.cued import CuedUp
from gui.menu import MenuBar
from gui.metapane import MetaSuite
from gui.helpbox import HelpBox
from gui.controls import AppControls
from gui.gui import TkGui

class MainApplication:
    """Class for the main application."""

    def __init__(self, root, *args, **kwargs) -> None:

        self.app = self
        self.root = root
        self.suite = None

        # init program settings
        self.settings = Settings(self)

        # tools for creating and moving data within the app, and scrolling
        # TODO: kinda convoluted struct
        self.tools = AppTools(self)

        # track songs played / cued & manage callbacks
        # TODO: seperate parts
        self.deck = SongDeck(self)

        # song cache, use weak references so old songs get gc'd
        self.cache = Cache(self)

        # sqlite3 / data mgmt
        self.data = AppData(self)

        # all gui elements
        self.gui = TkGui(app=self, root=root)
        # initial sync with 
        self.gui.sync()

        # keyboard / mouse / etc. mappings
        self.controls = AppControls(self)

        self._config_window_properties()

    def _init_gui(self):
        """Initialize all gui elements."""
        # 2nd window for talent
        self.talent = TalentWindow(self)

        # main window widgets
        self.monitor = TalentMonitor(self)
        self.monitor.grid(row=0, column=1, columnspan=2, sticky="nesw")

        # big PROMPT button, to be made context sensitive, eventually
        self.bigbutton = PromptButton(self)
        self.bigbutton.grid(
            row=3,
            column=1,
            rowspan=1,
            columnspan=2,
            ipadx=0,
            ipady=10,
            sticky="nesw",
            padx=5,
            pady=5,
        )

        self.browser = BrowserSuite(self)
        # self.browser = LibrarySuite(self) # this is the version that imports everything
        self.browser.grid(
            row=1,
            column=1,
            columnspan=1,
            rowspan=2,
            sticky="nesw",
            padx=8,
            pady=8,
        )

        # TODO: merge preview frame with cued since they will always live in that orientation
        self.cued = CuedUp(self)
        self.cued.grid(row=1, column=2, columnspan=1, sticky="nesw")

        self.preview = Preview(self)
        self.preview.grid(row=2, column=2, columnspan=1, sticky="nesw", padx=8, pady=8)

        self.meta = MetaSuite(self)
        self.meta.grid(row=0, column=3, sticky="nesw", rowspan=4) 

        # setlist / song pool pane on the left
        self.collections = CollectionsSuite(self)
        self.collections.grid(row=0, column=0, rowspan=3, sticky="nesw")

        # this will be a tooltip box in the bottom left corner of the app
        self.helpbox = HelpBox(self)
        self.helpbox.grid(row=3, column=0, sticky="nesw")

        # menubar at the top of the app
        self.menu = MenuBar(self)

    def _config_gui_columns(self):
        # configure rows / columns to get right weights
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=5)

    def _config_window_properties(self):
        # Set window attributes & icon
        self.root.tk.eval("tk::PlaceWindow . center")
        self.root.resizable(False, False)
        self.root.iconbitmap("./assets/generic.ico")

        # assign quit method
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

    def quit_app(self):
        """What to do when you quit."""

        # TODO: see if state has changed since last save, only show message if it has.
        choice = messagebox.askyesnocancel("Save State","Save state before quitting?")
        if choice is None:
            return
        elif choice == True:
            self.save_state()
        self.root.destroy()

    def save_state(self):
        """Save app state by dumping settings and gig data."""
        self.settings.dump_settings()
        self.tools.db_interface.dump_gig(self.app.data.gig, workspace=True)

def main():
    """Application main loop."""

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    root = tk.Tk()  # change to tkd.Tk if you end up using dnd package!
    root.title("PrompTools alpha")

    # TODO: decouple tkinter components from main app
    app = MainApplication(root)
    app.gui.mainloop()


if __name__ == "__main__":
    main()
