from bp import *
import inspect
def calc(expression):
        
    bp = Book(f"Combinators for {inspect.getsource(expression)}", icons=[Signal("signal-X"), Signal("signal-Y")])
    x = 1
    while True:
        squares = ConstantCombinator()
        for (sig, typ) in SIGNALS:
            for quality in ['normal', 'uncommon', 'rare', 'epic', 'legendary']:
                y = expression(x)
                if y > 2147483647:
                    if len(squares.filters) > 0:
                        bp.blueprints.append(Blueprint(f"Squares of up to {y-1}", content=[squares]))
                    return bp
                squares.add(Signal(sig, quality, typ), y)
                x += 1
        bp.blueprints.append(Blueprint(f"Squares of up to {y}", content=[squares]))

if __name__ == "__main__":
    bp = calc(lambda x: x*x)
    
    with open("outputs/formulatable.bp", 'w') as f:
        f.write(encode(bp.export()))