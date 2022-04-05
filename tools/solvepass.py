from z3 import *

multipliers = [
    0x0049, 0x0061, 0x000d, 0x0029,
    0x0043, 0x0065, 0x0059, 0x008b,
    0x0047, 0x0053, 0x003b, 0x00b5,
    0x007f, 0x00a3, 0x0067, 0x00a3,
    0x0095, 0x00c1, 0x00d3, 0x0097
]

offsets = [
    0x18df, 0x13eb, 0x11ef, 0x1145,
    0x12df, 0x0dfd, 0x13af, 0x149f,
    0x0fef, 0x0fb5, 0x0e75, 0x11fb,
    0x1237, 0x125f, 0x107b, 0x1951,
    0x1b47, 0x151f, 0x14b1, 0x13eb
]

regs = [
    BitVec('s0', 16),
    BitVec('s1', 16),
    BitVec('s2', 16),
    BitVec('s3', 16),
    BitVec('s4', 16),
    BitVec('s5', 16),
    BitVec('s6', 16),
    BitVec('s7', 16),
    BitVec('s8', 16),
    BitVec('s9', 16),
    BitVec('s10', 16),
    BitVec('s11', 16),
    BitVec('s12', 16),
    BitVec('s13', 16),
    BitVec('s14', 16),
    BitVec('s15', 16),
]

x8003 = 0x1b39 + regs[0]
for i in range(0, 10):
    off = regs[(i + 1) % 10] if i != 9 else 0
    x8003 = multipliers[i] * x8003 + offsets[i] + off

x8001 = 0x0539 + regs[0]
for i in range(0, 10):
    off = regs[(i + 1) % 10] if i != 9 else 0
    x8001 = multipliers[10 + i] * x8001 + offsets[10 + i] + off

print(x8003)
print(x8001)

solver = Solver()
solver.add(x8003 == 45295)
solver.add(x8001 == 54457)
for v in regs:
    solver.add(And(UGT(v, 0xBB), ULT(v, 0xEE)))
print(solver.check())
print("traversing model...")
for d in solver.model().decls():
    print("%s = %s" % (d.name(), solver.model()[d]))
print(solver.assertions())
