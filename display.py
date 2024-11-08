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
    return paste

def pp(data):
    print(json.dumps(data, indent=2))

def parameter(insignal, comparator, constant, outsignal):
    r = {
                "condition": {
                    "first_signal": {
                    "type": "virtual",
                    "name": insignal
                    },
                    "constant": constant,
                    "comparator": comparator
                },
                "icon": {
                    "type": "virtual",
                    "name": outsignal
                }
            }
    if outsignal == None:
        del r["icon"]
    return r

def entity(i):
    return {
            "entity_number": i,
            "name": "display-panel",
            "position": {
                "x": i + 0.5,
                "y": 0.5
            },
            "control_behavior": {
            }
        }

MAX_INT = 2147483647
MIN_INT = -2147483648

def generate(digits, base):
    bp = decode(open('inputs/constant.txt').read())
    pp(bp)
    entities = bp['blueprint']['entities']
    entities.clear()
    for exponent in range(digits):
        if exponent == digits -1:
            insignal = 'signal-dot'
        else:
            insignal = f'signal-{exponent}'
        display = entity(digits-exponent)
        params = []
        # handle positive numbers
        for cutoff in range(base-1, 0, -1):
            scaled = cutoff * base ** exponent
            if scaled <= MAX_INT:
                params.append(parameter(insignal, '>=', scaled, 'signal-'+f'{cutoff:x}'.capitalize()))
        # handle positive "zero case"
        boundry = 10**(exponent + 1)
        if boundry < MAX_INT:
            params.append(parameter('signal-dot', '>=', boundry, 'signal-0'))
        # handle negative numbers
        for cutoff in range(base - 1, 0, -1):
            scaled = -cutoff * base ** exponent
            if scaled >= MIN_INT:
                params.append(parameter(insignal, '<=', scaled, 'signal-'+f'{cutoff:x}'.capitalize()))
        # handle negative "zero case"
        boundry = -1 * base ** (exponent + 1)
        if boundry > MIN_INT:
            params.append(parameter('signal-dot', '<=', boundry, 'signal-0'))
        # sign logic
        if (exponent != 0):
            params.append(parameter('signal-dot', '<=', -1 * base ** (exponent-1), 'shape-horizontal'))
        display['control_behavior']['parameters'] = params
        entities.append(display)
    negsign = entity(0)
    negsign['control_behavior']['parameters'] = [
        parameter('signal-dot', '<=', -1 * base ** (digits - 1), 'shape-horizontal')
    ]
    entities.append(negsign)
    return bp

if __name__ == '__main__':
    print("Decimal")
    bp = generate(digits=10, base=10)
    print(f"{encode(bp).decode()}")
    print("=======")
    print("Hex")
    bp = generate(digits=8, base=16)
    print(f"{encode(bp).decode()}")
