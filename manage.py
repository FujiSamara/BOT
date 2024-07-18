import sys
import subprocess as sub
import pathlib

CURRENT_DIRECTORY = pathlib.Path(__file__).parent.resolve()
EXECUTEABLE_PATH = sys.executable


def run():
    run_type = "APP"
    if len(sys.argv) > 1:
        run_type = sys.argv[1]

    commands: list[list] = []

    # Backend
    backend_cmd = [
        f"{EXECUTEABLE_PATH}",
        "-Xfrozen_modules=off",
        f"{CURRENT_DIRECTORY}/src/backend/manage.py",
    ]
    if run_type != "FRONTEND":
        commands.append(backend_cmd)

    # Frontend
    frontend_cmd = [
        "npm",
        "--prefix",
        f"{CURRENT_DIRECTORY}/src/frontend",
        "run",
        "dev",
    ]
    if run_type != "BACKEND":
        commands.append(frontend_cmd)

    procs: list[sub.Popen] = []
    for cmd in commands:
        proc = sub.Popen(args=cmd)
        procs.append(proc)

    for proc in procs:
        proc.wait()


if __name__ == "__main__":
    run()
