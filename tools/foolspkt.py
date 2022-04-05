import base64
from time import sleep

import numpy as np
import requests
from requests.adapters import HTTPAdapter, Retry

uid = 0
token = ""

headers = {
    "User-Agent": "muzuwi-foolspkt/0.1",
    "X-Foolssessiontoken": token
}

retries = Retry(total=5, backoff_factor=5)
conn = requests.Session()
conn.mount("https://fools2022.online/", HTTPAdapter(max_retries=retries))


def send_packet(packet_data):
    global headers
    global uid
    global conn
    sleep(1)
    try:
        r = conn.post(f"https://fools2022.online/packet/{uid}", packet_data,
                      headers=headers,
                      timeout=5)
        if r.status_code != 200:
            print("Failed sending packet.")
            print(f"Error Response body: '{r.text}'")
            return None
        print(f"<- Request content: {r.text}")
        return r.content
    except():
        print("Failed making request.")
        return None


def login():
    global headers
    global conn
    sleep(2)
    try:
        r = conn.post("https://fools2022.online/login", '{"u": "USERUSERUSER", "p": "PASSPASSPASSPASSPASS"}',
                      headers=headers,
                      timeout=5)
        print(f"Status: {r.status_code}")
        print(f"Content: {r.text}")
    except():
        print("Failed making request.")


def send_raw(raw):
    padding = 0 if (len(raw) + 1) % 4 == 0 else (4 - ((len(raw) + 1) % 4))
    packet = raw + b'\xff' + b'\x00' * padding
    return send_packet(base64.b64encode(packet) + b':')


# (f"type={type}".encode("ascii")) + b'\xff\xc0\x46\x08\x00\x00\x00'
#       b = b'\x07\x00\x00\x00' + (f"holder={holder}".encode("ascii")) + b'/' + \
#           (f"type={type}".encode("ascii")) + b'\x00\x00\x00\x00\x00\x00\x00'
# b = b'\x07\x00\x00\x00' + cmd + b'\xff\x00\x00\x00\x00\x00\x00'
def request_certificate(holder, type):
    cmd = (f"holder={holder}".encode("ascii")) + b'/' + (f"type={type}".encode("ascii"))
    padding = 0 if (len(cmd) + 1) % 4 == 0 else (4 - ((len(cmd) + 1) % 4))

    packet = b'\x07\x00\x00\x00' + cmd + b'\xff' + b'\x00' * padding
    bytes = base64.b64encode(packet) + b':'

    print(f"Requesting certificate for '{holder}', type '{type}'")
    print(f"Certificate request b64: {bytes}")
    response = send_packet(bytes)
    if response is None:
        print("Failed creating certificate.")
        return None
    return response


def decode_cert_bytestream(certificate):
    first = base64.b64decode(certificate)
    bytes = base64.b64decode(first[0:-1])  # Skip over 0xFF terminator byte
    return bytes


# appraisal_request = b'\x08\x00\x00\x00' + certb64 + b'\xff' + b'\x00' * 167
# appraisal_request = b'\x08\x00\x00\x00' + certb64 + b'\xff' + b'\x00' * 167
def appraise(certificate):
    certb64 = base64.b64encode(certificate)
    padding = 0 if (len(certb64) + 1) % 4 == 0 else (4 - ((len(certb64) + 1) % 4))

    packet = b'\x08\x00\x00\x00' + certb64 + b'\xff' + b'\x00' * padding
    appraisal = base64.b64encode(packet) + (':'.encode("ascii"))

    response = send_packet(appraisal)
    if response is None:
        print("Failed appraising certificate.")
        return

    data = base64.b64decode(response)
    return data


def print_appraisal_data(data):
    weirdword = int.from_bytes(data[0:3], "little")
    datastr = data[4:-1].decode("ascii", errors='replace')  # Skip over the leading word and terminator byte
    values = datastr.split("/")
    print(f"> Weird word: {weirdword}")
    for value in values:
        print(f"> {value}")


def writebytes(path, bytes):
    with open(path, "wb") as f:
        f.write(bytes)


def loadbytes(path):
    with open(path, "rb") as f:
        return bytearray(f.read())


def main_requesting():
    holder = "Muzuwi"
    type = "gold"
    nc = request_certificate(holder, type)
    if nc is None:
        print("Failed requesting specified certificate")
        return

    certbytes = decode_cert_bytestream(nc)
    print(f"Decoded cert: {certbytes}")

    data = appraise(certbytes)
    print_appraisal_data(data)
    writebytes(f"certificate_{holder}_{type}.bin", certbytes)


def analyze_stuff():
    maxlen = 46
    for i in range(17, maxlen):
        holder = i * 'a' + 'b' + (maxlen - i - 1) * 'a'
        print(f"Checking holder {holder}")
        cert = request_certificate(holder, "silver")
        if cert is None:
            print("Failed requesting certificate.")
            continue
        certbytes = decode_cert_bytestream(cert)
        writebytes(f"certificate_{holder}_silver.bin", certbytes)


def analyze_more_stuff():
    list = []

    maxlen = 46
    for i in range(0, maxlen):
        holder = i * 'a' + 'b' + (maxlen - i - 1) * 'a'
        file = loadbytes(f"certificate_{holder}_silver.bin")
        for j in range(1, int(len(file) / 16)):
            block = file[(j * 16):(j * 16) + 16]
            print(f"Block: {block}")
            for v in list:
                if v[1] == block:
                    print(f"Found equal blocks between pattern {v[0]} and {i}")
                    print(f"Block: {block}")
            list.append((i, block))


def analyze_even_more_stuff():
    for i in range(0, 50):
        holder = 46 * 'a'
        print(f"Checking holder {holder}")
        cert = request_certificate(holder, "silver")
        if cert is None:
            print("Failed requesting certificate.")
            continue
        certbytes = decode_cert_bytestream(cert)
        writebytes(f"certificate_{holder}_silver_it{i}.bin", certbytes)


def analyze_stuff_pow4():
    tmp = loadbytes(f"certificate_{46 * 'a'}_silver_it0.bin")
    running_xor = np.zeros((int(len(tmp) / 16), 16), dtype=np.ubyte)

    for i in range(0, 50):
        holder = 46 * 'a'
        file = loadbytes(f"certificate_{holder}_silver_it{i}.bin")

        for j in range(0, int(len(file) / 16)):
            block = file[(j * 16):((j * 16) + 16)]
            arr = np.frombuffer(block, dtype=np.ubyte)
            running_xor[j] = np.bitwise_xor(running_xor[j], arr)
        print(running_xor)


def analyze_stuff_pow5():
    running_xor = np.zeros((7, 16), dtype=np.ubyte)

    for i in range(0, 200):
        holder = 46 * 'a'
        cert = request_certificate(holder, "silver")
        if cert is None:
            print("Failed requesting certificate")
            continue
        bytes = decode_cert_bytestream(cert)

        for j in range(1, 7):
            block = bytes[(j * 16):((j * 16) + 16)]
            arr = np.frombuffer(block, dtype=np.ubyte)
            running_xor[j] = np.bitwise_xor(running_xor[j], arr)

        print("Current round:")
        print(running_xor)


def analyze_stuff_pow6():
    running_xor = np.zeros((7, 16), dtype=np.ubyte)

    for i in range(0, 46):
        holder = i * 'a' + 'b' + (46 - i - 1) * 'a'
        file = loadbytes(f"certificate_{holder}_silver.bin")

        for j in range(0, int(len(file) / 16)):
            block = file[(j * 16):((j * 16) + 16)]
            arr = np.frombuffer(block, dtype=np.ubyte)
            running_xor[j] = np.bitwise_xor(running_xor[j], arr)
        print(running_xor)


def i_might_have_found_something():
    for i in range(16, 48):
        # holder = "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4A"
        holder = 'A' * (i + 1)
        type = "silver"
        nc = request_certificate(holder, type)
        if nc is None:
            print("Failed requesting specified certificate")
            return

        certbytes = decode_cert_bytestream(nc)
        print(f"Decoded cert: {certbytes}")

        data = appraise(certbytes)
        print_appraisal_data(data)
        writebytes(f"certificate_brute_{holder}.bin", certbytes)


def xor_byte_str(a, b):
    ass = np.frombuffer(a, dtype=np.ubyte)
    shit = np.frombuffer(b, dtype=np.ubyte)
    fuck = np.bitwise_xor(ass, shit)
    return fuck


# login()

# b'\x21\x32\x27\xA7\xE8\x5C\x4B\x07\xCF\xD8\x2E\x6B\xBD\x30\x32\xCA'

# print(xor_byte_str(xor_byte_str(b'\xBD\xA1\x68\x13\x96\x2D\x63\xF6\x8F\xBF\x6B\xDB\xF0\x0C\x54\x13',
#                                 b'\xCC\xDB\x53\x13\xE8\xE7\xD7\xBE\xFA\x0B\xF3\x4C\x79\xA4\xDE\xCD'),
#                    b'\x15\xDF\x82\xB5\x09\x0B\x60\x05\x46\x17\x50\x6E\xD8\xD0\xE4\xE6'))

# plain = bytearray(b'authority=Cracke')
# cipher = bytearray(b'\x21\x32\x27\xA7\xE8\x5C\x4B\x07\xCF\xD8\x2E\x6B\xBD\x30\x32\xCA')
#
# ivorshit = np.zeros(len(plain), dtype=np.ubyte)
# for i in range(0, len(plain)):
#     ivorshit[i] = plain[i] ^ cipher[i]
#
# s = codecs.encode(ivorshit.tobytes(), "hex")
# print(s)

# my_plain = bytearray(b'type=gold/aaaaaa')
# ass = np.frombuffer(my_plain, dtype=np.ubyte)
# shit = np.frombuffer(ivorshit, dtype=np.ubyte)
# fuck = np.bitwise_xor(ass, shit)
# lul = codecs.encode(fuck.tobytes(), "hex")
# print(lul)

# stare = bytearray(b'\xBD\xA1\x68\x13\x96\x2D\x63\xF6\x8F\xBF\x6B\xDB\xF0\x0C\x54\x13')
# gachi = np.frombuffer(stare, dtype=np.ubyte)
# res = np.bitwise_xor(gachi, plain)
# omegalul = codecs.encode(res.tobytes(), "hex")
# print(omegalul)

#
# print(fuck)

# login()

# c = request_certificate("A" * 16 * 4096, "silver")
# writebytes("cert_long_bullshit.bin", decode_cert_bytestream(c))
# writebytes("cert_long_bullshit_plain.bin", v)

# login()


have = b'/type=silver\xff\xff\xff\xff'
want = b'/type=gold\xff\xff\xff\xff\xff\xff'
ciphertext = b'\xd7\xa3\x17\x6a\x6f\x55\x3a\xa4\x89\x18\x53\x81\xd0\x46\x00\xa9'

a = np.frombuffer(have, dtype=np.ubyte)
b = np.frombuffer(want, dtype=np.ubyte)
c = np.frombuffer(ciphertext, dtype=np.ubyte)
r = np.bitwise_xor(np.bitwise_xor(a, b), c)

for v in a:
    print(hex(v) + " ", end='')
print()
for v in b:
    print(hex(v) + " ", end='')
print()
for v in c:
    print(hex(v) + " ", end='')
print()
for v in r:
    print(hex(v) + " ", end='')
print()

# b = loadbytes("test_cert.bin")
# a = appraise(b)
# print_appraisal_data(a)
# writebytes("appr.bin", a[4:-1])


# b = loadbytes("test_cert.bin")
# v = appraise(b)
# print_appraisal_data(v)
# writebytes("test_cert_plain.bin", v[4:-1])

# c = request_certificate("A" * 16 * 8 + "AAAA", "silver")
# writebytes("test_cert.bin", decode_cert_bytestream(c))
# v = appraise(decode_cert_bytestream(c))
# writebytes("test_cert_plain.bin", v[4:-1])

# b = loadbytes("cert_test_bullshit.bin")
# v = appraise(b)
# print_appraisal_data(v)

# main_requesting()

# cert = request_certificate("type", "gold")
# if cert is not None:
#     print(decode_cert_bytestream(cert))
#     v = appraise(decode_cert_bytestream(cert))
#     if v is not None:
#         print_appraisal_data(v)

# if __name__ == '__main__':
#     i_might_have_found_something()

# b = loadbytes("cert_test_bullshit.bin")
#
# # v = appraise(b)
# # print_appraisal_data(v)
#
# plaintexts = [
#     b"authority=Cracke",
#     b"rFour/serial=945",
#     b"6389/holder=AAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA", b"AAAAAAAAAAAAAAAA",
#     b"AAAAAAAAAAAA/typ"
# ]
# ip = []
# for i in range(1, int(len(b) / 16)):
#     if i >= len(plaintexts):
#         print(f"Skipping iteration {i} - no plaintexts")
#         continue
#     m0 = plaintexts[i]
#     m1 = b[((i - 1) * 16):((i - 1) * 16 + 16)]
#     arr0 = np.frombuffer(m0, dtype=np.ubyte)
#     arr1 = np.frombuffer(m1, dtype=np.ubyte)
#     xored = np.bitwise_xor(arr0, arr1)
#     ip.append(xored)
#
# for i in range(0, len(ip)):
#     print(f"IP{i + 1}: {ip[i]}")

# b = loadbytes("cert_test_bullshit.bin")
#
# for i in range(0, 256):
#     current = b.copy()
#     #  Modify it
#     current[0x2f] = i
#
#     print(f"Trying c={current}")
#
#     try:
#         response = appraise(current)
#         print_appraisal_data(response)
#     except:
#         print("Something went wrong.")


# v = request_certificate("A" * 16 * 8, "silver")
# writebytes("pkt.bin", decode_cert_bytestream(v))
# login()

# send_raw(b'\x01\x00\x00\x00\x00\x01\x07\x11')
