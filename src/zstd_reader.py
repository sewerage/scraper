import zstandard as zstd

class ZstdReader:
    def __init__(self, filePath : str) -> None:
        self.filePath = filePath
        self.file = None
        self.decompressor = zstd.ZstdDecompressor()
        self.reader = None
        self.buffer = b""

        self.linecount = 0 

    def status(self):
        return {
            "filePath": self.filePath,
            "bufferSize": len(self.buffer),
            "linecount": self.linecount
        }  

    def __enter__(self):
        self.file = open(self.filePath, 'rb')
        self.reader = self.decompressor.stream_reader(self.file)
        return self

    def __exit__(self, excType, excVal, excTb):
        if self.file:
            self.file.close()
        self.file = None
        self.reader = None

    def __iter__(self):
        return self

    def __next__(self) -> str:
        self.linecount += 1
        while True:
            if b'\n' in self.buffer:
                lineEnd = self.buffer.index(b'\n') + 1
                line = self.buffer[:lineEnd]
                self.buffer = self.buffer[lineEnd:]
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
    zstFilePath = 'RS_2023-09.zst'
    with ZstdReader(zstFilePath) as reader:
        idx = 0
        for line in reader:
            if idx > 10:
                break
            print(line)
            idx += 1
