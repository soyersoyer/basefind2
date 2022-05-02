#!/usr/bin/env python3
import re, struct, argparse, array

def get_pointers(file):
    pointers = set()
    for offset in range(0, len(file) - 4, 4):
        ptr = struct.unpack("<L", file[offset : offset + 4])[0]
        pointers.add(ptr)
    pointers = list(pointers)
    pointers.sort()
    return pointers

def get_strings(file, min_length):
    regexp = b"[ -~\\t\\r\\n]{%d,}" % min_length 
    pattern = re.compile(regexp)

    strings = []
    for m in pattern.finditer(file):
        strings.append(m.start())
    return strings

def get_offsets(set):
    offsets = array.array("L")
    last = 0
    for ptr in set:
        offsets.append(ptr - last)
        last = ptr
    return offsets

# strs and ptrs are ordered, so we can make ordered search
# only counts every samplerate elem, adjusts at return
def count_str(ptrs, strs, offset, samplerate):
    c = 0
    lastptr = 0
    for si in range(0, len(strs), samplerate):
        ptr = ptrs.find(struct.pack("<L", strs[si] + offset), lastptr)
        if ptr == -1:
            continue
        lastptr = ptr
        c += 1
    return c * samplerate
        
parser = argparse.ArgumentParser(description=
"""Scans a flat 32-bit binary and attempt to determine the base address.
Finds DIFFLENGTH part of the subsequent string differences inside the subsequent pointer differences to get base candidates.
It doesn't need to brute-force all of the base addresses, so it's much faster.
Based on the excellent basefind.py by mncoppola and the excellent rbasefind.""")
parser.add_argument("-sl", metavar="STRLENGTH", type=int, help="minimum length of the strings (default = 10)", default=10)
parser.add_argument("-dl", metavar="DIFFLENGTH", type=int, help="length of the differences (default = 10)", default=10)
parser.add_argument("-s", metavar="SAMPLERATE", type=int, help="samplerate for the validation (default = 20)", default=20)
parser.add_argument("file", help="file to scan")
args = parser.parse_args()

str_len = args.sl
diff_len = args.dl
samplerate = args.s

with open(args.file, "rb") as f:
    file = f.read()

print(f"scanning binary for strings len>={str_len}...")
strs = get_strings(file, str_len)
print(f"total strings found: {len(strs)}")

print("scanning binary for pointers...")
ptrs = get_pointers(file)
print(f"total pointers found: {len(ptrs)}")

str_offsets = get_offsets(strs)
ptr_offsets = get_offsets(ptrs)

ptrs_b = array.array("L", ptrs).tobytes()
ptr_off_b = ptr_offsets.tobytes()

found = set()

print(f"finding differences of length: {diff_len}")
for si in range(0, len(str_offsets) - diff_len):
    print(si, end = "\r")

    str_b = str_offsets[si : si + diff_len].tobytes()
    pi = ptr_off_b.find(str_b)

    if pi == -1:
        continue

    pi //= ptr_offsets.itemsize
    offset = ptrs[pi] - strs[si]
    
    if offset < 0 or offset in found:
        continue

    print(f"possible offset 0x{offset:x} ...", end = "\r")
    percent = count_str(ptrs_b, strs, offset, samplerate) / len(strs) * 100
    print(f"possible offset 0x{offset:x} {percent:05.2f}%")
    found.add(offset)
