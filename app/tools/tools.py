from tools.song import Song, SongFactory
from tools.transposer import Transposer
from tools.loader import LoadTool
from tools.scroll import ScrollTool
from tools.screens import Screens
from tools.dbmanager import DatabaseManager
from tools.guitools import GuiTools

class AppTools():
    """Class for holding tools for the app.
    Each tool contains methods for accomplishing
    a certain category of task."""

    def __init__(self, app):
        self.app = app

        self.factory = SongFactory(app)
        self.transposer = Transposer(app)
        self.screens = Screens(app)
        self.scroll = ScrollTool(app)
        # tool for loading songs between frames
        self.loader = LoadTool(app)
        self.dbmanager = DatabaseManager(app)
        self.gui = GuiTools(app)
