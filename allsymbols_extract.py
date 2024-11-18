from bp import decode

if __name__ == "__main__":
    signals = []
    bp = decode(open('inputs/allsymbols.bp').read())
    entities = bp['blueprint']['entities']
    entities.sort(key=lambda e: e['position']['y'], reverse=True)
    for entity in entities:
        for section in entity['control_behavior']['sections']['sections']:
            for filter in section['filters']:
                signals.append((filter['name'], filter.get('type') or ''))
    signals.append(('signal-dot', 'virtual'))
    with open('outputs/allsymbols.csv', 'w') as out:
        for (t,n) in signals:
            out.write(f'{t},{n}\n')