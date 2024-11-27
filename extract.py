""" Read and cache the contents of the logs, extracted with the mod 'Data Raw Serpent' which dumps full factorio state to a log file"""

import os
from slpp import slpp as lua
import json

def openlog(folder=None, name="factorio-current.log"):
    if folder:
        return open(os.path.join(folder, name))

    import platform
    ostype = platform.system()
    if ostype == 'Windows':
        file = os.path.expandvars(f"%APPDATA%\Factorio\{name}")
    elif ostype == 'Darwin':
        file = os.path.expandvars(f"$HOME/Library/Application Support/factorio/{name}")
    elif ostype == 'Linux':
        file = os.path.expandvars(f"$HOME/.factorio/{name}")
    else:
        raise Exception("Unsupported OS, provide folder manually")
    return open(file)

header = "Script @__DataRawSerpent__/data-final-fixes.lua:1: "
footer =  "--[[incomplete output with shared/self-references skipped]]"
def parselog(file):
    content = file.read()
    start = content.find(header) + len(header)
    end = content.find(footer)
    everything = lua.decode(content[start:end])
    return everything

RECIPES_CACHE = 'outputs/recipes.cache'
def getrecipes():
    try:
        return json.load(open(RECIPES_CACHE))
    except FileNotFoundError:
        recipes = parselog(openlog())['recipe']
        json.dump(recipes, open(RECIPES_CACHE, 'w'), indent=2)
        return recipes

if __name__ == '__main__':
    recipes = getrecipes()
    print(f"Loaded and cached {len(recipes)} recipes")
    categories = set()
    for _, recipe in recipes.items():
        categories.add(recipe.get('category'))
    print(categories)
