import sys
import subprocess as sub
import pathlib

CURRENT_DIRECTORY = pathlib.Path(__file__).parent.resolve()
EXECUTEABLE_PATH = sys.executable

def run():
    commands: list[list] = []

    # Backend
    backend_cmd = [f"{EXECUTEABLE_PATH}", f"{CURRENT_DIRECTORY}/src/backend/manage.py"]
    commands.append(backend_cmd)

    # Frontend
    # ...

    procs: list[sub.Popen] = []
    for cmd in commands:
        proc = sub.Popen(args=cmd)
        procs.append(proc)

    for proc in procs:
        proc.wait()
    
if __name__ == "__main__":
    run()

    
