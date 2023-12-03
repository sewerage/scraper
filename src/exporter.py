"""
This module is responsible for exporting the json list to a ndjson file,
and compress the file to a gz file.
"""

import json
import gzip
import io
from typing import List

class Exporter:
    def __init__(self, data: List, outputPath: str) -> None:
        self.data = data
        self.outputPath = outputPath

    def export(self) -> None:
        # first write into memory 
        ndjsonFile = io.BytesIO():
            for line in self.data:
                ndjsonFile.write(json.dumps(line).encode("utf-8") + b"\n")

        # then compress it 
        with open(self.outputPath, "wb") as gzFile:
            with gzip.open(gzFile, "wb") as _:
                _.write(ndjsonFile.getvalue())

if __name__ == "__main__":
    data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
    exporter = Exporter(data, "output.gz")
    exporter.export()