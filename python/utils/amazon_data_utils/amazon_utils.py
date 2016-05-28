# coding=utf-8
import datetime
import sys
import os

__author__ = 'jayvee'
import json
import gzip

projectpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print projectpath
sys.path.append(projectpath)
from utils.dao_utils.mongo_utils import get_db_inst
from utils.CommonUtils import PROJECT_PATH


def parse(path):
    g = gzip.open(path, 'r')
    for l in g:
        yield json.dumps(eval(l))


# f = open("output.strict", 'w')
# for l in parse("reviews_Video_Games.json.gz"):
#   f.write(l + '\n')


def save_list2mongo(item_list, db_name, collection_name):
    db_inst = get_db_inst(db_name, collection_name)
    # r = db_inst.find({"app_name": "UC浏览器"})
    # for item in item_list:
    db_inst.insert_many(item_list)
    # print '%s doc inserted' % len(item_list)


def handle_review_gzfile(gz_name, db_name, collection_name):
    ilist = []
    count = 0
    for l in parse("%s/data/%s" % (PROJECT_PATH, gz_name)):
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
                save_list2mongo(ilist, db_name, collection_name)
                print '%s documents inserted' % count
                ilist = []
    save_list2mongo(ilist, db_name, collection_name)
    #   f.write(l + '\n')
    print count


def handle_meta_gzfile(gz_name, db_name, collection_name):
    ilist = []
    count = 0
    for l in parse("%s/data/%s" % (PROJECT_PATH, gz_name)):
        # print l
        count += 1
        if count > 0:
            elem = json.loads(l)
            # try:
            #
            #     # t = elem['reviewTime'].split(',')
            #     # d = t[0].split(' ')
            #     # elem['up_vote'] = elem['helpful'][0]
            #     # elem['total_vote'] = elem['helpful'][1]
            #     # del (elem['helpful'])
            #     # elem['reviewTime'] = datetime.datetime(year=int(t[1]), month=int(d[0]), day=int(d[1]))
            ilist.append(elem)
            #
            # except ValueError, ve:
            #     print '[error]%s\tdetail=%s' % (l, ve)
            if count % 1000 == 0:
                save_list2mongo(ilist, db_name, collection_name)
                print '%s documents inserted' % count
                ilist = []
    save_list2mongo(ilist, db_name, collection_name)
    #   f.write(l + '\n')
    print count





if __name__ == '__main__':
    # handle_meta_gzfile('meta_Apps_for_Android.json.gz','AmazonReviews','AndroidAPP_Meta')
    pass
