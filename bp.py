"""
A library for writing factorio blueprints. WIP

by Kazagistar (Jakub Gedeon)
"""

import base64
import zlib
import json
import collections
import sympy

def _loadsignals():
    collected = []
    typelookup = collections.defaultdict(list)
    for line in open('inputs/allsignals.csv').readlines():
        name, type = line.split(',')
        name = name.strip()
        type = type.strip()
        collected.append((name.strip(), type.strip()))
        typelookup[name].append(type)
    return collected, typelookup
SIGNALS, SIGNALS_TYPE_LOOKUP = _loadsignals()
VERSION = 562949954404356
MIN_SIG = -2147483648
MAX_SIG = 2147483647

QUALITY_LOOKUP = {
    "normal": "normal",
    "uncommon": "uncommon",
    "rare": "rare",
    "epic": "epic",
    "legendary": "legendary",
    1: "normal",
    2: "uncommon",
    3: "rare",
    4: "epic",
    5: "legendary",
    "n": "normal",
    "u": "uncommon",
    "r": "rare",
    "e": "epic",
    "l": "legendary",
}
QUALITIES = ["normal", "uncommon", "rare", "epic", "legendary"]
SPECIAL_SIGNALS = ["signal-each", "signal-everything", "signal-anything"]

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

def pp(data):
    print(json.dumps(data, indent=2))

def indexedExport(unindexed, start=1):
    out = []
    for i, exported in enumerate(unindexed, start = start):
        exported['index'] = i
        out.append(exported)
    return out

class Signal:
    def __init__(self, name, quality="normal", type=None):
        self.name = name
        self.quality = QUALITY_LOOKUP[quality]
        if name in SPECIAL_SIGNALS:
            self.type = 'virtual'
            return
        if type == None:
            candidates = SIGNALS_TYPE_LOOKUP[self.name]
            if len(candidates) == 1:
                self.type = candidates[0]
            elif 'item' in candidates:
                self.type = 'item'
            elif len(candidates) == 0:
                raise Exception(f"Signal {name} not found")
            else:
                raise Exception(f"Ambiguous type for signal {name}")
        else:
            self.type = type
    
    def export(self):
        base = {
            "name": self.name
        }
        if self.type:
            base["type"] = self.type
        base["quality"] = self.quality
        return base
    
    def __eq__(self, other):
        return self.name == other.name and self.quality == other.quality and self.type == other.type
    
    def __repr__(self):
        return f"Signal(name={self.name}{f', quality={self.quality}' if self.quality != 'normal' else ''}{f', type={self.type}' if self.type != 'item' else ''})"

    @classmethod
    def convert(cls, src):
        if isinstance(src, cls):
            return src
        else:
            return cls(src)
    


class Book:
    def __init__(self, label=None, desc=None, icons=[], content=[]):
        self.label = label
        self.desc = desc
        self.blueprints = []
        self.icons = []
        self.extra = {}
        for item in icons:
            self.icons.append(Signal.convert(item))
        for item in content:
            if isinstance(item, Book) or isinstance(item, Blueprint):
                self.blueprints.append(item)
            else:
                raise Exception(f"Invalid book content {item}")
            
    def export(self):
        base = {
            "item": "blueprint-book",
            # seems optional
            "version": VERSION,
        }
        if self.label is not None:
            base["label"] = self.label
        if self.desc is not None:
            base["description"] = self.desc
        if self.blueprints:
            base["blueprints"] = indexedExport((bp.export() for bp in self.blueprints), start=0)
        if self.icons:
            base["icons"] = indexedExport({'signal': icon.export()} for icon in self.icons)
        if self.extra:
            for k, v in self.extra.items():
                base[k] = v
        return {"blueprint_book": base}

class EntityList(list):
    def __init__(self, iterable=[]):
        self.max = 0
        super(EntityList, self).__init__(self.id(item) for item in iterable)

    def id(self, item):
        if hasattr(item, 'entity_number'):
            number = item.entity_number
            if self.max <= number:
                self.max = number
            return item
        else:
            self.max += 1
            item.entity_number = self.max
            return item
        
    def __setitem__(self, index, item):
        super().__setitem__(index, self.id(item))

    def insert(self, index, item):
        super().insert(index, self.id(item))

    def append(self, item):
        super().append(self.id(item))

    def extend(self, other):
        raise NotImplemented("Entity disambiguation")


class Blueprint:
    def __init__(self, label=None, desc=None, icons=[], content=[]):
        self.label = label
        self.desc = desc
        self.entities = EntityList()
        self.icons = []
        self.extra = {}

        for item in icons:
            self.icons.append(Signal.convert(item))
        for item in content:
            if isinstance(item, Entity):
                self.entities.append(item)
            else:
                raise Exception(f"Invalid blueprint content {item}")

    def export(self):
        base = {
            "item": "blueprint",
            # seems optional
            "version": VERSION,
        }
        if self.label is not None:
            base["label"] = self.label
        if self.desc is not None:
            base["description"] = self.desc
        base["entities"] = [e.export() for e in self.entities]
        if self.icons:
            base["icons"] = indexedExport({'signal': icon.export()} for icon in self.icons)
        if self.extra:
            for k, v in self.extra.pairs():
                base[k] = v
        return {"blueprint": base}

class Entity:
    def __init__(self, name, x=0, y=0):
        self.name = name
        self.x = x
        self.y = y
        self.extra = {}

    def export(self):
        base = {
            "name": self.name,
            "position": {
                "x": self.x,
                "y": self.y,
            }
        }
        if hasattr(self, 'entity_number'):
            base["entity_number"] = self.entity_number
        if self.extra:
            for k, v in self.extra.pairs():
                base[k] = v
        return base

class ConstantCombinator(Entity):
    def __init__(self, desc=None, x=0, y=0, signals=[]):
        super().__init__("constant-combinator", x, y)
        self.desc = desc
        self.filters = collections.OrderedDict()
        for key, value in signals:
            self.add(key, value)

    def add(self, key, value):
        self.filters[Signal.convert(key)] = value

    def export(self):
        base = super().export()
        if self.desc:
            base['description'] = self.desc
        if self.filters:
            sections = []
            section = None
            for key, value in self.filters.items():
                if section == None:
                    section = []
                    sections.append(section)
                filterbase = key.export()
                filterbase['index'] = len(section) + 1
                filterbase['comparator'] = '='
                filterbase['count'] = value
                section.append(filterbase)
                if len(section) == 1000:
                    section = None
        
        base["control_behavior"] = {"sections": { "sections": indexedExport({'filters': section} for section in sections)}}
        return base

class _ColoredSignal:
    """
    Helper class for making decider combinator expressions
    """
    def __init__(self, signal, colors='rg'):
        self.signal = Signal.convert(signal)
        self.colors = colors

    def toSympy(self):
        if len(self.colors) == 1:
            return self._monocolorToSympy(self.colors)
        elif len(self.colors) == 2:
            return self._monocolorToSympy('r') + self._monocolorToSympy('g')
        
    def _monocolorToSympy(self, color):
        return sympy.Symbol(f"{color}\{self.signal.name}\{self.signal.quality}\{self.signal.type}", integer=True)

    def _otherToSympy(_, other):
        if isinstance(other, _ColoredSignal):
            return other.toSympy()
        elif isinstance(other, str):
            return _ColoredSignal(other).toSympy()
        else:
            return other

    def __lt__(self, other):
        return self.toSympy() < self._otherToSympy(other)
    def __gt__(self, other):
        return self.toSympy() > self._otherToSympy(other)
    def __le__(self, other):
        return self.toSympy() <= self._otherToSympy(other)
    def __ge__(self, other):
        return self.toSympy() >= self._otherToSympy(other)
    def __eq__(self, other):
        return sympy.Equality(self.toSympy(), self._otherToSympy(other))
    def __ne__(self, other):
        return sympy.Unequality(self.toSympy(), self._otherToSympy(other))
    
    def __repr__(self):
        return f"{self.colors}({self.signal})"
    
    @classmethod
    def fromSympy(cls, symbol):
        if symbol.func == sympy.Symbol:
            color, name, quality, type = str(symbol).split('\\')
            return _ColoredSignal(Signal(name, quality, type or None), color)
        elif symbol.func == sympy.Add:
            a = cls.fromSympy(symbol.args[0])
            b = cls.fromSympy(symbol.args[0])
            if a.signal != b.signal:
                raise ValueError(f"Symbol mismatch, {a} != {b}")
            return _ColoredSignal(a.signal)
        elif isinstance(symbol, sympy.Integer):
            return int(round(symbol.evalf()))
        else:
            raise ValueError(f"Unknown leaf symbol {symbol}")

def r(signal):
    return _ColoredSignal(signal, 'r')
def g(signal):
    return _ColoredSignal(signal, 'g')
def rg(signal):
    return _ColoredSignal(signal, 'rg')

class DeciderCombinator(Entity):
    def __init__(self, desc=None, x=0, y=0, conditions=None, outputs=[]):
        super().__init__("decider-combinator", x, y)
        self.desc = desc
        self.conditions = self._parse_dnf(sympy.to_dnf(sympy.simplify(conditions)))
        self.outputs = outputs
        self.check()

    def addConditions(self, expr):
        raise Exception("Not supported yet cause doing it properly is like... hard lol")

    def addOutput(self, rgsig, value=None):
        if value:
            self.outputs.append((rgsig, value))
        else:
            self.outputs.append(rgsig)
        self.check()


    def _parse_dnf(self, expr):
        # If expression proves entirely false via simplification, just get rid of it
        try:
            if not expr:
                return []
        except TypeError:
            pass
        return self._parse_or(expr)
    
    def _parse_or(self, expr):
        if expr.func != sympy.Or:
            return [self._parse_and(expr)]
        else:
            return self._parse_or(expr.args[0]) + self._parse_or(expr.args[1])
    def _parse_and(self, expr):
        if expr.func != sympy.And:
            return [self._parse_comp(expr)]
        else:
            return self._parse_and(expr.args[0]) + self._parse_and(expr.args[1])
    def _parse_comp(self, expr):
        if expr.func in self._sympy2comparator:
            a = _ColoredSignal.fromSympy(expr.args[0])
            b = _ColoredSignal.fromSympy(expr.args[1])
            c = self._sympy2comparator[expr.func]
            if isinstance(b, _ColoredSignal) and b.signal.name in SPECIAL_SIGNALS and a.signal.name not in SPECIAL_SIGNALS:
                return [b, c, a]
            else:
                return [a, c, b]
        else:
            raise ValueError(f"Weird expression {sympy.srepr(expr)}")

    _sympy2comparator = {
        sympy.LessThan: '≤',
        sympy.StrictLessThan: '<',
        sympy.GreaterThan: '≥',
        sympy.StrictGreaterThan: '>',
        sympy.Equality: '=',
        sympy.Unequality: '≠',
    }

    def check(self):
        inwild = set()
        for andexpr in self.conditions:
            for l,_,r in andexpr:
                if l.signal.name in SPECIAL_SIGNALS:
                    inwild.add(l.signal.name)
                    if isinstance(r, _ColoredSignal):
                        if l.signal.name == 'signal-each':
                            if r.signal.name in ['signal-anything', 'signal-everything']:
                                raise Exception("Each cannot be in the same clause as other wildcards")
                        else:
                            if r.signal.name in SPECIAL_SIGNALS:
                                raise Exception(f"{l.signal.name} cannot be in the same clause as any wildcards")
        outwild = set()
        for i, output in enumerate(self.outputs):
            # first some repair logic, why not have it here I guess
            if isinstance(output, str) or isinstance(output, Signal):
                output = rg(output)
                self.outputs[i] = output
            if isinstance(output, _ColoredSignal):
                if output.signal.name in SPECIAL_SIGNALS:
                    outwild.add(output.signal.name)
                continue
            if not isinstance(output, collections.abc.Sequence) or len(output) != 2:
                raise ValueError(f"Outputs must be formatted as a colored signal (for repeat output), or a list with a colored signal and a value (for constant output)")
            if isinstance(output[0], str) or isinstance(output[0], Signal):
                output[0] = rg(output[0])
            if not isinstance(output[0], _ColoredSignal) or not isinstance(output[1], int):
                raise ValueError(f"Outputs must be formatted as a colored signal (for repeat output), or a list with a colored signal and a value (for constant output)")
            outwild.add(output[0].signal.name)
        if 'signal-each' in inwild and 'signal-everything' in outwild:
            raise ValueError("Cannot mix each on input and everything on output")
        if 'signal-each' in outwild and not 'signal-each' in inwild:
            raise ValueError("Cannot output each without an each condtion")
        
    def export(self):
        base = super().export()
        if self.desc:
            base['description'] = self.desc

        conditions = []
        for andexpr in self.conditions:
            prev_or = True
            for first, comp, second in andexpr:
                c = {
                    "first_signal": first.signal.export(),
                    "comparator": comp,
                }
                red = "r" in first.colors
                green = "g" in first.colors
                if not red or not green:
                    c["first_signal_networks"] = {
                        'red': red,
                        'green': green,
                    }
                if not prev_or:
                    c["compare_type"] = "and"
                prev_or = False
                if isinstance(second, int):
                    c["constant"] = second
                else:
                    c["second_signal"] = second.signal.export()
                    red = "r" in first.colors
                    green = "g" in first.colors
                    if not red or not green:
                        c["second_signal_networks"] = {
                            'red': red,
                            'green': green,
                        }
                conditions.append(c)
        outputs = []
        for output in self.outputs:
            if isinstance(output, collections.abc.Sequence):
                sig, val = output
                o = {
                    "signal": sig.signal.export(),
                    "copy_count_from_input": False
                }
                if val != 1:
                    o["constant"] = val
            else:
                sig = output
                o = {
                    "signal": sig.signal.export()
                }
            red = "r" in sig.colors
            green = "g" in sig.colors
            if not red or not green:
                o["networks"] = {
                    'red': red,
                    'green': green,
                }
            outputs.append(o)
        base["control_behavior"] = { "decider_conditions": {
            "conditions": conditions,
            "outputs": outputs,
        }}
        return base

if __name__ == "__main__":
    decider = DeciderCombinator(conditions=~(r("signal-each") != 10) & (r("signal-X") == 10) | (g("signal-X") == rg("signal-anything")),
                                outputs=["signal-X", ["signal-X", 2]])
    bp = Blueprint(icons=["decider-combinator"], content=[decider]).export()
    print(encode(bp))
