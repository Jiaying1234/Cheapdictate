import pyperclip
from pynput import keyboard


def paste_text(text: str) -> None:
    """Paste text into whichever window currently has keyboard focus."""
    if not text:
        return

    controller = keyboard.Controller()
    pyperclip.copy(text)
    ctrl_pressed = False
    try:
        # Send paste to the active window without moving focus to Cheapdictate.
        controller.press(keyboard.Key.ctrl)
        ctrl_pressed = True
        controller.press("v")
        controller.release("v")
    finally:
        if ctrl_pressed:
            controller.release(keyboard.Key.ctrl)
