"""
This class allows to read a zstd compressed file line by line.
"""

import zstandard as zstd

class ZstdReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = None
        self.dctx = zstd.ZstdDecompressor()
        self.reader = None
        self.buffer = b""

    def __enter__(self):
        self.file = open(self.file_path, 'rb')
        self.reader = self.dctx.stream_reader(self.file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        self.file = None
        self.reader = None

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if b'\n' in self.buffer:
                line_end = self.buffer.index(b'\n') + 1
                line = self.buffer[:line_end]
                self.buffer = self.buffer[line_end:]
                return line.decode()

            chunk = self.reader.read(4096)
            if not chunk:
                if self.buffer:
                    line = self.buffer
                    self.buffer = b""
                    return line.decode()
                else:
                    raise StopIteration

            self.buffer += chunk
# Usage
if __name__ == "__main__":
    zst_file_path = '/tmp/RS_2023-09.zst'
    with ZstdReader(zst_file_path) as reader:
        idx = 0
        for line in reader:
            if idx > 10:
                break
            print(line)
            idx += 1
