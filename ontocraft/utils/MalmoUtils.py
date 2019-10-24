from malmo import MalmoPython
from pkgutil import get_data
from typing import Tuple
import sys
import time

def bootstrap(mission_file: Tuple[str, str]) -> MalmoPython.AgentHost:
    host = _make_host()
    mission = _config_malmo(mission_file)
    _start(host, mission)
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

def _start(host: MalmoPython.AgentHost, mission: MalmoPython.MissionSpec):
    record = MalmoPython.MissionRecordSpec()

    max_retries = 3
    for retry in range(max_retries):
        try:
            host.startMission(mission, record)
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:", e)
                exit(1)
            else:
                time.sleep(2.5)

    print("Waiting for the mission to start", end=' ')
    world_state = host.getWorldState()
    while not world_state.has_mission_begun:
        print(".", end="")
        time.sleep(0.1)
        world_state = host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)

    time.sleep(0.5)