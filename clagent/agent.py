from ontocraft.agent import MalmoAgent
from ontocraft.effectors.move import MoveAMR
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.observers.position import PositionXMR
from ontocraft.utils.MalmoUtils import OntoCraftAgentHost, bootstrap
from clagent.handle import ChatHandleExecutable
from operator import sub
from pkgutil import get_data
from typing import List, Tuple
import time


CARDINAL_LIST = [
    PositionXMR.Facing.SOUTH,
    PositionXMR.Facing.WEST,
    PositionXMR.Facing.NORTH,
    PositionXMR.Facing.EAST
]
DELTA_TO_CARDINAL = {
    (-1, 0): PositionXMR.Facing.SOUTH,
    (0, 1): PositionXMR.Facing.WEST,
    (1, 0): PositionXMR.Facing.NORTH,
    (0, -1): PositionXMR.Facing.EAST,
}

class CLAgent(MalmoAgent):
    @classmethod
    def build(cls, host: OntoCraftAgentHost, map_file: Tuple[str, str]) -> 'CLAgent':
        agent = super().build(host)
        agent = CLAgent(agent.anchor)
        
        if map_file is not None:
            map_array = get_data(*map_file).split(b'\n')
            agent.town_map = {(ix, iy): c for ix, row in enumerate(map_array)
                                          for iy, c in enumerate(row)}
            agent.map_loc = agent._get_coord('A')
            agent.town_map[agent.map_loc] = ord('R')
        
        return agent

        # TODO:
        #   [] - Do something with effectors
        #   [] - Build utilities for building movement AMRs paths automatically
        #   [] - Build utilities for moving, observing, and generating output (speech and movement)

    def _get_coord(self, char: str) -> Tuple[int, int]:
        return next(coord for coord, c in self.town_map.items() if c == ord(char))

    def _find_path(self, dest: Tuple[int, int]) -> List[Tuple[int, int]]:
        queue = [(self.map_loc, [self.map_loc])]
        while len(queue):
            (loc, path) = queue.pop(0)
            for delta in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_loc = tuple(map(sum, zip(loc, delta)))
                if next_loc not in self.town_map:
                    continue
                if next_loc == dest:
                    return path + [dest]
                if next_loc not in path and self.town_map[next_loc] == ord('R'):
                    queue.append((next_loc, path + [next_loc]))
        return None

    def navigate_to(self, char: str):
        if self.town_map is None:
            raise
        destination = self._get_coord(char)
        # keep trying till we get there
        success = False
        while not success:
            path = self._find_path(destination)
            success = True

            for next_loc in path[1:]:
                self.observe(join=True)
                target_delta = tuple(a - b for a, b in zip(next_loc, self.map_loc))
                
                # check if path is blocked
                block = self.environment().relative_block(self, -target_delta[1], 0, -target_delta[0]).type()
                # if it is, mark that on the map and try again
                if block and next_loc != destination:
                    print(block)
                    self.town_map[next_loc] = ord('X')
                    self.speaksentence('Recalculating.')
                    success = False
                    break

                target_dir = DELTA_TO_CARDINAL[target_delta]
                dir_delta = (CARDINAL_LIST.index(target_dir) - 
                            CARDINAL_LIST.index(self.facing()) + 4) % 4
                
                amr = MoveAMR.build()
                if dir_delta == 1:
                    amr.add_to_path_turn_clockwise()
                if dir_delta == 2:
                    amr.add_to_path_turn_clockwise()
                    amr.add_to_path_turn_clockwise()
                if dir_delta == 3:
                    amr.add_to_path_turn_counterclockwise()
                if next_loc != destination:
                    amr.add_to_path_move_forward()
                    self.map_loc = next_loc
                self.move(amr, join=True)



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
