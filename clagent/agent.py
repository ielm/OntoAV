from sys import path
from os.path import dirname as dir

path.append(dir(path[0]))
__package__ = "worldtest"
from ontocraft.agent import MalmoAgent
from ontocraft.effectors.move import MoveAMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.utils.MalmoUtils import OntoCraftAgentHost, bootstrap
from clagent.handle import ChatHandleExecutable
import time


class CLAgent(MalmoAgent):
    @classmethod
    def build(cls, host: OntoCraftAgentHost) -> 'CLAgent':
        agent = super().build(host)
        agent = CLAgent(agent.anchor)
        return agent

        # TODO:
        #   [] - Do something with effectors
        #   [] - Build utilities for building movement AMRs paths automatically
        #   [] - Build utilities for moving, observing, and generating output (speech and movement)

    def speaksentence(self, string: str):
        tmr = SpeechTMR.build(string)
        self.speak(tmr, join=True)

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

    def _move(self, mvmt: list, join=True, debug=False):
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
            if debug:
                print()
                print(amr.root().debug())
                print(list(map(lambda x: x.debug(), amr.constituents())))
            self.move(amr, join)
            self.observe(join)

    def movepath(self, input: str, debug=False):
        input = [item.strip() for item in input.split(',')]
        for mvmt in input:
            mvmt = list(map(lambda x: int(x) if x.isdigit() else x, mvmt.split("x")))
            self._move(mvmt, debug=debug)


if __name__ == '__main__':
    host = bootstrap(("resources", "world.xml"))
    host.sendCommand("hotbar.9 1")
    time.sleep(0.5)

    agent = CLAgent.build(host)
    agent.add_response("@ONT.SPEECH-ACT", ChatHandleExecutable)

    planned_path = "cwx1, fx1, ccwx1, fx5, cwx1"
    agent.movepath(planned_path)

    print(agent.environment().relative_block(agent, 0, 1, 1).type())
