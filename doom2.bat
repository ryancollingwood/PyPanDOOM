CALL .venv/Scripts/activate.bat
python export_level.py -o "export/" -m MAP01 wad/DOOM2.wad
python obj2egg.py export/map01.obj
python map_viewer.py map01
CALL deactivate