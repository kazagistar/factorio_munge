import networkx as nx

from bp import *
from extract import getrecipes

recipes = getrecipes()

graph = nx.DiGraph()

ignore = [
    ("fluoroketone-cold","fluoroketone-hot"),
    ("coal", "carbon"),
    ("sulfur", "coal"),
    ("sulfuric-acid", "carbon"),
    ("sulfuric-acid", "steam"),
    ("sulfuric-acid", "heavy-oil"),
    ("raw-fish", "nutrients"),
    ("uranium-235", "uranium-238"),
]

recipes = getrecipes()
for name, recipe in recipes.items():
    if recipe.get('hidden'):
        continue
    if 'ingredients' not in recipe:
        continue
    if name[:6] == "empty-":
        continue
    ingredients = [Signal(name=x['name'], type=x['type']) for x in recipe["ingredients"]]
    results = [Signal(name=x['name'], type=x['type']) for x in recipe["results"]]
    for (i,r) in ((i,r) for i in ingredients for r in results):
        if (i.name, r.name) in ignore:
            continue
        if i == r:
            continue
        if "-asteroid-chunk" in r.name:
            continue
        graph.add_edge(i, r)

i = 1
linear = ConstantCombinator(desc="Ingredients < Products, loopable")
for node in nx.topological_sort(graph):
    print(node)
    linear.add(node, i)
    i += 1

i = 1
generational = ConstantCombinator(desc="Topological generations share a number")
unique_generational = ConstantCombinator(desc="Sorted by topological generations, but with unique ids")
for sublist in nx.topological_generations(graph):
    j = 1
    for node in sublist:
        generational.add(node, i)
        unique_generational.add(node, 100 * i + j)
        j += 1
    i += 1

print(encode(Book(
    label="Crafting Order",
    desc="""All items sorted such that ingredients are before products
by Kazagistar""",
    content=[
        Blueprint(label=linear.desc,
                  content=[linear]),
        Blueprint(label=generational.desc,
                  content=[generational]),
        Blueprint(label=unique_generational.desc,
                  content=[unique_generational]),
    ]).export()))