import tkinter as tk
import sqlite3
import logging


class AppData():
    """Class for app data used in saving and recalling workspace, settings."""

    def __init__(self, app):
        self.app = app

        # local ref to db manager
        self.dbmanager = app.tools.dbmanager
        # connect the dbmanager 
        self.dbmanager.data = self
        self.db = app.settings.paths.db.get()

        # init workspace collections
        self.workspace = WorkspaceData(self)
        self.setlists = self.workspace.setlists
        self.pool = self.workspace.pool

        self.collections = (self.setlists, self.pool)

    def dump_workspace_to_db(self):
        """Dump the workspace to db at program exit."""

        logging.info('dump_workspace_to_db in AppData')

        # TODO:
        # get lowest available gig_id, assign to settings.workspace.workspace_gig_id
        # dump pool songs to db, tracking their song_ids
        # dump pool song_ids list to pool meta with associated workspace_gig_id
        # dump all songs in the setlists
        # dump all gig setlists, tracking their setlist_ids in the order they are in memory
            # before you dump each setlist, dump its songs, tracking their ids
            # dump the setlist with song_ids to setlist_songs
        # dump  the ordered setlist ids to gig_setlists table

    def get_last_workspace_from_db(self):
        """Restore workspace from last session on load."""
        logging.info('get_last_workspace_from_db in AppData')


class SongCollection:
    """Generic class for containing a list of songs."""

    def __init__(self, app, name=None):
        # TODO: on init, attempt to load previous.

        # name collection
        self.app = app
        self.name = name
        self.songs = []

        self.callbacks = {}

    def clear_collection_songs(self):
        """Delete all songs in the collection."""

        self.songs.clear()
        self.do_callbacks()

    @property
    def names(self):
        """Return names of all songs in the collection."""

        return [song.name for song in self.songs] if self.songs else None

    def add_callback(self, fn, *args, **kwargs):
        self.callbacks[fn] = (args, kwargs)

    def do_callbacks(self):
        for fn, v in self.callbacks.items():
            fn(*v[0], **v[1]) if v else fn()


class SetlistCollection(SongCollection):
    """Holds a song pool, and a list of Setlist versions that reference the song pool."""

    def __init__(self, app):
        SongCollection.__init__(self, app)
        # TODO: on init, attempt to load previous from db.

        self.setlists = [Setlist(self)]
        self.live = self.setlists[0]
        self.markers = {
        'played': [],
        'skipped': [],
        'live': None,
        'previous': None,
        'nextup': None
        }

        self.app.deck.add_callback('live', self.update_marks)

    def update_marks(self):
        """Update song markers based on deck."""
        logging.info('update_marks in SetlistCollection')
        self.try_mark('previous', self.app.deck.previous)
        self.try_mark('live', self.app.deck.live)
        self.mark_nextup()

    def try_mark(self, local, deck):
        """Try to update mark from deck"""

        if deck in self.live.songs:
            self.markers[local] = deck

    def mark_nextup(self):
        logging.info('mark_nextup in SetlistCollection')
        count = len(self.live.songs)
        for i, song in enumerate(self.live.songs):
            if song is self.markers.get('live'):
                self.markers['nextup'] = self.live.songs[i+1] if i < count-1 else None
                break

    def new_setlist(self, name=None):
        """Add a new setlist to the setlists."""
        self.setlists.append(Setlist(self, name))

    def add_song(self, song):
        """Add a song to the setlist."""

        if not song:
            return

        names = self.live.names
        if names is not None and song.name in names:
            logging.info('same named song already in setlist!')
            return

        self.songs.append(song)
        self.live.songs.append(song)
        self.update_marks()
        self.do_callbacks()

    def add_live(self):
        """Add the live song to the setlist."""

        self.add_song(self.app.deck.live)

    def skip_toggle(self, song):
        """Toggle song skip."""

        if song not in self.skipped:
            self.skipped.append(song)
        else:
            self.skipped.remove(song)

    def move_song(self, setlist, song_i, dest):
        """Move song within a setlist."""

        logging.info('move_song in SetlistCollection')
        if not setlist.songs:
            return

        # constrain dest to length of list
        if dest > len(setlist.songs) - 1:
            dest = song_i

        # move the song, refresh the list representation
        setlist.songs.insert(dest, setlist.songs.pop(song_i))
        self.update_marks()

    def remove_song_if_orphaned(self, song):
        """If a song no longer exists in any of the setlists,
        remove it from the pool."""

        logging.info(f'remove_song_if_orphaned in SetlistCollection')
        for setlist in self.setlists:
            if song in setlist.songs:
                logging.info('song in setlist.songs, keeping in pool')
                return

        logging.info('song no longer in any setlist versions, removing from pool')
        self.songs.remove(song)

class Setlist:
    """Class for a setlist."""

    def __init__(self, parent, *args, **kwargs):
        # pool contains all available songs

        self.parent = parent
        self.title = kwargs.get('title')

        self.pool = parent.songs

        # songs contains songs as they are ordered in this setlist
        self.songs = []

        # db pointers
        self.setlist_id = None 
        self.library_id = None 

    @property
    def names(self):
        """Return names of all songs in the collection."""
        return [song.name for song in self.songs] if self.songs else []

    @property
    def numbered(self, style=lambda i: " (" + str(i+1) + ") "):
        """Return songs with numbers."""

        # TODO: inefficient
        return [style(i) + song.name for i, song in enumerate(self.songs)] if self.songs else []

    def remove_song(self, i):
        """Remove song from the setlist, 
        and pool if it has no other references."""
        logging.info(f'remove_song in Setlist recieved index: {i}')
        song = self.songs[i]
        self.songs.remove(song)
        self.parent.remove_song_if_orphaned(song)
        # TODO: if deleted song is currently in song info, clear the song info
        # achieve with listeners within song? more comprehensive callback manager?


class PoolCollection(SongCollection):
    """Song collection with properties specific to pool."""

    def __init__(self, name=None):
        SongCollection.__init__(name)

        self.pointers = PoolPointers(self)

        # library pointers. TODO: maybe rename to collection_id
        self.pool_id = None
        self.library_id = None

class SetlistMetadata:
    """Class for storing setlist metadata."""
    # TODO: use dict instead, class probably not needed

    def __init__(self, setlist):
        self.setlist = setlist
        self.songs = setlist.songs 

        self.title = tk.StringVar()
        self.city = tk.StringVar()
        self.venue = tk.StringVar()
        self.date = tk.StringVar()

        # put the  schedule in here, fetch from it as needed.
        self.schedule = {}

        # guest performers {name: {guest_metadata}}
        self.guests = {}

        # other acts (openers generally) {name: time}
        self.other_acts = {}

        # most important dict! {meal: time}
        # extract this from sechedule
        # self.meals = {}

class PoolPointers:
    """Class for pointers used to determine visualization
    in a song list and play behavior."""

    def __init__(self, pool):
        self.pool = pool
        self.songs = setlist.songs

        # TODO: define pointers.

class WorkspaceData:
    """Class for holding the workspace data. Pool, setlists, notepad, config."""

    def __init__(self, parent):
        self.app = parent.app
        self.suite = parent

        # hold all workspace setlists
        self.setlists = SetlistCollection(self.app)
        self.pool = SongCollection(self.app, name='pool')


"""
SQLITE RESOURCES:

SCRUB table name strings: https://stackoverflow.com/questions/3247183/variable-table-name-in-sqlite

LINK TABLES: https://www.sqlitetutorial.net/sqlite-python/create-tables/
INSERT PYTHON VARS INTO SQLITE: https://stackoverflow.com/questions/19759349/how-to-insert-variable-into-sqlite-database-in-python
LINKING TABLES: https://stackoverflow.com/questions/46754674/linking-tables-in-sqlite-3-in-python
check documentation to get this running:
https://docs.python.org/3/library/sqlite3.html
suggestion on storing tuples:
https://stackoverflow.com/questions/5260095/saving-tuples-as-blob-data-types-in-sqlite3-in-python
BLOB data:
https://pynative.com/python-sqlite-blob-insert-and-retrieve-digital-data/#h-what-is-blob
i think songs will be stored as 2 tables each,
one for the contents (columns for the parts of the tuple),
and one for the song metadata. the metadata table will have a column that indicates the name of the song table.

still need to learn how sqlite dbs are sturctured, but i think it will be like... each song COLLECTION is a table.
the table contains columns for all the song metadata, and a column that points to the name of the table with the song tktuple data.
above the level of the COLLECTION will be another table that defines the different collections in each part of the program (setlist, pool)
and pointers for those respective tables.
another level higher we can point to the tables for GIG metadata alongside the COLLECTIONS. hopefully this
makes sense with the way SQL works. will research tomorrow.
FOREIGN KEYS, PRIMARY KEYS? 
    https://www.sqlitetutorial.net/sqlite-foreign-key/
    https://sqlite.org/forum/info/7c4fe04f2546ed2a
link tables: https://dba.stackexchange.com/questions/21929/how-to-link-data-from-a-table-to-another-table-in-sqlite-database
"""