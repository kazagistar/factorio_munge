from bp import *

dc = DeciderCombinator(outputs=[r("signal-X")])

for i in range(100000):
    dc.conditions.append([[r("signal-X"), '=',  i]])

print(encode(Blueprint(content=[dc]).export()))
