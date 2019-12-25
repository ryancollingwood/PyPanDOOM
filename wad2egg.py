import math, argparse, os, sys, re
from typing import List
from omg import txdef, wad, mapedit, util
from panda3d.core import *

class Wad2Egg:
    def __init__(
            self,
            wads_to_process: List,
            output_dir: str = "export/",
            map_pattern: str = "",
    ):
        self.wads_to_process = wads_to_process
        self.output_dir = output_dir
        self.current_dir = os.getcwd()

        self.map_matcher = None
        if map_pattern:
            self.map_matcher = re.compile(map_pattern)

        self.textures_names = None
        self.texture_sizes = None

    def execute(self):
        for wad_file in self.wads_to_process:
            self.execute_wad(wad_file)

    def execute_wad(self, wad_file: str):
        input_wad = wad.WAD()
        input_wad.from_file(wad_file)

        # export textures

        for level_map in input_wad.maps.keys():
            self.execute_level(input_wad, level_map)

    def execute_level(self, input_wad, level_name):
        if self.map_matcher is not None:
            if len(self.map_matcher.findall(level_name)) == 0:
                return

        egg_file = level_name.lower()+".egg"
        print("Writing %s" % egg_file)
        edit = mapedit.MapEditor(input_wad.maps[level_name.upper()])

        # first lets get into the proper coordinate system
        v = edit.vertexes[0]
        bb_min = mapedit.Vertex(v.x, v.y)
        bb_max = mapedit.Vertex(v.x, v.y)
        for v in edit.vertexes:
            v.x = -v.x
            if bb_max.x > v.x:
                bb_max.x = v.x
            if bb_max.y > v.y:
                bb_max.y = v.y
            if bb_min.x < v.x:
                bb_min.x = v.x
            if bb_min.y < v.y:
                bb_min.y = v.y

        sectors = self.get_sectors(level_name, edit)
        vertexes = self.get_vertexes(level_name, edit)
        linedefs = self.get_linedefs(level_name, edit, vertexes)


    def add_vertex_points(self, sector_index, sectors, vertex_a, vertex_b):
        result = list()
        if sector_index > -1:
            for z in sectors[sector_index]:
                result.append(Vec3(vertex_a[0], vertex_a[1], z))
                result.append(Vec3(vertex_b[0], vertex_b[1], z))
        else:
            result.append(Vec3(vertex_a[0], vertex_a[1], 0))
            result.append(Vec3(vertex_b[0], vertex_b[1], 0))
        return result

    def write_csv(self, level_name, collection_name, items):
        if len(items) == 0:
            return
        # do this instead: https://stackoverflow.com/a/109106/2805700
        file_name = f"{self.output_dir}/{level_name}_{collection_name}.csv".lower()
        print(f"csv: {file_name}")

        headers = ["index"] + list(vars(items[0]).keys())

        with open(file_name, "w") as out:
            csv_header = ",".join(headers)
            out.write(f"{csv_header}\n")
            for i, item in enumerate(items):

                values = [str(i)] + [str(x) if x is not None else "" for x in vars(item).values()]
                values_csv = ",".join(values)
                out.write(f"{values_csv}\n")

        return file_name

    def get_sectors(self, level_name, edit):
        self.write_csv(
            level_name,
            "sectors",
            edit.sectors,
        )

        result = [Vec2(x.z_floor, x.z_ceil) for x in edit.sectors]
        return result

    def get_vertexes(self, level_name, edit):
        self.write_csv(
            level_name,
            "vertexes",
            edit.vertexes,
        )

        result = [Vec2(v.x, v.y) for v in edit.vertexes]
        return result

    def get_linedefs(self, level_name, edit, vertexes):
        self.write_csv(
            level_name,
            "linedefs",
            edit.linedefs,
        )

        return [
            (vertexes[l.vx_a], vertexes[l.vx_b]) for l in edit.linedefs
        ]




def parse_args():
    """ parse arguments out of sys.argv """

    epilog = "Example: wad2obj.py doom.wad -m 'E1*' -o /tmp"

    parser = argparse.ArgumentParser(description=__doc__, epilog=epilog)
    parser.add_argument(
            'source_wad', type=str, help='Path to the input WAD file.')
    parser.add_argument(
            '-l','--list', action='store_true', default=False,
            help="List the names of the maps in the source wad without exporting anything.")
    parser.add_argument(
            '-m','--maps', type=str, default='*', metavar='PATTERN',
            help="Pattern of maps to export (e.g. 'MAP*' or 'E?M1'). Use * as a wildcard or ? as any single character.")
    parser.add_argument(
            '-o','--output', type=str, default='.', metavar='PATH',
            help="Directory path where output files will be written.")
    parser.add_argument(
            '-c','--center', action='store_true', default=False,
            help="Translate the output vertices so the center of the map is at the origin.")
    return parser.parse_args()


def main(*args):
    args = parse_args()
    print(args)

    wads_to_process = args.source_wad.split(",")

    wad2egg = Wad2Egg(
        wads_to_process,
        args.output,
        args.maps
    )
    wad2egg.execute()


if __name__ == "__main__":
    main()
