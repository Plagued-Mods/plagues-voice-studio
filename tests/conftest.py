"""Small, structural xWMA fixture; its packet bytes are not real encoded audio."""
import struct
import pytest


@pytest.fixture
def xwma_bytes():
    def make(*, form=b'XWMA', codec=0x0161, omit=(), extra=()):
        fmt = struct.pack('<HHIIHHH', codec, 1, 44100, 6000, 4, 16, 0)
        chunks = [(b'fmt ', fmt), (b'dpds', struct.pack('<II', 4096, 8192)),
                  (b'data', b'\x11' * 8), *extra]
        body = form + b''.join(tag + struct.pack('<I', len(data)) + data + b'\0' * (len(data) % 2)
                               for tag, data in chunks if tag not in omit)
        return b'RIFF' + struct.pack('<I', len(body)) + body
    return make
