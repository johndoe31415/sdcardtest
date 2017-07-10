#	sdcardtest - Test block devices for integrity.
#	Copyright (C) 2017-2017 Johannes Bauer
#
#	This file is part of sdcardtest.
#
#	sdcardtest is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	sdcardtest is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with sdcardtest; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>
#

import struct
import hashlib
import Crypto.Cipher.AES

class PRNG(object):
	_ENCODING = struct.Struct("<Q")

	def __init__(self, blocksize, seed = ""):
		self._blockno = 0
		self._plaintext = bytes(blocksize)
		self._key = hashlib.md5(seed.encode("utf-8")).digest()

	def reset(self):
		self._blockno = 0

	def next_block(self):
		self._blockno += 1
		iv = self._ENCODING.pack(self._blockno) + bytes(8)
		engine = Crypto.Cipher.AES.new(key = self._key, IV = iv, mode = Crypto.Cipher.AES.MODE_CBC)
		return engine.encrypt(self._plaintext)

if __name__ == "__main__":
	import time

	size = 1000000 * 100
	prng = PRNG(size)
	for i in range(100):
		t0 = time.time()
		prng.next_block()
		t1 = time.time()
		tdiff = t1 - t0
		print("%.1f MB/s" % (size / tdiff / 1e6))
