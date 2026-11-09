from collections.abc import Callable

from pynput import keyboard


class Hotkey:
    """Listen globally for a configured key's press and release events."""

    def __init__(
        self,
        key_name: str,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
    ) -> None:
        try:
            self._key = keyboard.Key[key_name]
        except KeyError as error:
            raise ValueError(f"Unsupported hotkey: {key_name}") from error
        self._on_press = on_press
        self._on_release = on_release
        self._pressed = False
        self._listener = keyboard.Listener(
            on_press=self._handle_press,
            on_release=self._handle_release,
        )

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()

    def _handle_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if key == self._key and not self._pressed:
            self._pressed = True
            self._on_press()

    def _handle_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if key == self._key:
            self._pressed = False
            self._on_release()


class RightShiftHotkey(Hotkey):
    """Backward-compatible default hotkey wrapper."""

    def __init__(
        self,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
    ) -> None:
        super().__init__("shift_r", on_press, on_release)
