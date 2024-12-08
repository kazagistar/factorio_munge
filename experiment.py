from bp import *

cc = ConstantCombinator()
for (i, (sig, typ)) in enumerate(SIGNALS):
    if i > 100:
        break
    cc.add(Signal(name=sig, type=typ), i)
bp = Blueprint("Numbers to 100", content=[cc])
print(encode(bp.export()))