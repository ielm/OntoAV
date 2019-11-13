from ontocraft.agent import MalmoAgent
from ontocraft.effectors.move import MoveAMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.utils.MalmoUtils import OntoCraftAgentHost, bootstrap

import time


class OntoAV:

    def __init__(self, agent: MalmoAgent = None, host: OntoCraftAgentHost = None, effectors: list = None):
        if host is None:
            self.host = bootstrap(("resources", "world.xml"))
            self.host.sendCommand("hotbar.9 1")
            time.sleep(0.5)

        if agent is None:
            self.agent = MalmoAgent.build(self.host)

        print(self.agent.anchor["HAS-NAME"].singleton())

        self.agent.observe(join=True)

        # TODO:
        #   [] - Do something with effectors
        #   [] - Build utilities for building movement AMRs paths automatically
        #   [] - Build utilities for moving, observing, and generating output (speech and movement)

    def speak(self, string: str):
        tmr = SpeechTMR.build(string)
        self.agent.speak(tmr, join=True)

    @staticmethod
    def move_forward(amr: MoveAMR = None, distance: int = 1):
        if amr is None:
            amr = MoveAMR.build()
        for i in range(distance):
            amr.add_to_path_move_forward()
        return amr

    @staticmethod
    def move_backward(amr: MoveAMR = None, distance: int = 1):
        if amr is None:
            amr = MoveAMR.build()
        for i in range(distance):
            amr.add_to_path_move_backward()
        return amr

    @staticmethod
    def turn_cw(amr: MoveAMR = None, times: int = 1):
        if amr is None:
            amr = MoveAMR.build()
        for i in range(times):
            amr.add_to_path_turn_clockwise()
        return amr

    @staticmethod
    def turn_ccw(amr: MoveAMR = None, times: int = 1):
        if amr is None:
            amr = MoveAMR.build()
        for i in range(times):
            amr.add_to_path_turn_counterclockwise()
        return amr

    def _move(self, mvmt: list, join=True):
        amrs = []

        if mvmt[0] == "f":
            amrs.append(self.move_forward(distance=mvmt[1]))
        if mvmt[0] == "b":
            amrs.append(self.move_backward(distance=mvmt[1]))
        if mvmt[0] == "cw":
            amrs.append(self.turn_cw(times=mvmt[1]))
        if mvmt[0] == "ccw":
            amrs.append(self.turn_ccw(times=mvmt[1]))
        for amr in amrs:
            self.agent.move(amr, join)
            self.observe(join)

    def move(self, input: str):
        input = [item.strip() for item in input.split(',')]
        for mvmt in input:
            mvmt = list(map(lambda x: int(x) if x.isdigit() else x, mvmt.split("x")))
            self._move(mvmt)

    def observe(self, join=True):
        self.agent.observe(join)

    def environment(self):
        return self.agent.environment()


if __name__ == '__main__':
    agent = OntoAV()

    planned_path = "cwx1, fx1, ccwx1, fx5"
    agent.move(planned_path)

    print(agent.environment().relative_block(agent.agent, 0, 1, 1).type())
