import json
import argparse

def load_chs_sub(filename):
    chs_sub = []
    with open(filename, "r") as f:
        for line in f:
            chs_sub.append(line.strip().lower())
        return chs_sub


def append_chs_sub(sub_name, filename):
    with open(filename, "a") as f:
        f.write("\n" + sub_name)

def main(args):
    CHS_SUB_FILE_NAME = args.chs_sub_file
    FILE_LIST = args.files

    for filename in FILE_LIST:

        CHS_SUB = set(load_chs_sub(CHS_SUB_FILE_NAME))

        new_chs_sub = []

        # read file
        with open(filename, "r") as f:
            print("Now reading ", filename)
            idx = 1
            for line in f:

                if idx % 10000 == 0:
                    print(f"{filename} : {idx}", end="\r")

                json_data = json.loads(line)
                try:
                    subname = json_data["subreddit_name_prefixed"]
                except KeyError:
                    try:
                        if json_data["subreddit"][0] == "u":
                            continue
                        subname = "r/" + json_data["subreddit"]
                    except KeyError:
                        print("Sub not found")
                        continue
                subname = subname.lower()

                if subname in CHS_SUB or subname in new_chs_sub:
                    continue

                if subname[0] != "u":
                    new_chs_sub.append(subname)

                idx += 1

        for subname in new_chs_sub:
            append_chs_sub(subname, CHS_SUB_FILE_NAME)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process NDJSON data and output a list of Chinese subreddits.")
    parser.add_argument("files", nargs="+", help="List of ndjson files")
    parser.add_argument("-t", "--threshold", type=float, default=0.7,
                        help="Minimum percentage of Chinese submissions to be considered a Chinese subreddit")
    parser.add_argument("-c", "--chs_sub_file", default="chs_sub.txt",
                        help="File containing Chinese subreddit names")
    args = None
    try:
        args = parser.parse_args()
        main(args)
    except argparse.ArgumentError as e:
        parser.print_help()