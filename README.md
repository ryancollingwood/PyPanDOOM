# PyPanDOOM

Export DOOM levels from WAD to .obj, then convert to .egg to view in the Panda3d engine.

To export levels to .obj and textures to PNG
`python export_level.py -o "export/" wad/DOOM2.wad`

To convert .obj level to .egg for Panda3d
`python obj2egg.py export/map01.obj`

To fly around in MAP01
`python map_viewer.py map01`

Code lifted and hacked to death from:
- export_level.py - https://github.com/jminor/omgifol/blob/master/demo/wad2obj.py
- obj2egg.py - http://panda3d.org/phpbb2/viewtopic.php?t=3378

# TODO
## Cleanup
`export_level.py`
 - Refactor and Document changes
 - Mostly around transparency and tile stamps
`obj2egg.py`
 - Refactor and Document changes
 - Collision mask hard-coded values :(
`map_viewer.py`
 - Make collision toggleable
 
 ## Later
 - Some geometry wierdness in exporting to fix
 - Export and apply Lighting
 - Thing(s), player spawn point a priority
