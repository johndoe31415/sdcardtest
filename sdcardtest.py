#!/usr/bin/python3
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

import os
import sys
import time
import datetime
from SpeedAverager import SpeedAverager
from PRNG import PRNG
from FriendlyArgumentParser import FriendlyArgumentParser
from FilesizeFormatter import FilesizeFormatter

parser = FriendlyArgumentParser()
parser.add_argument("-l", "--logfile", metavar = "filename", type = str, default = "report.txt", help = "Specifies log filename. Defaults to %(default)s.")
parser.add_argument("-s", "--seed", metavar = "seedstring", type = str, help = "Choose a specific seed.")
parser.add_argument("-n", "--nowrite", action = "store_true", help = "Do not write, only verify.")
parser.add_argument("-p", "--parsable", action = "store_true", help = "Output parsable information as well in logfile.")
parser.add_argument("--binary-units", action = "store_true", help = "Use binary (base 2) units instead of decimal (base 10) units. E.g., use 1 kiB = 1024 bytes instead of 1 kB = 1000 bytes.")
parser.add_argument("--blocksize", metavar = "bytes", type = int, default = 1024 * 1024, help = "Writing block size. Defaults to %(default)d.")
parser.add_argument("--force", action = "store_true", help = "Do not ask for any confirmation.")
parser.add_argument("device", metavar = "path", type = str, help = "Device to test. All data on this will be destroyed.")
args = parser.parse_args(sys.argv[1:])

fsfmt = FilesizeFormatter(base1000 = not args.binary_units)
def get_disksize(path):
	with open(path, "rb") as f:
		f.seek(0, os.SEEK_END)
		return f.tell()

def logmsg(f, msg):
	now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	print("%s: %s" % (now, msg))
	print("%s: %s" % (now, msg), file = f)

def writeblocks(pattern, device):
	with open("block-error-pattern.bin", "wb") as f:
		f.write(pattern)
	with open("block-error-device.bin", "wb") as f:
		f.write(device)

disksize = get_disksize(args.device)
if (not args.force) and (not args.nowrite):
	print("You are about to erase device %s" % (args.device))
	print("ALL DATA WILL BE LOST")
	print("%s: %d bytes = %s" % (args.device, disksize, fsfmt(disksize)))
	yes = input("Continue (type 'YES'): ")
	if yes != "YES":
		print("Aborted.")
		sys.exit(1)

full_block_count = disksize // args.blocksize
last_block_size = disksize % args.blocksize
if args.seed is None:
	seed = str(int(time.time()))
else:
	seed = args.seed
prng = PRNG(args.blocksize, seed = seed)

if args.nowrite:
	permissions = "rb"
else:
	permissions = "r+b"

t0 = time.time()
with open(args.logfile, "a") as logfile, open(args.device, permissions) as device:
	if not args.nowrite:
		logmsg(logfile, "Starting writing action onto %s (%d bytes = %s), %d full blocks of %d bytes + %d bytes. Seed \"%s\"." % (args.device, disksize, fsfmt(disksize), full_block_count, args.blocksize, last_block_size, seed))
		averager = SpeedAverager()
		for block_no in range(full_block_count):
			pos = args.blocksize * block_no
			averager.add(pos)
			if (block_no > 0) and ((block_no % 100) == 0):
				speed = averager.real_speed
				if speed is not None:
					percent_done = 100 * pos / disksize
					logmsg(logfile, "Current writing position is %s (%.1f%%), writing speed is %s/sec" % (fsfmt(pos), percent_done, fsfmt(round(speed))))
					if args.parsable:
						print("Parsable W %.3f %d %d" % (time.time() - t0, pos, speed), file = logfile)
			block = prng.next_block()
			device.write(block)
		if last_block_size != 0:
			block = prng.next_block()[:last_block_size]
			device.write(block)

		os.sync()
		if args.parsable:
			print("Parsable W %.3f %d %d" % (time.time() - t0, pos, speed), file = logfile)
		logmsg(logfile, "Writing finished.")

	logmsg(logfile, "Starting verification with seed \"%s\"." % (seed))
	device.seek(0, os.SEEK_SET)
	prng.reset()

	correct = 0
	incorrect = 0
	averager = SpeedAverager()
	t0 = time.time()
	for block_no in range(full_block_count):
		pos = args.blocksize * block_no
		averager.add(pos)
		if (block_no > 0) and ((block_no % 100) == 0):
			speed = averager.real_speed
			if speed is not None:
				if correct + incorrect != 0:
					percent_correct = 100 * correct / (correct + incorrect)
				else:
					percent_correct = 0
				percent_done = 100 * pos / disksize
				logmsg(logfile, "Current reading position is %s (%.1f%%), reading speed is %s/sec. %s correct (%.1f%%), %s (%d bytes) incorrect." % (fsfmt(pos), percent_done, fsfmt(round(speed)), fsfmt(correct), percent_correct, fsfmt(incorrect), incorrect))
				if args.parsable:
					print("Parsable R %.3f %d %d %d" % (time.time() - t0, pos, speed, correct), file = logfile)
		block = prng.next_block()
		device.seek(pos)
		dev_block = device.read(len(block))
		if block != dev_block:
			logmsg(logfile, "Verification error at %s (block index %d)." % (fsfmt(pos), block_no))
			incorrect += len(block)
		else:
			correct += len(block)

	if last_block_size != 0:
		block = prng.next_block()[:last_block_size]
		dev_block = device.read(len(block))
		if block != dev_block:
			logmsg(logfile, "Verification error at last block.")
			incorrect += len(dev_block)
		else:
			correct += len(dev_block)

	logmsg(logfile, "Verification finished: %s correct, %d blocks, i.e., %s (%d bytes) incorrect" % (fsfmt(correct), incorrect // args.blocksize, fsfmt(incorrect), incorrect))


