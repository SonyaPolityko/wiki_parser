#!/usr/bin/python
import sys

from project.config import INIT_REPO, JSON_NAME, NAME_PID
from project.daemon import WikiMonitorDaemon
from project.logger_config import setup_logging

setup_logging()


def run():
    daemon = WikiMonitorDaemon(NAME_PID, JSON_NAME, INIT_REPO)
    if len(sys.argv) == 2:
        if sys.argv[1] == "start":
            daemon.start()
        elif sys.argv[1] == "stop":
            daemon.stop()
        else:
            print("Неизвестная команда")
            sys.exit(2)
        sys.exit(0)
    else:
        print(f"Используйте: {sys.argv[0]} start|stop")
        sys.exit(2)


if __name__ == "__main__":
    run()
