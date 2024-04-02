from time import monotonic

from textual.app import App, ComposeResult
from textual.containers import Grid, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Button, Header, Footer, Label, Static

class QuitScreen(Screen):
    """Screen with a dialog to quit."""

    BINDINGS = [
        ("q", "request_quit", "Quit"),
        ("c", "request_cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit (q)", variant="error", id="quit"),
            Button("Cancel (c)", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            event.button.blur()
            self.app.exit()
        else:
            event.button.blur()
            self.app.pop_screen()
    
    def action_request_cancel(self) -> None:
        """An action to toggle dark mode."""
        self.app.pop_screen()

    def action_request_quit(self) -> None:
        self.app.exit()

class TimeDisplay(Static):
    """A widget to display elased time."""

    start_time = reactive(monotonic)
    time = reactive(0.0)
    total = reactive(1.0)
    finished = reactive(False)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update the time to the current time."""
        self.time = self.total - (monotonic() - self.start_time)

    def watch_time(self, time: float, finished: bool) -> None:
        """Called when the time attribute changes."""
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        if time < 0:
            self.update_timer.pause()
            self.time = 0
            self.update(f"00:00:00.00")
            self.finished = True
            self.parent.action_set_finished(True, self)
        else:
            self.update(f"{hours:02,.0f}:{minutes:02.0f}:{seconds:05.2f}")

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total += monotonic() - self.start_time
        self.time = self.total

    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.total = 0
        self.time = 0

class PomodoroTimer(Static):
    """A widget to display Pomodoro timers."""

    def action_set_finished(self, finish: bool, time_display: TimeDisplay) -> None:
        """a"""
        self.add_class("finished")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start":
            time_display.start()
            self.add_class("started")
        elif button_id == "stop":
            time_display.stop()
            self.remove_class("started")
        elif button_id == "finish":
            time_display.reset()
        elif button_id == "reset":
            time_display.reset()

    def compose(self) -> ComposeResult:
        """Create child widgets of PomodoroApp"""
        yield Button("Start", id="start", variant="success")
        yield Button("Stop", id="stop", variant="error")
        yield Button("Finished", id="finish")
        yield Button("Reset", id="reset")
        yield TimeDisplay()


class PomodoroApp(App):
    """A Textual app to manage pomodoro timers."""

    CSS_PATH = "pomodoro.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("a", "add_pomodoro_timer", "Add"),
        ("r", "remove_pomodoro_timer", "Remove"),
        ("q", "request_quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(PomodoroTimer(), PomodoroTimer(), PomodoroTimer(), id="timers")

    def action_add_pomodoro_timer(self) -> None:
        """An action to add a timer."""
        new_pomodoro_timer = PomodoroTimer()
        self.query_one("#timers").mount(new_pomodoro_timer)
        new_pomodoro_timer.scroll_visible()

    def action_remove_pomodoro_timer(self) -> None:
        """Called to remove a timer."""
        timers = self.query("PomodoroTimer")
        if timers:
            timers.last().remove()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_request_quit(self) -> None:
        self.push_screen(QuitScreen())


if __name__ == "__main__":
    app = PomodoroApp()
    app.run()