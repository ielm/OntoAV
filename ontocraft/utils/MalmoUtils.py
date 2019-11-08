from malmo import MalmoPython
from pkgutil import get_data
from typing import List, Tuple, Union
from xml.dom import minidom
import sys
import time

class OntoCraftAgentHost(MalmoPython.AgentHost):

    def startMission(self, mission: MalmoPython.MissionSpec, *args):
        super().startMission(mission, *args)
        self.mission_xml = mission
        self.role_index = 0 if len(args) == 1 else int(args[2])

    def agent_spec(self) -> minidom.Element:
        xmldoc = minidom.parseString(self.mission_xml.getAsXML(True))
        mission = xmldoc.getElementsByTagName("Mission")[0]
        agents = mission.getElementsByTagName("AgentSection")

        return agents[self.role_index]

    def name(self) -> str:
        agent = self.agent_spec()
        return agent.getElementsByTagName("Name")[0].firstChild.wholeText

    def chat(self) -> Tuple[bool, bool]:
        agent = self.agent_spec()
        handlers = agent.getElementsByTagName("AgentHandlers")[0]

        return (
            len(handlers.getElementsByTagName("ObservationFromChat")) > 0,
            len(handlers.getElementsByTagName("ChatCommands")) > 0,
        )

    def discrete_movement(self) -> bool:
        agent = self.agent_spec()
        handlers = agent.getElementsByTagName("AgentHandlers")[0]

        return len(handlers.getElementsByTagName("DiscreteMovementCommands")) > 0

    def position(self) -> bool:
        agent = self.agent_spec()
        handlers = agent.getElementsByTagName("AgentHandlers")[0]

        return len(handlers.getElementsByTagName("ObservationFromFullStats")) > 0

    def supervision(self) -> Union[None, Tuple[Tuple[int, int, int], Tuple[int, int, int]]]:
        agent = self.agent_spec()
        handlers = agent.getElementsByTagName("AgentHandlers")[0]

        ofgs = handlers.getElementsByTagName("ObservationFromGrid")
        if len(ofgs) == 0:
            return None

        ofg = ofgs[0]
        for grid in ofg.getElementsByTagName("Grid"):
            if grid.attributes["name"].value != "supervision":
                continue
            min = grid.getElementsByTagName("min")[0]
            max = grid.getElementsByTagName("max")[0]

            min = (
                int(min.attributes["x"].value),
                int(min.attributes["y"].value),
                int(min.attributes["z"].value),
            )

            max = (
                int(max.attributes["x"].value),
                int(max.attributes["y"].value),
                int(max.attributes["z"].value),
            )

            return min, max

        return None


def bootstrap(mission_file: Tuple[str, str]) -> OntoCraftAgentHost:
    host = _make_host()
    mission = _config_malmo(mission_file)
    _start(host, mission)
    _wait_for_ok(host)

    return host

def bootstrap_specific(mission_file: Tuple[str, str], clients: List[Tuple[str, int]], index: int) -> OntoCraftAgentHost:
    mission = _config_malmo(mission_file)
    client_pool = _config_clients(clients)

    host = _make_host()
    _start(host, mission, client_pool, index)

    _wait_for_ok(host)
    return host

def _make_host() -> OntoCraftAgentHost:
    host = OntoCraftAgentHost()

    try:
        host.parse(sys.argv)
    except RuntimeError as e:
        print('ERROR:', e)
        print(host.getUsage())
        exit(1)

    if host.receivedArgument("help"):
        print(host.getUsage())
        exit(0)

    return host

def _config_malmo(mission_file: Tuple[str, str]) -> MalmoPython.MissionSpec:
    xml = get_data(mission_file[0], mission_file[1])
    mission = MalmoPython.MissionSpec(xml, True)
    return mission

def _config_clients(clients: List[Tuple[str, int]]=None) -> Union[None, MalmoPython.ClientPool]:
    if clients is None:
        return None

    client_pool = MalmoPython.ClientPool()
    for client in clients:
        client_pool.add(MalmoPython.ClientInfo(client[0], client[1]))

    return client_pool

def _start(host: OntoCraftAgentHost, mission: MalmoPython.MissionSpec, client_pool: MalmoPython.ClientPool=None, role: int=0):
    record = MalmoPython.MissionRecordSpec()

    max_retries = 3
    for retry in range(max_retries):
        try:
            if client_pool is None:
                host.startMission(mission, record)
            else:
                host.startMission(mission, client_pool, record, role, "")
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:", e)
                exit(1)
            else:
                time.sleep(2.5)

def _wait_for_ok(host: OntoCraftAgentHost):
    print("Waiting for the mission to start", end=' ')
    world_state = host.getWorldState()
    while not world_state.has_mission_begun:
        print(".", end="")
        time.sleep(0.1)
        world_state = host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    time.sleep(0.5)