from ontoagent.engine.executable import HandleExecutable
from ontoagent.engine.signal import Signal
from ontocraft.agent import MalmoAgent
from ontocraft.effectors.speech import SpeechTMR
from ontocraft.observers.chat import ChatTMR
from ontocraft.utils.MalmoUtils import bootstrap_specific
from ontograph.Frame import Frame

from clagent.agent import CLAgent
from clagent.handle import CommandHandleExecutable

import time

if __name__ == '__main__':
    clients = [
        ("localhost", 10000),
        ("localhost", 10001),
    ]

    def bootstrap_user():
        agent_host = bootstrap_specific(("worldtest.resources", "multiworld.xml"), clients, 0)

        agent = CLAgent.build(agent_host)

        action = False
        while agent.host().getWorldState().is_mission_running:
            time.sleep(2)

            if not action:
                tmr = SpeechTMR.build("My name is Ozymandias, king of agents: Look on my works, ye Mighty, and despair!")
                agent.speak(tmr, join=True)
                action = True

    # The agent, after the mission loads, will observe every 1 second.  When he finds a chat signal,
    # it will be analyzed and execute a chat handler which checks for movement commands. On
    # a movement command, the agent will execute the movement command.
    def bootstrap_agent():
        agent_host = bootstrap_specific(("worldtest.resources", "multiworld.xml"), clients, 1)

        agent = CLAgent.build(agent_host)

        # The agent needs to know who the User is, so the input signal can be attributed to the speaker correctly.
        user = Frame("@ENV.AGENT.?").add_parent("@ONT.AGENT")
        user["HAS-NAME"] = "User"

        # Make sure the agent knows how to respond to an analyzed speech act.
        agent.add_response(Frame("@ONT.SPEECH-ACT"), CommandHandleExecutable)

        while agent.host().getWorldState().is_mission_running:
            time.sleep(1)
            agent.observe(join=True)

    # Make a process for bootstrapping and running each agent; they do not need to be joined or timed otherwise.
    from multiprocessing import Process

    p1 = Process(target=bootstrap_user)
    p1.start()

    p2 = Process(target=bootstrap_agent)
    p2.start()
