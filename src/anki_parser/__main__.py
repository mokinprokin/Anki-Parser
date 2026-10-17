import os
import subprocess
import sys
from pathlib import Path

from anki_parser.core.logger import logger
from anki_parser.core.toast import notifier

STARTUP_SCRIPT_NAME = "AnkiClipboardAgent.vbs"
WORKER_MODULE = "anki_parser.worker"


def get_windows_startup_dir() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable is missing.")
    return (
        Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    )


def register_in_startup(src_dir: Path) -> Path:
    startup_dir = get_windows_startup_dir()
    vbs_path = startup_dir / STARTUP_SCRIPT_NAME

    python_exe = Path(sys.executable)
    pythonw_exe = python_exe.with_name("pythonw.exe")
    target_exe = pythonw_exe if pythonw_exe.exists() else python_exe

    vbs_content = (
        'Set WshShell = CreateObject("WScript.Shell")\n'
        f'WshShell.CurrentDirectory = "{src_dir}"\n'
        f'WshShell.Run """{target_exe}"" -m {WORKER_MODULE}", 0, False\n'
    )

    vbs_path.write_text(vbs_content, encoding="utf-8")
    logger.info("Registered startup script at: %s", vbs_path)
    return vbs_path


def spawn_silent_worker(vbs_path: Path) -> None:
    subprocess.Popen(
        ["wscript.exe", str(vbs_path)],
        creationflags=subprocess.CREATE_NO_WINDOW,
        close_fds=True,
    )
    logger.info("Background worker spawned successfully.")


def main() -> None:
    src_dir = Path(__file__).resolve().parent.parent

    vbs_path = register_in_startup(src_dir=src_dir)
    spawn_silent_worker(vbs_path=vbs_path)
    notifier.notify(
        "Anki Agent Installed", "Added to Windows Startup and running in background."
    )


if __name__ == "__main__":
    main()
