POLYNOMIAL = 0x3DA3358B4DC173
POLYNOMIAL_DEGREE = 53
WINSIZE = 64
AVERAGE_BITS = 13
MINSIZE = 1024
MAXSIZE = 64 * 1024

MASK = ((1 << AVERAGE_BITS) - 1)
POL_SHIFT = POLYNOMIAL_DEGREE - 8

class rabin(object):

    def __init__(self):
        self.window = [0] * WINSIZE
        self.wpos = 0
        self.count = 0
        self.pos = 0
        self.start = 0
        self.digest = 0

        self.tables_initialized = False
        self.mod_table = [0] * 256
        self.out_table = [0] * 256

        self.last_chunk = {}

    def rabin_init(self):
        if not self.tables_initialized:
            self.__calc_tables()
            self.tables_initialized = True
        self.__rabin_reset()

    def __rabin_reset(self):
        for i in range(0, WINSIZE):
            self.window[i] = 0
        self.wpos = 0
        self.count = 0
        self.digest = 0
        self.__rabin_slide(1)

    def __rabin_slide(self, b):
        o = self.window[self.wpos]
        self.window[self.wpos] = b
        self.digest = (self.digest ^ self.out_table[o])
        self.wpos = (self.wpos + 1) % WINSIZE
        self.__rabin_append(b)

    def __rabin_append(self, b):
        index = self.digest >> POL_SHIFT
        index &= 0xff
        self.digest <<= 8
        self.digest |= (b & 0xffffffffffffffff)
        self.digest ^= self.mod_table[index]

    def rabin_next_chunk(self, buf, start_index, length):
        for i in range(0, length):
            b = buf[i + start_index]
            self.__rabin_slide(b)
            self.count += 1
            self.pos += 1
            if (self.count >= MINSIZE and ((self.digest & MASK) == 0)) or self.count >= MAXSIZE:
                self.last_chunk['start'] = self.start
                self.last_chunk['length'] = self.count
                self.last_chunk['cut_fingerprint'] = self.digest
                position = self.pos
                self.__rabin_reset()
                self.start = position
                self.pos = position
                return i + 1
        return -1

    def rabin_finalize(self):
        if self.count == 0:
            self.last_chunk['start'] = 0
            self.last_chunk['length'] = 0
            self.last_chunk['cut_fingerprint'] = 0
            return None
        self.last_chunk['start'] = self.start
        self.last_chunk['length'] = self.count
        self.last_chunk['cut_fingerprint'] = self.digest
        return self.last_chunk

    def __deg(self, p):
        mask = 0x8000000000000000
        for i in range(0, 64):
            if (mask & p) > 0:
                return 63 - i
            mask >>= 1
        return -1

    def __mod(self, x, p):
        while self.__deg(x) >= self.__deg(p):
            shift = self.__deg(x) - self.__deg(p)
            x = x ^ ((p << shift) & 0xffffffffffffffff)
        return x

    def __append_byte(self, hash, b, pol):
        hash <<= 8
        hash &= 0xffffffffffffffff
        hash |= b
        return self.__mod(hash, pol)

    def __calc_tables(self):
        for b in range(0, 256):
            hash = 0
            hash = self.__append_byte(hash, b, POLYNOMIAL)
            for i in range(0, WINSIZE - 1):
                hash = self.__append_byte(hash, 0, POLYNOMIAL)
            self.out_table[b] = hash
        k = self.__deg(POLYNOMIAL)
        for b in range(0, 256):
            self.mod_table[b] = self.__mod(b << k, POLYNOMIAL) | (b << k)

import copy
import utils

class cdc(object):

    def __init__(self, data):
        self.data = data
        self.index = 0

    def chunking(self):
        self.chunker = rabin()
        self.chunks = []
        self.chunker.rabin_init()
        length = len(self.data)
        start = 0
        while True:
            remaining = self.chunker.rabin_next_chunk(self.data, start, length)
            if remaining < 0:
                break
            length -= remaining
            start += remaining
            self.chunks.append(copy.deepcopy(self.chunker.last_chunk))
        if self.chunker.rabin_finalize() is not None:
            self.chunks.append(copy.deepcopy(self.chunker.last_chunk))

    def getchunks(self):
        while self.index < len(self.chunks):
            chunk = self.chunks[self.index]
            start = chunk['start']
            length = chunk['length']
            chunkdata = self.data[start : start + length]
            hash = utils.adler32(chunkdata) + utils.md5(chunkdata)
            yield { 'index': self.index, 'hash': hash, 'data': chunkdata }
            self.index += 1
