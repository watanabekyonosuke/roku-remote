"""TUI Roku Remote — Textual app."""

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.css.query import NoMatches
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, Label, Static

from roku_remote.ecp import RokuClient

CSS = """
Screen {
    background: $surface;
}

#main {
    layout: horizontal;
    height: 1fr;
}

#remote-panel {
    width: 42;
    min-width: 42;
    padding: 1 2;
    border-right: thick $primary-background;
}

#apps-panel {
    width: 1fr;
    padding: 1 2;
}

.section-title {
    color: $text-muted;
    text-style: bold;
    margin-bottom: 1;
    text-align: center;
}

#power-row {
    layout: horizontal;
    height: 3;
    align: center middle;
    margin-bottom: 1;
}

#power-row Button {
    min-width: 16;
    margin: 0 1;
}

#nav-grid {
    layout: grid;
    grid-size: 3 3;
    grid-gutter: 0;
    align: center middle;
    height: 9;
    width: 36;
    margin-bottom: 1;
}

#nav-grid Button {
    min-width: 12;
    height: 3;
}

.nav-blank {
    min-width: 12;
    height: 3;
}

#btn-ok { color: $text; }

#playback-row {
    layout: horizontal;
    height: 3;
    align: center middle;
    margin-bottom: 1;
}

#playback-row Button {
    min-width: 10;
    margin: 0 1;
}

#volume-row {
    layout: horizontal;
    height: 3;
    align: center middle;
    margin-bottom: 1;
}

#volume-row Button {
    min-width: 10;
    margin: 0 1;
}

#extra-row {
    layout: horizontal;
    height: 3;
    align: center middle;
    margin-bottom: 1;
}

#extra-row Button {
    min-width: 10;
    margin: 0 1;
}

#input-row {
    layout: horizontal;
    height: 3;
    align: center middle;
    margin-bottom: 1;
}

#input-row Button {
    min-width: 8;
    margin: 0 1;
}

#apps-grid {
    layout: grid;
    grid-size: 2;
    grid-gutter: 1;
    padding: 1;
}

#apps-grid Button {
    height: 3;
    min-width: 18;
}

#status-bar {
    dock: bottom;
    height: 1;
    background: $primary-background;
    color: $text;
    padding: 0 2;
}

.power-on {
    background: $success;
    color: $text;
}

.power-off {
    background: $error;
    color: $text;
}

Button.app-btn {
    background: $primary-background;
}

Button.app-btn:hover {
    background: $primary;
}
"""


class TypingScreen(ModalScreen[None]):
    BINDINGS = [Binding("escape", "dismiss", "Close")]

    DEFAULT_CSS = """
    TypingScreen {
        align: center middle;
    }
    #typing-dialog {
        width: 50;
        height: 9;
        border: round $primary;
        background: $surface;
        padding: 1 2;
    }
    #typing-dialog Label {
        margin-bottom: 1;
        text-align: center;
        width: 1fr;
    }
    #typing-dialog Input {
        margin-bottom: 1;
    }
    #typing-buttons {
        layout: horizontal;
        height: 3;
        align: center middle;
    }
    #typing-buttons Button {
        min-width: 12;
        margin: 0 1;
    }
    """

    def __init__(self, client: RokuClient) -> None:
        super().__init__()
        self.client = client

    def compose(self) -> ComposeResult:
        with Vertical(id="typing-dialog"):
            yield Label("Type text to send to TV")
            yield Input(placeholder="Type here...", id="typing-field")
            with Horizontal(id="typing-buttons"):
                yield Button("Send", variant="primary", id="send-text")
                yield Button("Cancel", id="cancel-text")

    def on_mount(self) -> None:
        self.query_one("#typing-field", Input).focus()

    @on(Button.Pressed, "#send-text")
    def send_text(self) -> None:
        text = self.query_one("#typing-field", Input).value
        if text:
            for ch in text:
                self.client.type_char(ch)
        self.dismiss()

    @on(Button.Pressed, "#cancel-text")
    def cancel(self) -> None:
        self.dismiss()

    @on(Input.Submitted)
    def on_submit(self) -> None:
        self.send_text()


class RokuRemote(App):
    TITLE = "Roku Remote"
    CSS = CSS
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("up", "nav('Up')", "Up", show=False),
        Binding("down", "nav('Down')", "Down", show=False),
        Binding("left", "nav('Left')", "Left", show=False),
        Binding("right", "nav('Right')", "Right", show=False),
        Binding("space", "press('Play')", "Play"),
        Binding("h", "press('Home')", "Home"),
        Binding("b", "press('Back')", "Back"),
        Binding("r", "press('Rev')", "Rew"),
        Binding("f", "press('Fwd')", "Fwd"),
        Binding("m", "press('VolumeMute')", "Mute"),
        Binding("i", "press('Info')", "Info"),
        Binding("s", "press('Search')", "Search"),
        Binding("t", "open_typing", "Type"),
        Binding("equal,plus", "press('VolumeUp')", "Vol+", show=False),
        Binding("minus", "press('VolumeDown')", "Vol-", show=False),
    ]

    def __init__(self, client: RokuClient, apps: dict[str, str],
                 inputs: dict[str, str], device_name: str) -> None:
        super().__init__()
        self.client = client
        self.installed_apps = apps
        self.tv_inputs = inputs
        self.device_name = device_name

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="main"):
            with Vertical(id="remote-panel"):
                yield Label("POWER", classes="section-title")
                with Horizontal(id="power-row"):
                    yield Button("On", id="btn-power-on", classes="power-on")
                    yield Button("Off", id="btn-power-off", classes="power-off")

                yield Label("NAVIGATE", classes="section-title")
                with Grid(id="nav-grid"):
                    yield Static(classes="nav-blank")
                    yield Button("▲", id="btn-up")
                    yield Static(classes="nav-blank")
                    yield Button("◄", id="btn-left")
                    yield Button("OK", id="btn-ok", variant="primary")
                    yield Button("►", id="btn-right")
                    yield Static(classes="nav-blank")
                    yield Button("▼", id="btn-down")
                    yield Static(classes="nav-blank")

                yield Label("PLAYBACK", classes="section-title")
                with Horizontal(id="playback-row"):
                    yield Button("◄◄", id="btn-rev")
                    yield Button("▶||", id="btn-play", variant="success")
                    yield Button("►►", id="btn-fwd")

                yield Label("VOLUME", classes="section-title")
                with Horizontal(id="volume-row"):
                    yield Button("−", id="btn-vol-down")
                    yield Button("Mute", id="btn-mute")
                    yield Button("+", id="btn-vol-up")

                yield Label("QUICK", classes="section-title")
                with Horizontal(id="extra-row"):
                    yield Button("Home", id="btn-home")
                    yield Button("Back", id="btn-back")
                    yield Button("Search", id="btn-search")
                    yield Button("Type", id="btn-type")

                if self.tv_inputs:
                    yield Label("INPUTS", classes="section-title")
                    with Horizontal(id="input-row"):
                        for input_id, name in self.tv_inputs.items():
                            btn_id = input_id.replace("tvinput.", "btn-")
                            yield Button(name, id=btn_id)

            with Vertical(id="apps-panel"):
                yield Label("APPS", classes="section-title")
                with Grid(id="apps-grid"):
                    for name, app_id in self.installed_apps.items():
                        yield Button(name, id=f"app-{app_id}", classes="app-btn")

        yield Label("Connecting...", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.update_status()
        self.set_interval(5, self.update_status)

    @work(thread=True)
    def update_status(self) -> None:
        power = self.client.power_state()
        app = self.client.active_app()
        status = f" {self.device_name}  |  {power}  |  {app}  |  {self.client.ip}"
        try:
            self.query_one("#status-bar", Label).update(status)
        except NoMatches:
            pass

    def on_key(self, event: Key) -> None:
        """Intercept Enter and Escape before Textual consumes them."""
        if event.key == "enter":
            event.prevent_default()
            event.stop()
            self._fire("Select")
        elif event.key == "escape":
            event.prevent_default()
            event.stop()
            self._fire("Back")

    def action_nav(self, key: str) -> None:
        """Send d-pad key to TV."""
        self._fire(key)

    def action_press(self, key: str) -> None:
        self._fire(key)

    def action_open_typing(self) -> None:
        self.push_screen(TypingScreen(self.client))

    @work(thread=True)
    def _fire(self, key: str) -> None:
        ok = self.client.keypress(key)
        mark = "+" if ok else "x"
        try:
            bar = self.query_one("#status-bar", Label)
            power = self.client.power_state()
            app = self.client.active_app()
            bar.update(f" [{mark}] {key}  |  {power}  |  {app}  |  {self.client.ip}")
        except NoMatches:
            pass

    @work(thread=True)
    def _launch(self, app_id: str, name: str) -> None:
        ok = self.client.launch(app_id)
        label = f"Launched {name}" if ok else f"Failed: {name}"
        try:
            self.query_one("#status-bar", Label).update(
                f" {label}  |  {self.client.ip}"
            )
        except NoMatches:
            pass

    @on(Button.Pressed)
    def handle_button(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if not btn_id:
            return

        key_map = {
            "btn-power-on": "PowerOn",
            "btn-power-off": "PowerOff",
            "btn-up": "Up",
            "btn-down": "Down",
            "btn-left": "Left",
            "btn-right": "Right",
            "btn-ok": "Select",
            "btn-play": "Play",
            "btn-rev": "Rev",
            "btn-fwd": "Fwd",
            "btn-vol-up": "VolumeUp",
            "btn-vol-down": "VolumeDown",
            "btn-mute": "VolumeMute",
            "btn-home": "Home",
            "btn-back": "Back",
            "btn-search": "Search",
        }

        # Handle HDMI/AV input buttons
        input_key_map = {
            "btn-hdmi1": "InputHDMI1",
            "btn-hdmi2": "InputHDMI2",
            "btn-hdmi3": "InputHDMI3",
            "btn-hdmi4": "InputHDMI4",
            "btn-cvbs": "InputAV1",
            "btn-dtv": "InputTuner",
        }

        if btn_id in key_map:
            self._fire(key_map[btn_id])
        elif btn_id in input_key_map:
            self._fire(input_key_map[btn_id])
        elif btn_id == "btn-type":
            self.push_screen(TypingScreen(self.client))
        elif btn_id.startswith("app-"):
            app_id = btn_id[4:]
            name = str(event.button.label)
            self._launch(app_id, name)
