"""
This script scans through a list of NDJSON files and outputs a list of Chinese subreddits.
"""

import json
import utils
from typing import Iterator, List


class ChsSubScanner:

    def __init__(self, existingChsSubList : List, reader : Iterator[str], threashold : float = 0.8):
        self.chsSubList = existingChsSubList
        self.reader = reader
        self.threashold = threashold

        self.subList = {} # subname : [chs_count, total_count]

    def scan(self) -> List[str]:

        for line in self.reader:
            json_data = json.loads(line)
            subname = utils.get_sub_name(json_data)

            if subname is None:
                continue
            if subname[0] == 'u':
                continue
            if subname in self.chsSubList:
                continue

            isChs = utils.is_chinese(json_data["title"])
            self._add_to_sub_list(subname, isChs)

        for subname, (chs_count, total_count) in self.subList.items():
            if chs_count / total_count >= self.threashold:
                self.chsSubList.append(subname)

        return self.chsSubList


    def _add_to_sub_list(self, subname : str, isChs : bool) -> None:
        if subname not in self.subList:
            self.subList[subname] = [0, 0]
        if isChs:
            self.subList[subname][0] += 1
        self.subList[subname][1] += 1



if __name__ == "__main__":
    with open("sample/samplers") as file:
        reader = ChsSubScanner([], file.readlines())
        reader.scan()
        print(reader.export())