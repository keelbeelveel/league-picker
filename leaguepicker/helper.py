from pathlib import Path, PurePosixPath, PureWindowsPath
from platform import uname
import os

if 'Microsoft' in uname().release and False:
    appdata = PureWindowsPath(os.getenv('APPDATA'))
    if Path.cwd().drive == "":
        appdata = Path(appdata.relative_to(Path(appdata.drive)/'\\'))
        appdata = Path('/mnt/c/') / appdata
else:
    appdata = Path(__file__).parent.parent / 'stored-data'
    if not appdata.exists():
        appdata.mkdir()


data_dir = Path(appdata)

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

def get_data_dir(userid):
    user_dir = data_dir / f'{userid}'
    if not user_dir.exists():
        user_dir.mkdir()
    if not (user_dir/'.tmp').exists():
        (user_dir/'.tmp').mkdir()
    if not (user_dir/'lists').exists():
        (user_dir/'lists').mkdir()
    return user_dir

def get_champ_file(userid):
    user_dir = get_data_dir(userid)
    user_champ_file = user_dir / "champ_data.json"
    if not user_champ_file.exists():
        user_champ_file.touch()
        user_champ_file.write_text(champ_file.read_text())
    return user_champ_file

def get_data_file(userid):
    user_dir = get_data_dir(userid)
    user_data_file = user_dir / "game_data.json"
    if not user_data_file.exists():
        user_data_file.touch()
        user_data_file.write_text(data_file.read_text())
    return user_data_file
