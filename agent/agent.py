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
    def move_forward_x(amr: MoveAMR = None, distance: int = 1):
        if amr is None:
            amr = MoveAMR.build()
        for i in range(distance):
            amr.add_to_path_move_forward()
        return amr

    @staticmethod
    def move_backward_x(amr: MoveAMR = None, distance: int = 1):
        if amr is None:
            amr = MoveAMR.build()
        for i in range(distance):
            amr.add_to_path_move_backward()
        return amr

    @staticmethod
    def turn_cw_x(amr: MoveAMR = None, times: int = 1):
        if amr is None:
            amr = MoveAMR.build()
        for i in range(times):
            amr.add_to_path_turn_clockwise()
        return amr

    @staticmethod
    def turn_ccw_x(amr: MoveAMR = None, times: int = 1):
        if amr is None:
            amr = MoveAMR.build()
        for i in range(times):
            amr.add_to_path_turn_counterclockwise()
        return amr

    def move(self, f: int=0, b: int=0, cw: int=0, ccw: int=0, join=True):
        # TODO - This is an abhorrent way to do this, I'll get around to doing this correctly soon

        amrs = []

        if f is not 0:
            amrs.append(self.move_forward_x(distance=f))
        if b is not 0:
            amrs.append(self.move_backward_x(distance=b))
        if cw is not 0:
            amrs.append(self.turn_cw_x(times=cw))
        if ccw is not 0:
            amrs.append(self.turn_ccw_x(times=ccw))

        for amr in amrs:
            self.agent.move(amr, join)
            # self.observe(join=True)

    def observe(self, join=True):
        self.agent.observe(join)


if __name__ == '__main__':
    agent = OntoAV()
    # agent.move(cw=1)
    # host = bootstrap(("resources", "world.xml"))
    # host.sendCommand("hotbar.9 1")
    # time.sleep(0.5)
    #
    # # Build a new agent
    # agent = MalmoAgent.build(host)
    # print(agent.anchor["HAS-NAME"].singleton())
    #
    # # Observe location and surroundings
    # agent.observe(join=True)
