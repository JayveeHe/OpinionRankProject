# coding:utf-8
# Compatible with Python2.x & 3.x
# Email：lidongone@qq.com
import os
import sys
import arrow
import time
from utils.CommonUtils import timer

try:
    from gevent import monkey  # 有gevent就用它比较快，没有就用内置多线程，同时也为py3兼容

    monkey.patch_all()
    from gevent.pool import Pool
except:
    from multiprocessing.dummy import Pool  # py2和3通用的多线程
import requests
import json
import random

reload(sys)
sys.setdefaultencoding('utf-8')
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))
# import uniout
# 。这个库可以让python2像3一样print中文列表


'''
#声明：
该源码仅为学习交流使用，不用于商业用途，如有侵权问题

请及时联系lidongone@qq.com撤销全部代码

##介绍：

文件名：get_jd.py
用途：非官方-京东商品爬虫API（包括价格、评论等），评分在评价的返回页面里有，销量暂时无法抓取。

抓取所有评论页耗费时间：

Python2 :3.19 s

Python3 :4.21 s

## 函数说明：
get_jd_rate：根据商品ID与页码获得评论页面的源代码，后续解析工作暂时不做了，就是解析Json

get_jd_rate_totalpagenum：根据商品ID得到评论页码范围，返回值是整型数字，最大页码-1，因为从0开始

get_jd_rate_all：根据商品ID抓取所有评论，返回结果是按顺序存放页面源码的列表

get_jd_price：根据商品ID抓取价格，这个速度最快，而且从来不会封IP

######modifie：2014-11-09 11:23:36
'''
# 没这header就抓不到
headers = {'Host': 'club.jd.com',
           'Referer': 'http://item.jd.com/0.html'}


def get_jd_title(pid):
    aa = get_jd_rate(pid, 0)
    try:
        title = json.loads(aa)["comments"][0]['referenceName']
    except:
        title = 'Null'
    return title


def get_jd_rate(pid, pagenum):
    '''页码从0开始，在网页上显示的第一页'''
    print 'crawling page:%s' % pagenum
    for i in range(3):
        # 因为经常抓到空数据，所以重试20次（本来是while 1）
        try:
            r = requests.get(
                'http://club.jd.com/productpage/p-{}-s-0-t-3-p-{}.html'.format(pid, pagenum), timeout=3,
                headers=headers)
            if 'content-length' in r.headers or len(r.text) < 1:
                # 一般它的值要么是0说明没抓到数据(包括页码超出)，要么不存在
                r = random.random() * 10
                print 'retry sleep %s seconds' % r
                time.sleep(r)
                continue
            else:
                print(pid, pagenum, 'get it', len(r.text))
                return r.text
                # continue
        except Exception as e:
            print 'error!!!!!!'
            print e
            r = random.random() * 3
            print 'sleep %s seconds' % r
            time.sleep(r)
            continue
            # print(pid, pagenum, 'failed')
    return None


def get_jd_rate_totalpagenum(pid):
    # 得到的是pagenum的最大数字，页面上显示的页码，还要+1
    try:
        totalpn = json.loads(get_jd_rate(pid, 0))[
            'productCommentSummary']['commentCount']
        return totalpn // 10
    except:
        # print('failed')
        return -1


def get_jd_rate_all(pid):
    maxpn = get_jd_rate_totalpagenum(pid)
    if maxpn == -1:
        # print('null')
        return
    pp = Pool(100)
    result = pp.map(
        lambda x: get_jd_rate(x[0], x[1]), list(zip([pid] * (maxpn + 1), range(maxpn + 1))))
    try:
        pp.close()
        pp.join()
    except Exception, e:
        pass
    return result


def get_jd_price(*pid):
    # 可以是多个PID
    pids = ','.join(['J_{}'.format(i) for i in pid])
    url = 'http://p.3.cn/prices/mgets?skuids=' + pids
    r = requests.get(url)
    return r.content


def getjd(pid):
    aa = get_jd_rate_all(pid)
    # print aa[0]

    aa = [json.loads(i)['comments'] for i in aa if i]
    aa = sum(aa, [])
    aa = [i['content'].strip() for i in aa]

    return '\n'.join(aa)


def getjd_range(pid, mxpage=10):
    maxpn = get_jd_rate_totalpagenum(pid)
    if maxpn == -1:
        # print('null')
        return
    maxpn = min(maxpn, mxpage)
    pp = Pool(100)
    result = pp.map(
        lambda x: get_jd_rate(x[0], x[1]), list(zip([pid] * (maxpn + 1), range(maxpn + 1))))
    try:
        pp.close()
        pp.join()
    except Exception, e:
        # 解析
        pass
    print 'pp done'
    res = []
    print len(result)
    for iline in result:
        # print iline
        try:
            a = json.loads(iline)
            res.extend(a.get('comments'))
        except ValueError, ve:
            print ve
            print iline
    return {'pid': pid, 'max_page': maxpn, 'comments': res}


def getjd_range_no_pool(pid, mxpage=10):
    maxpn = get_jd_rate_totalpagenum(pid)
    if maxpn == -1:
        # print('null')
        return
    maxpn = min(maxpn, mxpage)
    result = []
    for i in xrange(maxpn):
        page = get_jd_rate(pid, i)
        if page:
            result.append(page)
            r = random.random() * 2
            print 'page %s done!\tsleep %s seconds' % (i, r)
            time.sleep(r)
        else:
            print 'skip page %s' % i
    res = []
    print len(result)
    for iline in result:
        # print iline
        try:
            a = json.loads(iline)
            res.extend(a.get('comments'))
        except Exception, e:
            print e
            print iline
    return {'pid': pid, 'max_page': maxpn, 'comments': res}


# @timer
def get_and_save_jd_range(pid, max_page, fout_path=None):
    """
    保存京东的comment，并返回爬取的数据（json形式）
    :rtype : object
    :param pid:
    :param max_page:
    :param fout_path:
    :return:
    """
    # res = getjd_range(pid, max_page)
    res = getjd_range_no_pool(pid, max_page)
    title = get_jd_title(pid).replace(' ', '')
    print title
    res['title'] = title
    if not fout_path:
        title = title[:10]
        fout_path = '%s/data/%s-%s.json' % (PROJECT_PATH, arrow.utcnow().timestamp, title)
    with open(fout_path, 'w') as fout:
        fout.write(json.dumps(res, ensure_ascii=False))
        return res


if __name__ == '__main__':
    import time

    aa = time.time()
    # getjd(187678)
    # res = get_jd_rate(187678, 0)
    ITEM_ID = 996964
    MAXPAGE = 20
    # res = getjd_range(ITEM_ID, MAXPAGE)
    # jres = json.loads(res)
    # title = get_jd_title(ITEM_ID).replace(' ', '')
    # print(title)
    # open('%s/crawler/data/%s.json' % (PROJECT_PATH, title[:10]), 'w').write(json.dumps(res, ensure_ascii=False))
    # jd_result = get_jd_rate_all(187678)
    # fout = open(get_jd_title(187678), 'w')
    # total = []
    # print len(jd_result)
    # count = 0
    # for r_page in jd_result:
    #     print len(r_page)
    #     print r_page
    #     print '======='
    #     r_page = r_page.replace('\\"', '"')
    #     print r_page
    #     jd_result[count] = r_page
    #     count +=1
    #     # json_page = json.loads(r_page)
    #     # total.append(json_page)
    #
    # str_result = json.dumps(jd_result)
    # # str_result = str_result.replace('\\"', '"')
    # fout.write(str_result)
    print time.time() - aa
