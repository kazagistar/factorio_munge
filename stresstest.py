from bp import *

bp = Blueprint()
b = Book(content=[bp for _ in range(12)])
for i in range(5):
    b = Book(content=[b for _ in range(12)])
b.label = "Endless Nothing"

with open("outputs/endless.bp", 'w') as f:
    f.write(encode(b.export()))