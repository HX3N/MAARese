import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from maa.agent.agent_server import AgentServer
from maa.toolkit import Toolkit


def main() -> None:
    import account_actions
    import battle_actions
    import dialog_actions
    import event_actions
    import flow_actions
    import gacha_actions
    import nav_actions
    import select_actions
    import watchdog

    # AgentServer's init_option ignores config/maa_option.json and only applies the given config.
    try:
        option = json.loads(Path("config/maa_option.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        option = {}
    Toolkit.init_option("./", option)

    if len(sys.argv) < 2:
        print("Usage: python main.py <socket_id>")
        print("socket_id is provided by AgentIdentifier.")
        sys.exit(1)

    socket_id = sys.argv[-1]

    AgentServer.start_up(socket_id)
    AgentServer.join()
    AgentServer.shut_down()


if __name__ == "__main__":
    main()
