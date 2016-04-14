import codecs
import json
import datetime
import arrow
from crawler.JD_Parser.get_jd import get_and_save_jd_range, get_jd_rate
from utils.node_vec_utils.global_utils import SentenceNodeManager
from utils.node_vec_utils.vec_building_utils import SentenceNode

__author__ = 'jayvee'


def jd_parser(pid, max_page):
    res = get_and_save_jd_range(pid, max_page)
    # print res
    comments = res['comments']
    result = {'pid': pid, 'title': res['title'], 'max_page': max_page, 'comments': []}
    for comment in comments:
        result['comments'].append({'content': comment['content'], 'creationTime': comment['creationTime'],
                                   'nickname': comment['nickname'], 'user_id': comment['id']})
    return result


def save_csv(jd_result, fout_path=None):
    if not fout_path:
        fout_path = jd_result['title'][:10]
    with open('../data/csv/%s-%s.csv' % (arrow.utcnow().timestamp, fout_path), 'w') as fout:
        fout.write(codecs.BOM_UTF8)
        for item in jd_result['comments']:
            fout.write('%s,%s,%s,0,%s\n' % (
                jd_result['pid'], item['creationTime'], item['nickname'], item['content'].replace('\n', '')))
        print 'saved! path = %s' % fout_path


if __name__ == '__main__':
    ITEM_ID = 1441414
    MAXPAGE = 30
    # RES = get_jd_rate(ITEM_ID,MAXPAGE)
    jd_res = jd_parser(ITEM_ID, MAXPAGE)
    open('%s-%s-parser_result.json' % (arrow.utcnow().timestamp, jd_res['title'][:10]), 'w').write(
        json.dumps(jd_res, ensure_ascii=False))
    save_csv(jd_res)
    # add sentence
    # st = open('parser_result.json', 'r').read()
    # jd_res = json.loads(st)
    snm = SentenceNodeManager()
    for item in jd_res['comments']:
        snm.add_node(SentenceNode(item['content']))
    import utils.node_vec_utils.node_cluster_utils as CU

    CU.APcluster(snm, '../data/clusters/%s-APresult.json' % jd_res['title'][:10])
    CU.DBSCANcluster(snm, '../data/clusters/%s-DBSCANresult.json' % jd_res['title'][:10])
