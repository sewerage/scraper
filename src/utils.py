import string
import re
from typing import List

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


def get_sub_name(jsonData: dict) -> str:
    """
    Input json, return the name of the subreddit 
    Will return none if the subreddit is not found
    """

    if "subreddit_name_prefixed" in jsonData:
        subname = jsonData["subreddit_name_prefixed"]
    elif "subreddit" in jsonData:
        subname = "r/" + jsonData["subreddit"]
    else:
        return None

    return subname.lower()


def is_chinese(s: str) -> bool:
    """
    Determine if string is Chinese
    """

    # https://zhuanlan.zhihu.com/p/84625185

    def filter_str(sentence: str) -> str:
        remove_nota = u'[’·°–!"#$%&\'()*+,-./:;<=>?@，。?★、…【】（）《》？“”‘’！[\\]^_`{|}~]+'
        remove_punctuation_map = dict((ord(char), None)
                                      for char in string.punctuation)
        sentence = re.sub(remove_nota, '', sentence)
        sentence = sentence.translate(remove_punctuation_map)
        return sentence.strip()

    def determine_language(s: str) -> List[str]:
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

    result = determine_language(s)
    return "zh" == result \
        or ("zh" in determine_language(s)
            and "ja" not in determine_language(s)
                and "ko" not in determine_language(s))
