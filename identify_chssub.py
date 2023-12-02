import json
import os
import multiprocessing
import string
import re
import queue
import time
import argparse


def judge_language(s):
    s = filter_str(s)
    result = []
    s = re.sub('[0-9]', '', s).strip()
    # unicode english
    re_words = re.compile(u"[a-zA-Z]")
    res = re.findall(re_words, s)  # 查询出所有的匹配字符串
    res2 = re.sub('[a-zA-Z]', '', s).strip()
    if len(res) > 0:
        result.append('en')
    if len(res2) <= 0:
        return 'en'

    # unicode chinese
    re_words = re.compile(u"[\u4e00-\u9fa5]+")
    res = re.findall(re_words, s)  # 查询出所有的匹配字符串
    res2 = re.sub(u"[\u4e00-\u9fa5]+", '', s).strip()
    if len(res) > 0:
        result.append('zh')
    if len(res2) <= 0:
        return 'zh'

    # unicode korean
    re_words = re.compile(u"[\uac00-\ud7ff]+")
    res = re.findall(re_words, s)  # 查询出所有的匹配字符串
    res2 = re.sub(u"[\uac00-\ud7ff]+", '', s).strip()
    if len(res) > 0:
        result.append('ko')
    if len(res2) <= 0:
        return 'ko'

    # unicode japanese katakana and unicode japanese hiragana
    re_words = re.compile(u"[\u30a0-\u30ff\u3040-\u309f]+")
    res = re.findall(re_words, s)  # 查询出所有的匹配字符串
    res2 = re.sub(u"[\u30a0-\u30ff\u3040-\u309f]+", '', s).strip()
    if len(res) > 0:
        result.append('ja')
    if len(res2) <= 0:
        return 'ja'
    return result


def filter_str(sentence):
    remove_nota = u'[’·°–!"#$%&\'()*+,-./:;<=>?@，。?★、…【】（）《》？“”‘’！[\\]^_`{|}~]+'
    remove_punctuation_map = dict((ord(char), None)
                                  for char in string.punctuation)
    sentence = re.sub(remove_nota, '', sentence)
    sentence = sentence.translate(remove_punctuation_map)
    return sentence.strip()


def is_chinese(string):
    # https://zhuanlan.zhihu.com/p/84625185
    result = judge_language(string)
    return "zh" == result \
        or ("zh" in judge_language(string)
            and "ja" not in judge_language(string)
                and "ko" not in judge_language(string))


def load_chs_sub(filename):
    chs_sub = []
    with open(filename, "r") as f:
        for line in f:
            chs_sub.append(line.strip().lower())
        return chs_sub


def append_chs_sub(sub_name, filename):
    with open(filename, "a") as f:
        f.write("\n" + sub_name)


def worker(
    read_queue,  # queue read from file
    result_queue,  # queue to append results to
    chs_sub,  # exisiting chs_sub
    terminate_flag,  # flag to terminate workers
    worker_status,  # dict to store worker status
    chs_threshold=0.8  # threshold to determine if a subreddit is chinese
):
    total_sub_count = {}
    chs_sub_count = {}
    worker_status[multiprocessing.current_process().name] = "active"
    while not terminate_flag.is_set():
        try:
            # t1 = time.time()
            buffer = read_queue.get(timeout=1)
            # t2 = time.time()
            # if multiprocessing.current_process().name == "Process-5":
            #     print(t2-t1)
        except queue.Empty:
            worker_status[multiprocessing.current_process().name] = "idle"
            time.sleep(1)
            continue

        worker_status[multiprocessing.current_process().name] = "active"

        for subname, title in buffer:
            if subname in chs_sub:
                continue

            if subname not in total_sub_count:
                total_sub_count[subname] = 1
            else:
                total_sub_count[subname] += 1

            if is_chinese(title):
                if subname not in chs_sub_count:
                    chs_sub_count[subname] = 1
                else:
                    chs_sub_count[subname] += 1

        read_queue.task_done()

    worker_status[multiprocessing.current_process().name] = "terminating"
    new_chs_sub = []
    for subname in chs_sub_count:
        if chs_sub_count[subname] > 30 and chs_sub_count[subname] / total_sub_count[subname] > chs_threshold:
            new_chs_sub.append(subname)
    result_queue.put(set(new_chs_sub))
    worker_status[multiprocessing.current_process().name] = "terminated"


def monitor(worker_status, read_queue, pause_flag, qsize_upper_bound, buffer_packet_size, interval=10):
    while True:
        try:
            read_queue_size = read_queue.qsize()
        except NotImplementedError:
            read_queue_size = -1

        if read_queue_size > qsize_upper_bound:
            pause_flag.set()
        else:
            pause_flag.clear()

        active_worker_count = 0
        total_worker_count = len(worker_status)
        for status in worker_status.values():
            if status == "active":
                active_worker_count += 1

        print(
            f"queue size {read_queue_size*buffer_packet_size}, {active_worker_count}/{total_worker_count} active\t\t\t")
        # print(" ".join([s[0] for s in worker_status.values()]), end="\r")
        time.sleep(interval)


def main(args):
    THREAD_COUNT = args.threads
    CHS_SUB_FILE_NAME = args.chs_sub_file
    FILE_LIST = args.files
    THRESHOLD = args.threshold
    QSIZE_UPPER_BOUND = args.qsize_upper_bound
    BUFFER_PACKET_SIZE = 10000

    for filename in FILE_LIST:

        CHS_SUB = set(load_chs_sub(CHS_SUB_FILE_NAME))

        new_chs_sub = set()

        result_queue = multiprocessing.Queue()
        terminate_flag = multiprocessing.Event()
        pause_flag = multiprocessing.Event()  # flag to signal main to pause
        worker_status = multiprocessing.Manager().dict()
        read_queue = multiprocessing.JoinableQueue()

        # creat pool
        pool = []
        for _ in range(THREAD_COUNT):
            p = multiprocessing.Process(target=worker, args=(
                read_queue, result_queue, CHS_SUB, terminate_flag, worker_status, THRESHOLD))
            pool.append(p)
            p.start()

        status_monitor_process = multiprocessing.Process(target=monitor, args=(
            worker_status, read_queue, pause_flag, QSIZE_UPPER_BOUND, BUFFER_PACKET_SIZE))
        status_monitor_process.start()

        # read file
        with open(filename, "r") as f:
            print("Now reading ", filename)
            idx = 1
            read_buffer = []
            for line in f:

                if idx % BUFFER_PACKET_SIZE == 0:
                    if pause_flag.is_set():
                        time.sleep(1)
                        continue
                    if len(read_buffer) >= BUFFER_PACKET_SIZE:
                        read_queue.put(read_buffer)
                        read_buffer = []
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
                if subname[0] != "u":
                    read_buffer.append(
                        (subname, json_data["title"]))

                idx += 1

            if len(read_buffer) > 0:
                read_queue.put(read_buffer)
                read_buffer = []

        # waiting for workers to finish
        print("File read complete, waiting for workers to finish...")
        while worker_status.values() != ["idle"] * THREAD_COUNT:
            time.sleep(1)
        terminate_flag.set()

        # waiting for workers to terminate
        print("Terminating workers...")
        while worker_status.values() != ["terminated"] * THREAD_COUNT:
            time.sleep(1)

        # terminate workes and append the results
        for p in pool:
            p.join()

        status_monitor_process.terminate()

        while not result_queue.empty():
            new_chs_sub |= result_queue.get()

        # write results to file

        for subname in new_chs_sub:
            append_chs_sub(subname, CHS_SUB_FILE_NAME)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process NDJSON data and output a list of Chinese subreddits.")
    parser.add_argument("files", nargs="+", help="List of ndjson files")
    parser.add_argument("-t", "--threshold", type=float, default=0.7,
                        help="Minimum percentage of Chinese submissions to be considered a Chinese subreddit")
    parser.add_argument("-u", "--qsize-upper-bound", type=int, default=3e7,
                        help="Upper bound of queue size")
    parser.add_argument("-j", "--threads", type=int, default=os.cpu_count(),
                        help="Number of threads")
    parser.add_argument("-c", "--chs_sub_file", default="chs_sub.txt",
                        help="File containing Chinese subreddit names")
    args = None
    try:
        args = parser.parse_args()
        main(args)
    except argparse.ArgumentError as e:
        parser.print_help()