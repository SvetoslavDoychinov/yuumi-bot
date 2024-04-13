import logging
from time import sleep
from typing import Tuple, Callable

import keyboard
import mouse
import pyautogui
from win32gui import FindWindow, GetWindowRect, SetForegroundWindow


class WindowManager:
    """Base Class to manage a Window"""

    def __init__(self, window_name: str):
        self.window_name = window_name
        self.logger = logging.getLogger(__name__)
        self.handle = None
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def configure(self) -> None:
        """Get necessary window parameters and set attributes accordingly"""
        self.logger.debug(f"Configuring WindowClicker for {self.window_name}")
        self.handle = FindWindow(None, self.window_name)
        window_rect = GetWindowRect(self.handle)
        self.x = window_rect[0]
        self.y = window_rect[1]
        self.width = window_rect[2] - self.x
        self.height = window_rect[3] - self.y

    def set_foreground(self) -> bool:
        """
        Sets the window as foreground
        :return: True if succeeded, False otherwise
        """
        try:
            self.configure()
            SetForegroundWindow(self.handle)
            sleep(0.5)  # Might click too fast on wrong screen otherwise
            return True
        except Exception:
            return False

    def right_click(self, ratio: Tuple[float, float]) -> None:
        """
        Right click on window
        :param ratio: used to calculate where to click
        """
        if self.set_foreground():
            self.logger.debug(f"Right clicking {self.window_name} on ratio {ratio}")
            pyautogui.moveTo(x=self.width * ratio[0] + self.x, y=self.height * ratio[1] + self.y)
            mouse.right_click()

    def left_click(self, ratio: Tuple[float, float]) -> None:
        """
        Right click on window
        :param ratio: used to calculate where to click
        """
        if self.set_foreground():
            self.logger.debug(f"Left clicking {self.window_name} on ratio {ratio}")
            pyautogui.moveTo(x=self.width * ratio[0] + self.x, y=self.height * ratio[1] + self.y)
            mouse.click()

    def press_key(self, key: str) -> None:
        """
        Press a keyboard key once and release it
        :param key: key to press
        """
        if self.set_foreground():
            self.logger.debug(f"Pressing and releasing key {key} on window {self.window_name}")
            keyboard.press_and_release(key)

    def hold_key(self, key: str) -> None:
        """
        Hold a key indefinitely
        :param key: key to hold
        """
        if self.set_foreground():
            self.logger.debug(f"Holding key {key} on window {self.window_name}")
            if not keyboard.is_pressed(key):
                keyboard.press(key)

    def release(self, key: str) -> None:
        """
        Release a key you are holding
        :param key: key to hold
        """
        if self.set_foreground():
            self.logger.debug(f"Releasing key {key} on window {self.window_name}")
            if keyboard.is_pressed(key):
                keyboard.release(key)

    def write(self, text: str) -> None:
        """
        Write text to window
        :param text:
        """
        if self.set_foreground():
            keyboard.write(text)
