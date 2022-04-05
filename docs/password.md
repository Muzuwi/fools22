## Password

16 byte "registers"
- In memory: <0x02021dc4, 0x02021dd3>  

~~2 byte "parameters":~~
~~- 0x020375da - A~~
~~- 0x020375db - B~~
**0x020375da is just the address of 0x8001**

### Basic Block

Input:
- 0x8001 of previous iteration
- Multiplier M
- Offset C
- "Register" value Rn  

Output:
- Hword, which is used as input for the next block

```
h = hword{B, A}
v = M * h + C 
out = v + Rn
```

Iterations:
- **Iteration -1:** out = 0x1b39 + R0
- **Iteration 0:** M = 0x0049, C = 0x18df, Rn = R1
- **Iteration 1:** M = 0x0061, C = 0x13eb, Rn = R2
- **Iteration 2:** M = 0x000d, C = 0x11ef, Rn = R3
- **Iteration 3:** M = 0x0029, C = 0x1145, Rn = R4
- **Iteration 4:** M = 0x0043, C = 0x12df, Rn = R5
- **Iteration 5:** M = 0x0065, C = 0x0dfd, Rn = R6
- **Iteration 6:** M = 0x0059, C = 0x13af, Rn = R7
- **Iteration 7:** M = 0x008b, C = 0x149f, Rn = R8
- **Iteration 8:** M = 0x0047, C = 0x0fef, Rn = R9
- **Iteration 9:** M = 0x0053, C = 0x0fb5, Rn = R0
- **Iteration 10:** M = 0x003b, C = 0x0e75, Rn = R1
- **Iteration 11:** M = 0x00b5, C = 0x11fb, Rn = R2
- **Iteration 12:** M = 0x007f, C = 0x1237, Rn = R3
- **Iteration 13:** M = 0x00a3, C = 0x125f, Rn = R4
- **Iteration 14:** M = 0x0067, C = 0x107b, Rn = R5
- **Iteration 15:** M = 0x00a3, C = 0x1951, Rn = R6
- **Iteration 16:** M = 0x0095, C = 0x1b47, Rn = R7
- **Iteration 17:** M = 0x00c1, C = 0x151f, Rn = R8
- **Iteration 18:** M = 0x00d3, C = 0x14b1, Rn = R9
- **Iteration 19:** M = 0x0097, C = 0x13eb

## Targets

0x8001 = 54457

0x8003 = 45295
