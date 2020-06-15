import time
import datetime

import numpy as np
import cv2
from skimage.measure import compare_ssim as ssim

from Vision import TemplateDetector


class Fisherman:
    _MAX_WAITING_SECONDS = 20
    _BITE_SSIM_THRESHOLD = 0.2
    _DELAY_BTW_THROWS = 2
    _DELAY_AFT_THROWS = 2.5
    _NUMBER_FRAMES_FOR_SCENE = 60
    _BOBBER_W = 46
    _BOBBER_H = 46

    def __init__(self, vision, controller, minutes):
        self.vision = vision
        self.controller = controller
        self.tmplDet = TemplateDetector()
        self.minutes = minutes
        
        self.bobberTmpl = None

    # ----------------------------------------------------------------------------------------------------------------------
    # Public methods
    def Activate(self):
        self.controller.FirstPerson()
        self.bobberTmpl = self._NewBobberTemplate()
        start = datetime.datetime.now()
        while True:
            self._ThrowBobber()
            bitedPos = self._WaitForBite()
            if not bitedPos is None:
                self._PullBobber(bitedPos)
            # Check time for exit
            now = datetime.datetime.now()
            deltaMinutes = (now - start).total_seconds() / 60
            if deltaMinutes >= self.minutes:
                break    
    
    # ----------------------------------------------------------------------------------------------------------------------
    # Private methods
    def _CreateStaticScene(self):
        staticScene = None
        for _ in range(Fisherman._NUMBER_FRAMES_FOR_SCENE):
            state = self.vision.GetGameState()
            normedImg = state['screen'] / Fisherman._NUMBER_FRAMES_FOR_SCENE
            if staticScene is None:
                staticScene = np.zeros(normedImg.shape)
            staticScene = staticScene + normedImg
        return staticScene

    def _NewBobberTemplate(self):
        staticScene = self._CreateStaticScene()
        self._ThrowBobber()
        state = self.vision.GetGameState()
        img = state['screen']
        # Find diff img
        diffImg = np.uint8(np.sqrt((img - staticScene)**2))
        gray = cv2.cvtColor(diffImg, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)
        diffImg = cv2.bitwise_and(img, img, mask=mask)
        pos = self._FindBobber(diffImg)
        self.controller.Click(pos)
        time.sleep(3)
        newTmpl = self._GetBobberImg(img, pos)
        return newTmpl

    def _GetBobberImg(self, img, pos):
        bobberLeft = pos[0] - Fisherman._BOBBER_W // 2
        bobberTop = pos[1] - Fisherman._BOBBER_H // 2
        bobberImg = img[bobberTop : bobberTop + Fisherman._BOBBER_H, 
                        bobberLeft : bobberLeft + Fisherman._BOBBER_W, :]
        return bobberImg

    def _FindBobber(self, img):
        if not self.bobberTmpl is None:
            pos = self.tmplDet.FindObject(img, tmplImg=self.bobberTmpl)
        else:
            pos = self.tmplDet.FindObject(img, self.tmplDet.TMPL_BOBBER)
        return pos

    def _WaitForBite(self):
        start = datetime.datetime.now()
        state = self.vision.GetGameState()
        pos = self._FindBobber(state['screen'])
        startBobberImg = self._GetBobberImg(state['screen'], pos)
        while True:
            state = self.vision.GetGameState()
            currentBobberImg = self._GetBobberImg(state['screen'], pos)
            m = ssim(startBobberImg, currentBobberImg, multichannel=True)
            if m < Fisherman._BITE_SSIM_THRESHOLD:
                return pos
            # Check time for exit
            now = datetime.datetime.now()
            deltaSeconds = (now - start).total_seconds()
            if deltaSeconds >= Fisherman._MAX_WAITING_SECONDS:
                return None

    def _ThrowBobber(self):
        state = self.vision.GetGameState()
        buttonPos = self.tmplDet.FindObject(state['screen'], tmplName=self.tmplDet.TMPL_FISHING)
        self.controller.Click(buttonPos)
        time.sleep(Fisherman._DELAY_AFT_THROWS)

    def _PullBobber(self, pos):
        self.controller.Click(pos)
        time.sleep(Fisherman._DELAY_BTW_THROWS)