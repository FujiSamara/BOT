import sys
import subprocess as sub
import pathlib
from typing import Callable

from src.server import tunnel


CURRENT_DIRECTORY = pathlib.Path(__file__).parent.resolve()
EXECUTEABLE_PATH = sys.executable


def run():
    OKBLUE = "\033[94m"
    ENDC = "\033[0m"

    # region Configuring main commands
    print(OKBLUE + "[Processes configuring started]" + ENDC)

    processes: list[list] = []

    # Backend
    backend_cmd = [
        f"{EXECUTEABLE_PATH}",
        "-Xfrozen_modules=off",
        f"{CURRENT_DIRECTORY}/src/backend/manage.py",
    ]
    if "FRONTEND" not in sys.argv:
        processes.append(backend_cmd)

    # Frontend
    frontend_cmd = [
        "npm",
        "--prefix",
        f"{CURRENT_DIRECTORY}/src/frontend",
        "run",
        "dev",
    ]
    if "BACKEND" not in sys.argv:
        processes.append(frontend_cmd)

    procs: list[sub.Popen] = []

    print(OKBLUE + "[Processes configuring completed]" + ENDC)
    # endregion

    # region Configuring and launch preLaunch tasks
    print(OKBLUE + "[Prelaunch tasks started]" + ENDC)

    pre_launch_tasks = []

    if "TUNNEL" in sys.argv:
        pre_launch_tasks.append(tunnel.run)

    run_pre_launch_tasks(pre_launch_tasks)

    print(OKBLUE + "[Prelaunch tasks completed]" + ENDC)
    # endregion

    # region Launch and waiting processes.
    print(OKBLUE + "[Processes started]" + ENDC)

    for cmd in processes:
        proc = sub.Popen(args=cmd)
        procs.append(proc)
    for proc in procs:
        proc.wait()

    print(OKBLUE + "[Processes completed]" + ENDC)
    # endregion


def run_pre_launch_tasks(tasks: list[Callable]):
    try:
        for task in tasks:
            task()
    except Exception as e:
        print(e)
        sys.exit()


if __name__ == "__main__":
    run()
