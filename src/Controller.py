import os

import time

import cv2

from pynput.keyboard import Key
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button
from pynput.mouse import Controller as MouseController

class Controller:
    # ------------------------------------------------------------------------------------------------------------------
    # Const vars
    # Cursor
    _CENTER_POS = (960, 540)
    _ROTATE_SPEED_X = 4.47
    _ROTATE_SPEED_Y = 6.8
    _ROTATE_STEP = 10
    
    # General
    _CONTROL_DELAY = 0.02

    def __init__(self):
        self.keyboard = KeyboardController()
        self.cursor = MouseController()

        self.loadedTemplates = {}
        self.currentPressedButtons = []
    
    # ------------------------------------------------------------------------------------------------------------------
    # Public methods
    def Forward(self):
        self.cursor.press(Button.left)
        self.cursor.press(Button.right)
        self.currentPressedButtons.append(Button.left)
        self.currentPressedButtons.append(Button.right)

    def Stop(self):
        for keycode in self.currentPressedButtons:
            if keycode in [Button.left, Button.right, Button.middle]:
                self.cursor.release(keycode)
            else:
                self.keyboard.release(keycode)
        time.sleep(Controller._CONTROL_DELAY)

    def Click(self, position):
        self.cursor.position = int(position[0]), int(position[1])
        time.sleep(Controller._CONTROL_DELAY)
        self.cursor.press(Button.left)
        time.sleep(Controller._CONTROL_DELAY)
        self.cursor.release(Button.left)

    def Scroll(self, amp):
        self.cursor.scroll(0, amp)

    def Rotate(self, angX, angY):
        self.cursor.position = Controller._CENTER_POS
        self.cursor.press(Button.left)
        currentAngX = abs(angX)
        currentAngY = abs(angY)
        modX = 1 if angX >= 0 else -1
        modY = 1 if angY >= 0 else -1
        while (currentAngX > 0) or (currentAngY > 0):
            # Find step by X and Y axis
            stepX = Controller._ROTATE_STEP if currentAngX >= Controller._ROTATE_STEP else currentAngX
            currentAngX -= stepX
            stepY = Controller._ROTATE_STEP if currentAngY >= Controller._ROTATE_STEP else currentAngY
            currentAngY -= stepY
            time.sleep(Controller._CONTROL_DELAY)
            pos = Controller._CENTER_POS
            newPos = (int(pos[0] + modX * Controller._ROTATE_SPEED_X * stepX), 
                      int(pos[1] + modY * Controller._ROTATE_SPEED_Y * stepY))
            self.cursor.position = newPos
            time.sleep(Controller._CONTROL_DELAY)
        self.cursor.release(Button.left)
        time.sleep(Controller._CONTROL_DELAY)

    def FirstPerson(self):
        self.Rotate(0, 180)
        self.Rotate(0, -80)
        for _ in range(30):
            self.Scroll(10)
            time.sleep(Controller._CONTROL_DELAY)


    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    def _PressKeyboard(self, keycode):
        self.keyboard.press(keycode)
        time.sleep(Controller._CONTROL_DELAY)
    
    