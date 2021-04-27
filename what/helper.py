from pathlib import Path, PurePosixPath, PureWindowsPath
from platform import uname
import os
appdata = PureWindowsPath(os.getenv('APPDATA'))

if 'Microsoft' in uname().release:
    if Path.cwd().drive == "":
        appdata = Path(appdata.relative_to(Path(appdata.drive)/'\\'))
        appdata = Path('/mnt/c/') / appdata


data_dir = appdata / 'league-picker'

def run():
    if not data_dir.exists():
        data_dir.mkdir()
    if not (data_dir/'.tmp').exists():
        (data_dir/'.tmp').mkdir()
    if not (data_dir/'lists').exists():
        (data_dir/'lists').mkdir()
    champ_file = Path(__file__).parent / "champ_data.json"
    data_file = Path(__file__).parent / "game_data.json"
    champ_data = data_dir / "champ_data.json"
    data_data = data_dir / "game_data.json"
    if not champ_data.exists():
        champ_data.touch()
        champ_data.write_text(champ_file.read_text())

    if not data_data.exists():
        data_data.touch()
        data_data.write_text(data_file.read_text())

    champ_file = champ_data
    data_file = data_data

champ_file = data_dir / "champ_data.json"
data_file = data_dir / "game_data.json"
