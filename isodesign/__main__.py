from subprocess import run
import sys
from pathlib import Path

from threading import Thread
import requests

import isodesign

def get_last_version():
    """Get last IsoDesign version."""
    try:
        isodesign_path = Path(isodesign.__file__).parent
        # Get the version from testpypi
        response = requests.get('https://test.pypi.org/simple/ isodesign')
        latest_version = response.json()['info']['version']
        with open(str(Path(isodesign_path, "last_version.txt")), "w") as f:
            f.write(latest_version)
    except Exception:
        pass

def main():
    """The main routine"""

    thread = Thread(target=get_last_version)
    thread.start()
    path_to_app = Path(isodesign.__file__).parent
    path_to_app = path_to_app / "ui/Upload_data.py"
    run(["streamlit", "run", str(path_to_app)])


if __name__ == "__main__":
    sys.exit(main())