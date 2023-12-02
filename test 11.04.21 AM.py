import json 
import libtorrent as lt


with open("samplerc") as sample:
    data = json.loads(sample.readline())
    for line in data.keys():
        print(line)
