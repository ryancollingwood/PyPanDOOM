CALL .venv/Scripts/activate.bat
python export_level.py -o "export/" -m E1M1 wad/DOOM.wad
python obj2egg.py export/e1m1.obj
python map_viewer.py e1m1
CALL deactivate