import sys
import subprocess as sub
import pathlib
from typing import Callable

from src.server import tunnel


CURRENT_DIRECTORY = pathlib.Path(__file__).parent.resolve()
EXECUTEABLE_PATH = sys.executable

OKBLUE = "\033[94m"
ENDC = "\033[0m"


class AppProcess:
    def __init__(self, name: str, args: list[str]):
        self.name = name
        self.args = args


class AppTask:
    def __init__(self, name: str, task: Callable):
        self.name = name
        self.callback = task


def run():
    # region Configuring main processes
    print(OKBLUE + "[Processes configuring started]" + ENDC)

    processes: list[AppProcess] = []

    # Backend
    backend_cmd = [
        f"{EXECUTEABLE_PATH}",
        "-Xfrozen_modules=off",
        f"{CURRENT_DIRECTORY}/src/backend/manage.py",
    ]
    if "FRONTEND" not in sys.argv:
        processes.append(AppProcess("Backend", backend_cmd))

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

    # Prelaunch tasks
    pre_launch_tasks: list[AppTask] = []

    if "TUNNEL" in sys.argv:
        pre_launch_tasks.append(AppTask("Tunnel", tunnel.run))

    run_pre_launch_tasks(pre_launch_tasks)

    # Run processes
    run_processes(processes)


def run_pre_launch_tasks(tasks: list[AppTask]):
    print(OKBLUE + "[Prelaunch tasks starting]" + ENDC)
    try:
        for task in tasks:
            print(OKBLUE + f"[Task({task.name}) starting]" + ENDC)
            task.callback()
            print(OKBLUE + f"[Task({task.name}) started]" + ENDC)
    except Exception as e:
        print(e)
        sys.exit()

    print(OKBLUE + "[Prelaunch tasks completed]" + ENDC)


def run_processes(processes: list[AppProcess]):
    print(OKBLUE + "[Processes starting]" + ENDC)
    procs: list[sub.Popen] = []

    for cmd in processes:
        print(OKBLUE + f"[Process({cmd.name}) starting]" + ENDC)
        proc = sub.Popen(args=cmd.args)
        print(OKBLUE + f"[Process({cmd.name}) started]" + ENDC)
        procs.append(proc)
    print(OKBLUE + "[Processes started]" + ENDC)

    for proc in procs:
        proc.wait()

    print(OKBLUE + "[Processes completed]" + ENDC)


if __name__ == "__main__":
    run()
