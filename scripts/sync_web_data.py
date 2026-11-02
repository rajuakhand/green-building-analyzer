"""Copy the project data files into the web app folder.

The static front end in web/ reads its own copies of the CSVs so the folder can be
deployed on its own. Run this after editing anything under data/.

    python3 scripts/sync_web_data.py
"""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WEB_DATA_DIR = ROOT / "web" / "data"

FILES = ("materials.csv", "material_factors.csv")


def main() -> int:
    WEB_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name in FILES:
        source = DATA_DIR / name
        destination = WEB_DATA_DIR / name

        # The web folder keeps its own committed copy, so a source file that is
        # not tracked in git is skipped rather than breaking the deploy.
        if not source.exists():
            print(f"skipped {name}: no data/{name} in this checkout, keeping web/data/{name}")
            continue

        shutil.copyfile(source, destination)
        print(f"copied {name} -> {destination.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
