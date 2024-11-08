import base64
import zlib
import json

def decode(paste):
    encoded = paste[1:]
    zipped = base64.b64decode(encoded)
    text = zlib.decompress(zipped)
    blueprint = json.loads(text)
    return blueprint

def encode(blueprint):
    text = json.dumps(blueprint)
    zipped = zlib.compress(text.encode('utf-8'))
    encoded = base64.b64encode(zipped)
    paste = b'0' + encoded
    return paste.decode()

def newbp():
    return {
                "blueprint": {
                    "icons":[],
                    "entities": [],
                    "item": "blueprint",
                    "version": 562949954338818
                }
            }

def pp(data):
    print(json.dumps(data, indent=2))

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
            
    sections = []
    chunks = [signals[0:200], signals[200:400], signals[400:]] #hardcoded lol
    for (ci, chunk) in enumerate(chunks, start=1):
        section = []
        i = 1
        for (sig, typ) in chunk:
            for quality in ['normal', 'uncommon', 'rare', 'epic', 'legendary']:
                filter = {
                    "index": i,
                    "name": sig,
                    "quality": quality,
                    "comparator": "=",
                    "count": 1,
                }
                if typ:
                    filter["type"] = typ
                section.append(filter)
                i += 1
        sections.append({
            "index": ci,
            "filters": section
        })

    entity = {
        "entity_number": 1,
        "name": "constant-combinator",
        "position": {"x": 0.5, "y": 0.5},
        "control_behavior": {"sections": { "sections": sections}}
    }
    bp = newbp()
    bp['blueprint']['entities'].append(entity)

    with open("outputs/allsymbols.bp", 'w') as f:
        f.write(encode(bp))