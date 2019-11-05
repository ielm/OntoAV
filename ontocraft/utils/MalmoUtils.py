from malmo import MalmoPython
from pkgutil import get_data
from typing import List, Tuple, Union
import sys
import time

def bootstrap(mission_file: Tuple[str, str]) -> MalmoPython.AgentHost:
    host = _make_host()
    mission = _config_malmo(mission_file)
    _start(host, mission)
    _wait_for_ok(host)

    return host

def bootstrap_specific(mission_file: Tuple[str, str], clients: List[Tuple[str, int]], index: int) -> MalmoPython.AgentHost:
    mission = _config_malmo(mission_file)
    client_pool = _config_clients(clients)

    host = _make_host()
    _start(host, mission, client_pool, index)

    _wait_for_ok(host)
    return host

def _make_host() -> MalmoPython.AgentHost:
    host = MalmoPython.AgentHost()

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

def _start(host: MalmoPython.AgentHost, mission: MalmoPython.MissionSpec, client_pool: MalmoPython.ClientPool=None, role: int=0):
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

def _wait_for_ok(host: MalmoPython.AgentHost):
    print("Waiting for the mission to start", end=' ')
    world_state = host.getWorldState()
    while not world_state.has_mission_begun:
        print(".", end="")
        time.sleep(0.1)
        world_state = host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    time.sleep(0.5)