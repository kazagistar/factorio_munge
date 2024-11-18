from bp import *

if __name__ == "__main__":
    allone = ConstantCombinator()
    increasing = ConstantCombinator()
    squares = ConstantCombinator()
    squareshift = ConstantCombinator()
    qgrouped = ConstantCombinator()
    i = 1
    qi = 1
    for (sig, typ) in SIGNALS:
        for quality in ['normal', 'uncommon', 'rare', 'epic', 'legendary']:
            allone.add(Signal(sig, quality, typ), 1)
            increasing.add(Signal(sig, quality, typ), i)
            qgrouped.add(Signal(sig, quality, typ), qi)
            squares.add(Signal(sig, quality, typ), i*i)
            squareshift.add(Signal(sig, quality, typ), (i+1)*(i+1))
            i += 1
        qi += 1
    bp = Book("Every Signal Combinators", icons=[Signal("signal-X")], content=[
        Blueprint("Every Signal = 1", content=[allone]),
        Blueprint("Every Signal w/ unique natural number", content=[increasing]),
        Blueprint("Every Signal quality grouped", "Same signals with different qualities all have the same number", content=[qgrouped])
    ])
    with open("outputs/allsymbols.bp", 'w') as f:
        f.write(encode(bp.export()))
    #print(encode(Blueprint("Every Signal squared", content=[squares]).export()))
    print(encode(Blueprint("Every Signal squared shifted up one", content=[squareshift]).export()))