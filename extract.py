""" Read and cache the contents of the logs, extracted with the mod 'Data Raw Serpent' which dumps full factorio state to a log file"""

import os
import json

def _first_valid(*paths):
    for path in paths:
        expanded = os.path.expandvars(path)
        if os.path.exists(expanded):
            return expanded

def _run_raw_dump(exe=None):
    if not exe:
        exe = _first_valid(
            r"C:\Program Files (x86)\Steam\steamapps\common\Factorio\bin\x64\factorio.exe",
            r"C:\Program Files\Factorio\bin\x64\factorio.exe",
            # TODO add OSX and Linux options properly... idk what the actual path to the executable is on those platforms
        )
    import subprocess
    subprocess.check_call([exe, "--dump-data"])

def _open_raw_dump(userdir=None):
    if userdir:
        return open(os.path.join(userdir, "script-output", "data-raw-dump.json"))
    file = _first_valid(
        f"%APPDATA%\Factorio\script-output\data-raw-dump.json",
        f"$HOME/Library/Application Support/factorio/script-output/data-raw-dump.json",
        f"$HOME/.factorio/script-output/data-raw-dump.json"
    )
    if file == None:
        raise Exception("Unsupported OS, provide folder manually")
    return open(file)

def _fresh_raw(userdir=None, exe=None):
    _run_raw_dump(exe)
    raw = json.load(_open_raw_dump(userdir))
    return raw

def getrecipes(userdir=None, exe=None, cachedir='outputs'):
    recipe_cache_file = os.path.join(cachedir, "recipes.cache.json")
    try:
        return json.load(open(recipe_cache_file))
    except FileNotFoundError:
        recipes = _fresh_raw()['recipe']
        json.dump(recipes, open(recipe_cache_file, 'w'), indent=2)
        return recipes

if __name__ == '__main__':
    recipes = getrecipes()
    print(f"Loaded and cached {len(recipes)} recipes")
    categories = set()
    for _, recipe in recipes.items():
        categories.add(recipe.get('category'))
    print(categories)
