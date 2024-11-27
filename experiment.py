from bp import *

recipes = ["metallic-asteroid-crushing", "advanced-metallic-asteroid-crushing", "carbonic-asteroid-crushing", "advanced-carbonic-asteroid-crushing", "oxide-asteroid-crushing", "advanced-oxide-asteroid-crushing"]
items = ["iron-ore", "copper-ore", "coal", "sulfur", "ice", "calcite"]
chunks = ["metallic-asteroid-chunk", "carbonic-asteroid-chunk", "oxide-asteroid-chunk"]
recycles = ["metallic-asteroid-reprocessing", "carbonic-asteroid-reprocessing", "oxide-asteroid-reprocessing"]

qrecipes = ConstantCombinator(x = 0)
qitems = ConstantCombinator(x = 1)
qchunks = ConstantCombinator(x = 2)
qrecycles = ConstantCombinator(x = 3)
i = 0
for quality in QUALITIES:
    for recipe, item in zip(recipes, items):
        qrecipes.add(Signal(recipe, quality), 1<<i)
        qitems.add(Signal(item, quality), 1<<i)
        i += 1
i = 0
for quality in QUALITIES:
    for chunk,recycle in zip(chunks, recycles):
        qchunks.add(Signal(chunk, quality), 3<<i)
        qrecycles.add(Signal(recycle, quality), 3<<i)
        i += 2
bp = Blueprint(icons=["crusher", "signal-any-quality"], content=[qrecipes, qitems, qchunks, qrecycles]).export()
print(encode(bp))