# coding=utf-8
import datetime
import sys
import os
__author__ = 'jayvee'
import json
import gzip
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.dao_utils.mongo_utils import get_db_inst
from utils.CommonUtils import PROJECT_PATH
def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield json.dumps(eval(l))


# f = open("output.strict", 'w')
# for l in parse("reviews_Video_Games.json.gz"):
#   f.write(l + '\n')


def save_to_mongo(item_list):
    db_inst = get_db_inst('AmazonReviews', 'AndroidAPP')
    # r = db_inst.find({"app_name": "UC浏览器"})
    # for item in item_list:
    db_inst.insert_many(item_list)
    # print '%s doc inserted' % len(item_list)


if __name__ == '__main__':
    ilist = []
    count = 0
    for l in parse(
            "%s/data/reviews_Apps_for_Android.json.gz"%PROJECT_PATH):
        # print l
        count += 1
        if count > 153488:
            elem = json.loads(l)
            try:
                t = elem['reviewTime'].split(',')
                d = t[0].split(' ')
                elem['up_vote'] = elem['helpful'][0]
                elem['total_vote'] = elem['helpful'][1]
                del (elem['helpful'])
                elem['reviewTime'] = datetime.datetime(year=int(t[1]), month=int(d[0]), day=int(d[1]))
                ilist.append(elem)

            except ValueError, ve:
                print '[error]%s\tdetail=%s' % (l, ve)
            if count % 1000 == 0:
                save_to_mongo(ilist)
                print '%s documents inserted' % count
                ilist = []
    save_to_mongo(ilist)
    #   f.write(l + '\n')
    print count
