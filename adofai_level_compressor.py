import os, sys
import re, json
import math
import argparse
from typing import Any, Literal, TypedDict, NotRequired

# import adofaipy

version: str = "0.1.0"


# deal with type notations
type Settings = dict[str, Any]

class Action(TypedDict):
    floor: int
    eventType: str
class ImageDecoration(TypedDict):
    eventType: Literal["AddDecoration"]
    decorationImage: str
    depth: int
class TextDecoration(TypedDict):
    eventType: Literal["AddText"]
    decText: str
    depth: int
class ObjectDecoration(TypedDict):
    eventType: Literal["AddObject"]
    objectType: Literal["Floor", "Planet"]
class ParticleDecoration(TypedDict):
    eventType: Literal["AddParticle"]
type Decoration = ImageDecoration | TextDecoration | ObjectDecoration | ParticleDecoration

class Level(TypedDict):
    angleData: NotRequired[list[float]]
    pathData: NotRequired[str]
    settings: Settings
    actions: list[Action]
    decorations: list[Decoration]


def convert_level_to_valid_json_format(content: str, /) -> Level:
    # The code of this function is based on code that is copied from https://github.com/M1n3c4rt/adofaipy by M1n3c4rt, at 2026-06-16.
    # The original code is licensed under the MIT license. For more information, see: https://opensource.org/licenses/MIT

    # Copyright 2023 M1n3c4rt
    # Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    # The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    # THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    # split contents
    splited = re.split(r"(?<!\\)(?:\\\\)*(\")", content)

    # for each content after a value and before a key:
    for i in range(len(splited)):
        if i % 4 == 0:
            splited[i] = re.sub(r"(\n|\t)", "", splited[i]) # remove \n and \t
            splited[i] = re.sub(r"\,(( *)(\]|\}))", "\\3", splited[i]) # remove extra commas before right brackets
            splited[i] = re.sub(r"(\]|\})(\[|\{)", "\\1,\\2", splited[i]) # add missing commas between brackets
        elif i % 4 == 2:
            splited[i] = re.sub("\n", "\\\\r", splited[i]) # convert \n (was \r) to \\r
            splited[i] = re.sub("\t", "", splited[i]) # remove \t
    
    # and all of those steps above is to make this an VALID JSON DATA... WELL DONE 7TH BEAT GAMES.
    return json.loads("".join(splited))


parser = argparse.ArgumentParser(
    description = "compress *.adofai file",
    # description = "",
    epilog = "TL;DR: just drag the *.adofai file onto this exe",
    exit_on_error = False
)
parser.add_argument(
    "-v", "--version", action="version", version=f"%(prog)s {version}"
)
path_data_group = parser.add_argument_group(
    "pathData", 
    "if and how to convert angleData to pathData"
)
path_data_exclusive_group = path_data_group.add_mutually_exclusive_group()
path_data_exclusive_group.set_defaults(path_data=5)
path_data_exclusive_group.add_argument(
    "-a", "--angle-data", dest="path_data", action="store_const", const=0,
    help="do not convert"
)
path_data_exclusive_group.add_argument(
    "-p", "--path-data", dest="path_data", action="store_const", const=1,
    help="convert angleData to pathData (directions and midspins only; keep angleData unchanged if fails)"
)
path_data_exclusive_group.add_argument(
    "-5", "--pentagon", dest="path_data", action="store_const", const=5,
    help="in addition to the above, try to convert pentagon corners; this is default behavior"
)
path_data_exclusive_group.add_argument(
    "-7", "--heptagon", dest="path_data", action="store_const", const=7,
    help="in addition to the above, try to convert heptagon corners; this would also set legacySpriteTiles to true, which do causes some problems, but can at least keeps the rhythm same. USE THIS AT YOUR OWN RISK"
)
path_data_exclusive_group.add_argument(
    "-d", "--dodecagon", dest="path_data", action="store_const", const=12,
    help="in addition to the above, try to convert dodecagon corners; not sure if it's intentional, but 9 in pathData behaves like a upside-down dodecagon corner. USE THIS AT YOUR OWN RISK"
)
parser.add_argument(
    "-s", "--safe", action="store_true",
    help="keep unused data (for example, track settings for planet objects)"
)
parser.add_argument(
    "-f", "--force", action="store_true",
    help="overwrite existing file; there will be NO WARNING if you leave output blank"
)
file_path_group = parser.add_argument_group(
    "Files"
)
file_path_group.add_argument(
    "input", 
    help="the *.adofai file to load and compresses level"
)
file_path_group.add_argument(
    "output", nargs="?", 
    help="the *.adofai file to save the compressed level; leave this blank will save the result to *.compressed.adofai and will overwrite the old one if exist WITHOUT WARNING"
)
class Args(TypedDict):
    path_data: int
    safe: bool
    force: bool
    input: str
    output: str
args = argparse.Namespace()
args_dict: Args


with open(
    os.path.join(os.path.dirname(sys.argv[0]), "default.adofai"),
    "r", encoding="utf-8-sig"
) as default_level_file:
    default_level_json: Level = convert_level_to_valid_json_format(default_level_file.read())

setting_defaults: Settings = default_level_json["settings"].copy()
action_defaults: dict[str, Action] = {
    a["eventType"]: a for a in default_level_json["actions"]
}
decoration_defaults: dict[str, Decoration] = {
    a["eventType"]: a for a in default_level_json["decorations"]
}

setting_key_keys: list[str] = ["version"]
action_key_keys: list[str] = ["floor", "eventType"]
deco_key_keys: dict[str, list[str]] = {
    "AddDecoration": ["eventType", "decorationImage", "depth"],
    "AddText": ["eventType", "decText", "depth"],
    "AddObject": ["eventType"],
    "AddParticle": ["eventType"]
}
certain_obj_deco_only_keys: dict[str, list[str]] = {
    "Floor": [
        "trackType",
        "trackAngle",
        "trackColorType",
        "trackColor",
        "secondaryTrackColor",
        "trackColorAnimDuration",
        "trackOpacity",
        "trackStyle",
        "trackIcon",
        "trackIconAngle",
        "trackIconFlipped",
        "trackRedSwirl",
        "trackGraySetSpeedIcon",
        "trackSetSpeedIconBpm",
        "trackGlowEnabled",
        "trackGlowColor",
        "trackIconOutlines",
    ],
    "Planet": [
        "planetColorType",
        "planetColor",
        "planetTailColor",
    ],
}


ad2pd_map: dict[float, str] = {
      0: "R",  15: "p",  30: "J",  45: "E",  60: "T",  75: "o", 
     90: "U", 105: "q", 120: "G", 135: "Q", 150: "H", 165: "W", 
    180: "L", 195: "x", 210: "N", 225: "Z", 240: "F", 255: "V", 
    270: "D", 285: "Y", 300: "B", 315: "C", 330: "M", 345: "A",
}
rel_tol: float = 0
abs_tol: float = 1/128

def angle_data_to_path_data(angle_data: list[float]) -> str | None:
    path_data: str = ""
    previous_angle: float = 0
    for i, angle in enumerate(angle_data):
        if angle == 999:
            path_data += "!"
            previous_angle = (previous_angle - 180) % 360
            continue
        if angle % 360 in ad2pd_map.keys():
            path_data += ad2pd_map[angle % 360]
            previous_angle = angle % 360
            continue
        if args_dict["path_data"] >= 5:
            if math.isclose(
                (angle - previous_angle) % 360,
                (360 / 5) % 360,
                rel_tol=rel_tol, abs_tol=abs_tol
            ):
                path_data += "5"
                previous_angle = (previous_angle + (360 / 5)) % 360
                continue
            if math.isclose(
                (angle - previous_angle) % 360,
                (360 / -5) % 360,
                rel_tol=rel_tol, abs_tol=abs_tol
            ):
                path_data += "6"
                previous_angle = (previous_angle + (360 / -5)) % 360
                continue
        if args_dict["path_data"] >= 7:
            if math.isclose(
                (angle - previous_angle) % 360,
                (360 / 7) % 360,
                rel_tol=rel_tol, abs_tol=abs_tol
            ):
                path_data += "7"
                previous_angle = (previous_angle + (360 / 7)) % 360
                continue
            if math.isclose(
                (angle - previous_angle) % 360,
                (360 / -7) % 360,
                rel_tol=rel_tol, abs_tol=abs_tol
            ):
                path_data += "8"
                previous_angle = (previous_angle + (360 / -7)) % 360
                continue
        if args_dict["path_data"] >= 12:
            if math.isclose(
                (angle - previous_angle) % 360,
                (360 / -12) % 360,
                rel_tol=rel_tol, abs_tol=abs_tol
            ):
                path_data += "9"
                previous_angle = (previous_angle + (360 / -12)) % 360
                continue
        print(angle)
        print(angle_data[i-1])
        print((angle - angle_data[i-1]) % 360)
        return None
    return path_data


def remove_setting_default_value(settings: Settings) -> Settings:
    new_settings: Settings = {
        k: v for k, v in settings.items()
        if k in setting_key_keys
        or k not in setting_defaults.keys()
        or v != setting_defaults[k]
    }
    return new_settings


def remove_action_default_value(actions: list[Action]) -> list[Action]:
    new_actions: list[Action] = []
    for action in actions:
        new_actions.append({
            k: v for k, v in action.items()
            if k in action_key_keys
            or k not in action_defaults[action["eventType"]].keys()
            or v != action_defaults[action["eventType"]][k]
        }) # type: ignore
    return new_actions


def remove_decoration_default_value(decos: list[Decoration]) -> list[Decoration]:
    new_decos: list[Decoration] = []
    for deco in decos:
        new_decos.append({
            k: v for k, v in deco.items()
            if k in deco_key_keys[deco["eventType"]]
            or k not in decoration_defaults[deco["eventType"]].keys()
            or v != decoration_defaults[deco["eventType"]][k]
        }) # type: ignore
    return new_decos


def remove_object_decoration_unused_value(decos: list[Decoration]) -> list[Decoration]:
    new_decos: list[Decoration] = []
    for deco in decos:
        if deco["eventType"] != "AddObject":
            new_decos.append(deco)
            continue
        new_decos.append({
            k: v for k, v in deco.items()
            if all(
                k not in keys
                for obj_type, keys in certain_obj_deco_only_keys.items()
                if obj_type != deco.get("objectType", decoration_defaults["AddObject"]["objectType"]) # type: ignore
            )
        }) # type: ignore
    return new_decos


def show_exception(e: Exception, msg: str | None = None) -> None:
    if msg: print(msg)
    print(f"{type(e).__name__}: {str(e)}")
    input("Press Enter to continue...\n")


def main() -> int:
    if len(sys.argv) <= 1:
        parser.print_help()
        input("Press Enter to continue...\n")
        return 0
    
    global args_dict
    try:
        args_dict = vars(parser.parse_args()) # type: ignore
    except argparse.ArgumentError:
        print()
        parser.print_help()
        input("Press Enter to continue...\n")
        return 1
    # some error still raises SystemExit for some reason :/
    """
    except SystemExit:
        print()
        parser.print_help()
        input("Press Enter to continue...\n")
        return 1
    """
    
    if not args_dict.get("output"):
        args_dict["output"] = ".compressed".join(os.path.splitext(args_dict["input"]))
        # assuming we can overwrite *.compressed.adofai files
    elif os.path.isfile(args_dict["output"]) and not args_dict["force"]:
        print(f"File {args_dict["output"]} already exists.\nUse --force or -f to force overwrite file.")
        input("Press Enter to continue...\n")
        return 1
    
    try:
        with open(args_dict["input"], "r", encoding="utf-8-sig") as input_file:
            content = input_file.read()
        size_before = len(content)
        level_json = convert_level_to_valid_json_format(content)
    except Exception as e:
        show_exception(e, "Failed to load the level.")
        return 1
    
    try:
        level_json["settings"] = remove_setting_default_value(level_json["settings"])
        level_json["actions"] = remove_action_default_value(level_json["actions"])
        level_json["decorations"] = remove_decoration_default_value(level_json["decorations"])
        if args_dict["path_data"]:
            angle_data = level_json.get("angleData")
            if angle_data is not None:
                path_data = angle_data_to_path_data(angle_data)
                if path_data is not None:
                    level_json.pop("angleData")
                    level_json["pathData"] = path_data
                    if args_dict["path_data"] >= 7:
                        level_json["settings"]["legacySpriteTiles"] = True
                else:
                    print("Failed to convert angleData to pathData.\nUse the original angleData instead.")
            else:
                print("Failed to convert angleData to pathData: There is no angleData.\nDid you inputed a level that already uses pathData to store track?")
        if not args_dict["safe"]:
            level_json["decorations"] = remove_object_decoration_unused_value(level_json["decorations"])
    except Exception as e:
        show_exception(e, "Failed to compress the level (my bad).")
        return 1
    
    try:
        compressed_content = json.dumps(level_json, separators=(",", ":"))
        with open(args_dict["output"], "w", encoding="utf-8-sig") as output_file:
            size_after = output_file.write(compressed_content)
    except Exception as e:
        show_exception(e, "Failed to save the level.")
        return 1
    
    print(f"Successfully compressed the specified file by {1.0 - (size_after / size_before):.2%} and saved it to:\n{args_dict["output"]}")
    input("Press Enter to continue...\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())