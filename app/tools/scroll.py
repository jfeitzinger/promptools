import datetime
import logging
import time

from tools.apppointers import AppPointers

# TODO: this probably belongs in gui since it is specific to tkinter gui
# helpers
def next_line(text):
    text.yview_scroll(1, "units")
    text.xview_moveto(0)


class ScrollTool(AppPointers):
    """Class for scroll & follow behaviors."""

    def __init__(self, parent):
        AppPointers.__init__(self, parent)

        # autoscroll rates
        self.rates = self.app.settings.scroll.rates

        # scroll settings should push on change to fill these
        self._pos = None
        self.pos = self.settings.scroll.pos.get()

        # init frame counter for delay comp
        self.reset_scroll_frame_counter()

        # register callback so params get updated when settings change
        self.settings.scroll.add_callback(self.refresh)

    @property
    def running(self):
        return self.settings.scroll.running

    def refresh(self):
        """Fetch all the scroll parameters and update."""
        logging.info("refresh in ScrollTool")
        self.pos = self.settings.scroll.pos.get()
        # self.running = self.settings.scroll.running.get()

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, new):
        pos = self.percent_to_pos(new)
        self._pos = self.percent_to_pos(new)

    def percent_to_pos(self, new):
        """Convert the pos % setting to the nearest scale value."""
        scale = len(self.rates)
        return int(scale * new // 1)

    def reset_scroll_frame_counter(self):
        """Reset the frame counter for delay comp."""
        self.next_frame = datetime.datetime.now()

    def scroll_loop(self):
        """Schedulet the autoscroll based on rate slider."""
        if self.running.get():
            self.talent.scroll() if self.pos != 0 else None
            self.schedule_scroll()
        elif self.settings.scroll.mon_snap.get():
            self.monitor.match_sibling_yview()

    def scaled_sleep_time(self):
        """Sleep for the time set by the speed slider."""
        rates = self.settings.scroll.rates
        return int(rates[self.pos - 1]) if self.running else int(rates[-1])

    def start_scroll(self):
        """When you start scroll from stopped, reset next frame."""

        self.next_frame = datetime.datetime.now()
        self.schedule_scroll(delay_comp=True)

    def schedule_scroll(self, delay_comp=True):
        """Schedule next scroll, accounting for latency in the after queue."""
        if delay_comp:
            self.gui.after(self.delay_comp(), self.scroll_loop)
        else:
            self.gui.after(self.scaled_sleep_time(), self.scroll_loop)

    def delay_comp(self):
        """Return ms with delay compensation for smoother autoscroll."""
        self.next_frame += datetime.timedelta(milliseconds=self.scaled_sleep_time())
        now = datetime.datetime.now()
        delta = max(datetime.timedelta(), self.next_frame - now)
        time = int(delta.total_seconds() * 1000)
        fps = int(1000 / time) if time else 0
        # print(f"ms: {time}, fps: {fps}") # comment in for readout on each tick while running
        return time

    def carriage_return(self):
        """Jump to next line and reset x scroll."""
        next_line(self.talent.text) if not self.settings.edit.enabled.get() else None

    def chunk_scroll(self, direction):
        """Scrolls for a little bit."""

        def toggle(chunk):
            chunk.enabled = False if chunk.enabled else True

        logging.info(f"chunk scrolling in direction: {direction}")
        # do not chunk scroll when editing
        if self.settings.edit.enabled.get():
            return

        scroll = self.settings.scroll
        chunk = self.settings.chunk
        talent = self.gui.talent
        monitor = self.monitor

        if not chunk.enabled:

            duration = chunk.duration_ms
            pixels = chunk.pixels_advanced
            step = chunk.step

            chunk.enabled = True

            for i in range(0, duration, step):
                self.gui.after(i, talent.scroll, direction)

            # allow overlapping chunk scrolls as long as first is half done.
            # TODO: make this configurable
            self.gui.after(duration // 2, lambda: toggle(chunk))

            mon_snaps_to_talent_pos = self.settings.scroll.mon_snap.get()
            if mon_snaps_to_talent_pos:
                self.gui.after(duration, monitor.match_sibling_yview)

    # TODO: re-integrate the monitor refresh loop
    def monitor_refresh_loop(self):
        """Refresh loop for monitor update."""
        # TODO: only run this when talent is running.
        # Currently scheduling even when talent is not running.
        app = self.app
        monitor = app.monitor
        ms = app.settings.scroll.mon_ms  # TODO: MonitorSettings()

        # TODO: Get this running smoother someday. underlying tkinter issue imo
        if self.monitor_refresh_conditions():
            monitor.match_sibling_yview()

        self.gui.after(ms, self.monitor_refresh_loop)

    def monitor_refresh_conditions(self):
        """Conditions for monitor refresh loop to execute refresh."""
        scroll = self.app.settings.scroll
        if scroll.mon_follow.get():
            return scroll.running

    # MOVED FROM MONITOR

    def shift_scroll_on(self, event=None):
        """Holding shift scrolls prompter."""

        if self.monitor.editable.get():
            return

        self.running.set(True)
        # self.schedule_scroll()
        self.start_scroll()
        logging.info("shift_scroll_on")

    def shift_scroll_off(self, event=None):
        """Releasing shift stops prompter."""
        self.running.set(False)
        logging.info("shift_scroll_off")

    def toggle_scroll(self):
        """Toggle autoscroll."""
        if self.scroller.running.get():
            self.scroller.running.set(False)
            logging.info("toggle_scroll OFF")
        elif not self.monitor.editable.get():
            self.scroller.running.set(True)
            self.start_scroll()
            logging.info("toggle_scroll ON")


class AutoscrollBehavior:
    """Define range of speed values for autoscroll speed slider as a list."""

    def __init__(self, smin=0.1, smax=0.001, steps=101, *args, **kwargs):

        self.set(smin, smax, steps)

    def set(self, smin, smax, steps):
        # hard limit loop speed for safety.
        smin = self.limit(smin)
        smax = self.limit(smax)
        mult = 10  # mult to scale this up for my uses.

        # Max pixels per second
        xps = 1 / smax
        inc = xps / steps

        # Make an empty list of correct length.
        vals = [None] * steps

        # Base pps for min speed.
        pix = 1 / smin

        for i in range(steps):
            vals[i] = 1 / pix * mult
            pix += inc

        self._vals = vals

    def limit(self, param, limit=0.0001):
        """Limit param value if it exceeds limit."""
        return limit if param < limit else param

    @property
    def vals(self):
        return self._vals
