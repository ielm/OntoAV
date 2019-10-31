from ontoagent.agent import Agent
from ontoagent.engine.effector import Effector
from ontoagent.engine.executable import EffectorExecutable
from ontoagent.engine.signal import XMR
from ontograph.Frame import Frame
from ontograph.Space import Space
from typing import Union
import time


class MoveAMR(XMR):

    @classmethod
    def build(cls) -> 'MoveAMR':
        anchor = Frame("@IO.AMR.?").add_parent(Frame("@ONT.AMR"))
        space = XMR.next_available_space("AMR")
        root = space.frame("@.MOTION-EVENT.?").add_parent("@ONT.MOTION-EVENT")
        path = space.frame("@.PATH.?")

        root["DESTINATION"] = path

        a = super().build(root, space=space, anchor=anchor, constituents=[anchor, path])

        return MoveAMR(a.anchor)

    def path(self) -> Frame:
        return self.root()["DESTINATION"].singleton()

    def add_to_path_move_forward(self):
        self.add_step("FORWARD")

    def add_to_path_move_backward(self):
        self.add_step("BACKWARD")

    def add_to_path_turn_clockwise(self):
        self.add_step("CLOCKWISE")

    def add_to_path_turn_counterclockwise(self):
        self.add_step("COUNTERCLOCKWISE")

    def add_step(self, direction: str):
        step = self.space().frame("@.STEP.?")
        step["DIRECTION-OF-MOTION"] = direction
        self.path()["HAS-STEP"] += step
        self.add_constituent(step)


class MoveEffector(Effector):

    @classmethod
    def build(cls, space: Union[str, Space]=None) -> 'MoveEffector':
        type = Frame("@ONT.MOVE-EFFECTOR").add_parent("@ONT.EFFECTOR")
        effector = super().build(type=type, space=space, executable=MoveEffectorExecutable)
        return MoveEffector(effector.anchor)


class MoveEffectorExecutable(EffectorExecutable):

    def run(self, agent: Agent, xmr: XMR, effector: Effector):

        direction_map = {
            "FORWARD": self.move_forward,
            "BACKWARD": self.move_backward,
            "CLOCKWISE": self.turn_clockwise,
            "COUNTERCLOCKWISE": self.turn_counterclockwise
        }

        move = xmr.root()
        path = move["DESTINATION"].singleton()
        for step in path["HAS-STEP"]:
            direction = step["DIRECTION-OF-MOTION"].singleton()
            direction_map[direction]()
            time.sleep(0.5)

    def move_forward(self):
        Agent.malmo_host.sendCommand("move 1")

    def move_backward(self):
        Agent.malmo_host.sendCommand("move -1")

    def turn_clockwise(self):
        Agent.malmo_host.sendCommand("turn 1")

    def turn_counterclockwise(self):
        Agent.malmo_host.sendCommand("turn -1")
