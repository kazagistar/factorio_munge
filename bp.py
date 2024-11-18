import base64
import zlib
import json
import collections
from enum import Enum

def _loadsignals():
    collected = collections.OrderedDict()
    for line in open('inputs/allsignals.csv').readlines():
        name, type = line.split(',')
        collected[name.strip()] = type.strip()
    return collected
SIGNALS = _loadsignals()
VERSION = 562949954404356

QUALITIES = {
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
    def __init__(self, name, quality="normal"):
        self.name = name
        self.type = SIGNALS[name]
        self.quality = QUALITIES[quality]
    
    def export(self):
        base = {
            "name": self.name
        }
        if self.type:
            base["type"] = self.type
        base["quality"] = self.quality
        return base

class Book:
    def __init__(self, label=None, desc=None, icons=[], content=[]):
        self.label = label
        self.desc = desc
        self.blueprints = []
        self.icons = []
        self.extra = {}
        for item in icons:
            if isinstance(item, Signal):
                self.icons.append(item)
            else:
                raise Exception(f"Invalid book icon {item}")
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
            if isinstance(item, Signal):
                self.icons.append(item)
            else:
                raise Exception(f"Invalid book icon {item}")
        for item in content:
            if isinstance(item, Entity):
                self.entities.append(item)
            else:
                raise Exception(f"Invalid book content {item}")

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
            "entity_number": self.entity_number,
            "position": {
                "x": self.x,
                "y": self.y,
            }
        }
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
        if not isinstance(key, Signal):
            key = Signal(key)
        self.filters[key] = value

    def export(self):
        base = super().export()
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

if __name__ == "__main__":
    print(json.dumps(decode(open("inputs/example6.bp").read()), indent=2))

    result = Book("Empty book", "No longer!",
                  icons=[Signal("signal-2"), Signal('constant-combinator')],
                  content=[
                      Blueprint(content=[
                          ConstantCombinator("Some numbers for ya", signals=[
                              (Signal("constant-combinator", quality="rare"), 10),
                              ("signal-2", -3)
                          ])])]).export()
    print(json.dumps(result, indent=2))
    print(encode(result))
    print(Signal('signal-2').export())
