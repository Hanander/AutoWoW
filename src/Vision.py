import os

import cv2

import numpy as np

import time
from datetime import datetime

import numpy as np

from PIL import Image, ImageGrab 

from threading import Thread
from threading import Lock


class ScreenViewer:
    def __init__(self):
        self.mut = Lock()
        self.lastImageTimeStamp = None  # Time stamp of last image
        self.latestImage = None
        self.tmpImage = None
        self.continueLooping = False
        self.counter = 0

    # ----------------------------------------------------------------------------------------------------------------------
    # Public methods
    def Start(self):
        self.continueLooping = True
        thrd = Thread(target=self._ScreenUpdateT)
        thrd.start()
        return True

    def Stop(self):
        self.continueLooping = False

    def GetScreen(self):
        while self.latestImage is None:  # Screen hasn't been captured yet
            pass
        self.mut.acquire()
        screen = self.latestImage
        self.mut.release()
        return screen

    def GetScreenWithTime(self):
        while self.latestImage is None:  # Screen hasn't been captured yet
            pass
        self.mut.acquire()
        screen = self.latestImage
        timeStamp = self.lastImageTimeStamp
        self.mut.release()
        return screen, timeStamp

    #-----------------------------------------------------------------------------------------------------------------------
    # Private methods
    def _ScreenUpdateT(self):
        while self.continueLooping:
            self.tmpImage = self._GetScreenImg()
            self.counter += 1
            self.mut.acquire()
            self.latestImage = self.tmpImage  # Update the latest image in a thread safe way
            self.lastImageTimeStamp = time.time()
            self.mut.release()

    def _GetScreenImg(self):
        outImg = np.array(ImageGrab.grab(bbox = None))
        return outImg


class TemplateDetector:
    # Public template names
    TMPL_BOBBER = 'tmpl_bobber.bmp'
    TMPL_FISHING = 'tmpl_fishing.jpg'

    _ASSETS_FOLDER_PATH = 'assets'

    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(TemplateDetector, self).__new__(self)
        return self.instance

    def __init__(self):
        self.loadedTemplates = {}

    # ------------------------------------------------------------------------------------------------------------------
    # Public methods
    @staticmethod
    def FindObject(screen, tmplName=None, tmplImg=None):
        if not tmplName is None: 
            tmpl = TemplateDetector()._GetTemplate(tmplName)
        elif not tmplImg is None:
            tmpl = tmplImg
        x, y = TemplateDetector._FindCoordsByTmpl(screen, tmpl)
        return (int(x), int(y))

    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    @staticmethod
    def _FindCoordsByTmpl(source, tmpl):
        result = cv2.matchTemplate(source, tmpl, cv2.TM_CCOEFF_NORMED)
        loc = cv2.minMaxLoc(result)
        x = loc[3][0] + tmpl.shape[0] // 2
        y = loc[3][1] + tmpl.shape[1] // 2
        return int(x), int(y)

    def _GetTemplate(self, tmplName):
        if not tmplName in self.loadedTemplates.keys():
            tmplPath = os.path.join(TemplateDetector._ASSETS_FOLDER_PATH, tmplName)
            tmpl = cv2.imread(tmplPath)
            self.loadedTemplates[tmplName] = tmpl
        else:
            tmpl = self.loadedTemplates[tmplName]
        return tmpl


class Vision:
    # ------------------------------------------------------------------------------------------------------------------
    # Const vars
    SCREEN_BBOX = (0,0,1920,1080)
    ASSETS_FOLDER_PATH = 'assets'

    def __init__(self):
        self._sv = ScreenViewer()
        self._tmplDetector = TemplateDetector()
        self.isStarting = False

    # ------------------------------------------------------------------------------------------------------------------
    # Public methods
    def GetGameState(self):
        img, timestamp = self._GetGameScreen()
        if not img is None:
            status = self._CheckStatus(img)
            gameState = {
                'status': status,
                'timestamp': str(timestamp),
                'screen': img
            }
        else:
            gameState = {
                'status': 'fail',
                'timestamp': None,
                'screen': None,
            }
        return gameState

    def Start(self):
        self._sv.Start()

    def Stop(self):
        self._sv.Stop()

    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    def _GetGameScreen(self):
        if not self.isStarting:
            self.isStarting = True
            self.Start()
        screen, timestamp = self._sv.GetScreenWithTime()
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        cutScreen = screen[Vision.SCREEN_BBOX[1]:Vision.SCREEN_BBOX[3],
                           Vision.SCREEN_BBOX[0]:Vision.SCREEN_BBOX[2]]
        
        return cutScreen, timestamp

    def _CheckStatus(self, img):
        return 'play'