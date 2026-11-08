from collections.abc import Callable

from pynput import keyboard


class RightShiftHotkey:
    """Listen globally for right Shift press and release events."""

    def __init__(
        self,
        on_press: Callable[[], None],
        on_release: Callable[[], None],
    ) -> None:
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
        if key == keyboard.Key.shift_r and not self._pressed:
            self._pressed = True
            self._on_press()

    def _handle_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if key == keyboard.Key.shift_r:
            self._pressed = False
            self._on_release()
