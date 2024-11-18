from bp import *

def extract_signals():
    signals = []
    bp = decode(open('inputs/allsymbols.bp').read())
    entities = bp['blueprint']['entities']
    entities.sort(key=lambda e: e['position']['y'], reverse=True)
    for entity in entities:
        for section in entity['control_behavior']['sections']['sections']:
            for filter in section['filters']:
                signals.append((filter['name'], filter.get('type') or ''))
    signals.append(('signal-dot', 'virtual'))
    return signals

if __name__ == "__main__":
    signals = extract_signals()
    with open('outputs/allsymbols.csv', 'w') as out:
        for (t,n) in signals:
            out.write(f'{t},{n}\n')
            
    allone = ConstantCombinator()
    increasing = ConstantCombinator()
    qgrouped = ConstantCombinator()
    i = 1
    qi = 1
    for (sig, _) in signals:
        for quality in ['normal', 'uncommon', 'rare', 'epic', 'legendary']:
            allone.add(Signal(sig, quality), 1)
            increasing.add(Signal(sig, quality), i)
            qgrouped.add(Signal(sig, quality), qi)
            i += 1
        qi += 1
    Book("Every Signal Combinators", icons=[Signal("signal-X")], content=[
        Blueprint("Every Signal = 1", content=[allone]),
        Blueprint("Every Signal w/ unique natural number", content=[increasing]),
        Blueprint("Every Signal quality grouped", "Same signals with different qualities all have the same number", content=[qgrouped])
    ])
 
    with open("outputs/allsymbols.bp", 'w') as f:
        f.write(encode(bp))