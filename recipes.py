from bp import *
from extract import getrecipes

if __name__ == "__main__":
    recipes = getrecipes()
    time = ConstantCombinator(desc="Ticks to craft recipe (rounded to nearest tick)")
    for name, recipe in recipes.items():
        if recipe.get('hidden'):
            continue
        ticks = round(recipe.get("energy_required", 0.5) * 60)
        sig = Signal(recipe['name'], type=recipe['type'])
        time.add(sig, ticks)
    bp = Blueprint("Recipe Craft Ticks", "by Kazagistar", icons=[Signal("signal-info"), Signal("item-on-ground")], content=[time])
    print(encode(bp.export()))