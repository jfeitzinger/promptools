import tkinter as tk
import logging

from gui.setlist import SetlistFrame
from gui.pool import PoolAndSetlistsFrame, PoolAndSetlistsNotebook
from tools.api import PrompToolsAPI

class CollectionsSuite(tk.PanedWindow, PrompToolsAPI):
    """Paned frame for the song collections on the left side of the app.
    It shows the live setlist, and the gig song pool."""

    def __init__(self, gui, *args, **kwargs):
        tk.PanedWindow.__init__(self,
            gui.root,
            orient="vertical",
            sashwidth=5,
            bg="light blue",
            # showhandle=True
            )
        PrompToolsAPI.__init__(self, gui)

        # make frames
        self.pool_and_setlists = PoolAndSetlistsNotebook(self)
        self.add(self.pool_and_setlists)

        self.live_setlist = SetlistFrame(self)
        self.add(self.live_setlist)

        # reload collection data from db
        # self.app.data.reload_all_collections_from_db()

    def sync(self):
        """Refresh views to match app state."""
        self.pool_and_setlists.sync()
        self.live_setlist.sync()