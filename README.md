# basefind2

A faster base address scanner based on [@mncoppola's](https://github.com/mncoppola) [basefind.py](https://github.com/mncoppola/ws30/blob/master/basefind.py) and [rbasefind](https://github.com/sgayou/rbasefind).

## Features
Scans a flat 32-bit binary and attempt to determine the base address. Finds parts of the subsequent string differences
inside the subsequent pointer differences to get base candidates. It doesn't need to brute-force all the of the base addresses, so it's much faster.


### Help
```
$ ./basefind2.py -h
usage: basefind2.py [-h] [-sl STRLENGTH] [-dl DIFFLENGTH] [-s SAMPLERATE] file

Scans a flat 32-bit binary and attempt to determine the base address. 
Finds DIFFLENGTH part of the subsequent string differences inside the 
subsequent pointer differences to get base candidates. It doesn't need 
to brute-force all of the base addresses, so it's much faster. Based on 
the excellent basefind.py by mncoppola and the excellent rbasefind.

positional arguments:
  file            file to scan

options:
  -h, --help      show this help message and exit
  -sl STRLENGTH   minimum length of the strings (default = 10)
  -dl DIFFLENGTH  length of the differences (default = 10)
  -s SAMPLERATE   samplerate for the validation (default = 20)
```

### Example

```
$ time ./basefind2.py FWSector -dl 40
scanning binary for strings len>=10...
total strings found: 8672
scanning binary for pointers...
total pointers found: 290797
finding differences of length: 40
possible offset 0x27807fe0 81.64%
possible offset 0x2780791a 03.00%
possible offset 0x27807b2d 03.23%
possible offset 0x2780705c 05.30%

real    0m26.393s
user    0m12.443s
sys     0m0.410s
```

`0x27807fe0` was the correct base address for this binary.
