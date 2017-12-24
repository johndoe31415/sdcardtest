sdcardtest
==========
sdcardtest allows you to check block devices for write errors, e.g., if you
have SD cards which may be fake, they will report a larger capacity to the
operating system than what they are actually able to store. sdcardtest uses a
pseudo-random data stream that is written on the complete device and then,
after all data has been written, read back. This ensures that the SD card has
no way to "cheat".

WARNING: All data on the device will be IRREVOCABLY destroyed. So don't do this
unless you have no valuable data on the test device (e.g., an empty USB drive).

Usage
=====
```
usage: sdcardtest.py [-h] [-l filename] [-s seedstring] [-n] [-p]
                     [--binary-units] [--blocksize bytes] [--force]
                     path

positional arguments:
  path                  Device to test. All data on this will be destroyed.

optional arguments:
  -h, --help            show this help message and exit
  -l filename, --logfile filename
                        Specifies log filename. Defaults to report.txt.
  -s seedstring, --seed seedstring
                        Choose a specific seed.
  -n, --nowrite         Do not write, only verify.
  -p, --parsable        Output parsable information as well in logfile.
  --binary-units        Use binary (base 2) units instead of decimal (base 10)
                        units. E.g., use 1 kiB = 1024 bytes instead of 1 kB =
                        1000 bytes.
  --blocksize bytes     Writing block size. Defaults to 1048576.
  --force               Do not ask for any confirmation.
```

License
=======
GNU GPL v3.
