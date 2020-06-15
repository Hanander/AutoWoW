import time

from Vision import Vision
from Controller import Controller
from behaviours.Fisherman import Fisherman


class Agent:
    def __init__(self):
        self._vision = Vision()
        self._controller = Controller()
        self._behaviours = []

    # ------------------------------------------------------------------------------------------------------------------
    # Public methods
    def AddBehaviour(self, behaviourName, minutes):
        behaviour = self._GetBehaviourByName(behaviourName)(vision=self._vision,
                                                            controller=self._controller,
                                                            minutes=minutes)
        self._behaviours.append(behaviour)

    def Activate(self):
        self._vision.Start()
        while len(self._behaviours) > 0:
            behaviour = self._behaviours.pop(0)
            behaviour.Activate()
        self._vision.Stop()

    def Deactivate(self):
        self._vision.Stop()

    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    def _GetBehaviourByName(self, name):
        behaviour = None
        if name == 'fisherman':
            behaviour = Fisherman
        return behaviour