Establishing a connection
- out: 0xbe5015ff
- out: 0xffbe5015

waits for incoming data?
compare with 0x000f0015, if not then failed

wait for incoming data?
compare with 0x420b00b5, if true then pass
compare with 0x20221337, if true then pass
otherwise fail

something with 0800e085

```
struct TransmitBuffer {
    uint32* data_start;
    uint32* word_count;
} at(0x0203d5a0);
```

```
struct ReceiveBuffer {
    uint32* buf_start;
    uint32* buf_size?;  //  Might be a static 0x04000
} at(0x0203d5b8);
```

**transmits data from 0x0203db90, 2 words**

receive words from server

compare with 0xCACEFACE and 0xFEF0CEC0 (end of transmittion synchronization?)

receive response length from the server, limit to max 0x4000 and read it

## 0x0203db90 - request words buffer
## 0x0203db48 - request words count (always?)

## 0x0203d5a4 - pointer to request words count

### Going right in center square

~~Request { ??????
    bytes: {01 1a 37 76 2b 2a 07 06}c
    bytes: {01 1a 37 76 2b 2a 07 06}
    length: {2}
}~~

Request {
    bytes: {01 81 7f 71 2b 2e 07 06}
    length: {2}
}

Request {
    bytes: {01 67 6f 6e 2b 2e 07 06}
    length: {2}
}

Request {
    bytes: {01 72 f7 6e 2b 2e 07 06}
    length: {2}
}

Request {
    bytes: {01 ab cf 2c 2b 2a 07 06}
    length: {2}
}

#  Right -> Center

Request {
    bytes: {01 ca 4a 3e 00 01 1b 12}
    length: {2}
}

# Center -> Up

Request {
    bytes: {01 af 82 40 10 02 0e 20}
    length: {2}
}

# Up -> Center

Request {
    bytes: {01 2b 52 3d 00 01 11 07}
    length: {2}
}

# Center -> Left

Request {
    bytes: {01 00 3b 64 37 1b 20 0e}
    length: {2}
}

# Left -> Center

Request {
    bytes: {01 3e ea 3d 00 01 07 11}
    length: {2}
}

#  Center -> Down

Request {
    bytes: {01 e4 a1 fd 3d 3f 0f 07}
    length: {2}
}

#  Down -> Center

Request {
    bytes: {01 fa ca 43 00 01 11 1b}
    length: {2}
}

# Generalized command format

- b[0]: command type

1 - request map data

01 xx xx xx HH LL xx xx

W0 - - - - - - W1


### Weird checksum part 1 

```
x = (byte[0x03005d80] << 8)
W0 = (W0 + x)
```

### Weird checksum part 2

```
magic = 0xF0DBEB15
for each word in data buffer {
    magic = rotr(magic, 5)
    magic = magic ^ word   
    magic = (xored + 2*word)
}
```
DATAW0 = (magic << 16) + (halfword[DATA0]) 

#### 0x0203db70 - something important?


W1:
- MX MY xx yy
- xx/yy - player x/y?
- MX/MY - map id X/Y