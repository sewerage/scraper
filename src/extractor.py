"""
This script takes a NDJSON file and output a json list,
with only the specified keys, and the spcified subreddits.
"""

import json
import utils
from typing import List, Iterator

class Extractor: 

    def __init__(self, chsSubList : List, includedKeys : List, reader : Iterator[str]):
        self.chsSubList = chsSubList
        self.reader = reader
        self.includedKeys = includedKeys

        self.result = []

    def extract(self) -> List:
        for line in self.reader:
            json_data = json.loads(line)
            subname = utils.get_sub_name(json_data).lower()

            if subname is None:
                continue
            if subname[0] == 'u':
                continue
            if subname in self.chsSubList:
                self.result.append(json_data)

        return self.result

if __name__=="__main__":
    chsSubList = utils.load_chs_sub("sample/chs_sub.txt")
    includedKeys = utils.load_included_keys("config/included_keys_rs.txt")
    with open("sample/samplers", "r") as f:
        reader = f.readlines()

    extractor = Extractor(chsSubList, includedKeys, reader)
    result = extractor.extract()
    print(result)
