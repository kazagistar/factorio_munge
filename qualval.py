import bp


lookup = bp.ConstantCombinator()
for science in ["automation", "logistic", "military", "chemical", "production", "utility", "space", "metallurgic", "electromagnetic", "agricultural", "cryogenic", "promethium"]:
    pack = science + "-science-pack"
    for mul, qual in zip((1,2,3,4,6), bp.QUALITIES):
        lookup.add(bp.Signal(name=pack, quality=qual, type="item"), mul)
print(bp.encode(bp.Blueprint(content=[lookup]).export()))
