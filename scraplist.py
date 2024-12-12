import bp

lookup = bp.ConstantCombinator()
for scrap in ["iron-gear-wheel", "solid-fuel", "concrete", "ice", "battery", "steel-plate", "stone", "copper-wire", "advanced-circuit", "processing-unit", "low-density-structure", "holmium-ore"]:
    for qual in bp.QUALITIES:
        lookup.add(bp.Signal(name=scrap, quality=qual, type="item"), 1)
print(bp.encode(bp.Blueprint(content=[lookup]).export()))
