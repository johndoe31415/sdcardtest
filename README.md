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

License
=======
GNU GPL v3.
