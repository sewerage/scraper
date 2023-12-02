import json
import argparse

def load_included_keys(filename):
    included_keys = []
    with open(filename, "r") as f:
        for line in f:
            included_keys.append(line.strip())
        return included_keys

def load_chs_sub(filename):
    chs_sub = []
    with open(filename, "r") as f:
        for line in f:
            chs_sub.append(line.strip())
        return chs_sub

def append_to_new_file(newfilename, json_data, included_keys):
    with open(newfilename, "a") as f:
        new_json_data = {key: json_data[key]
                         for key in included_keys if key in json_data}
        f.write(json.dumps(new_json_data, ensure_ascii=False) + "\n")

def main(args):
    NDJSON_FILE_NAME = args.input_file
    OUTPUT_FILE_NAME = args.output_file
    CHS_SUB_FILE_NAME = args.chs_sub_file
    INCLUDED_KEYS_FILE_NAME = args.included_keys_file

    CHS_SUB = set(load_chs_sub(CHS_SUB_FILE_NAME))
    INCLUDED_KEYS = set(load_included_keys(INCLUDED_KEYS_FILE_NAME))

    with open(NDJSON_FILE_NAME, 'r') as file:
        idx = 0
        hit_cnt = 0
        print(f"\nNow reading {NDJSON_FILE_NAME}")
        print(len(CHS_SUB), " subs included")
        print(len(INCLUDED_KEYS), " keys included")
        print("------------------------------")
        for line in file:
            idx += 1

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

            # skip u/
            if subname[0] == "u":
                continue
            
            if subname.lower() in CHS_SUB:
                hit_cnt += 1
                append_to_new_file(OUTPUT_FILE_NAME, json_data, INCLUDED_KEYS)

            if idx % 10000 == 0:
                print(f"{NDJSON_FILE_NAME} : {idx} -> {OUTPUT_FILE_NAME} : {hit_cnt}",end="\r")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process NDJSON data, limit dimensions and ")
    parser.add_argument("-i", "--input_file",  required=True,
                        help="Input NDJSON file name")
    parser.add_argument("-o", "--output_file",  required=True,
                        help="Output NDJSON file name")
    parser.add_argument("-c", "--chs_sub_file", default="chs_sub.txt",
                        help="File containing Chinese subreddit names")
    parser.add_argument("-k", "--included_keys_file",
                        default="included_keys.txt", help="File containing included keys")
    args = None
    try:
        args = parser.parse_args()
        main(args)
    except argparse.ArgumentError as e:
        parser.print_help()
