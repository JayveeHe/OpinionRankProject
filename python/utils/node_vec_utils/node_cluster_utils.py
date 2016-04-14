import json

__author__ = 'jayvee'


def APcluster(sentenceNodeManager, fout_path):
    veclist = []
    sentlist = []
    labellist = []
    tokenlist = []
    nodelist = []
    sentenceNodeManager.normalize_all_sentnodes()
    veclist.extend(sentenceNodeManager.get_vec_list())
    sentlist.extend(sentenceNodeManager.get_sent_list())
    for node in sentenceNodeManager.node_list:
        labellist.append(node.extra)
        tokenlist.append(node.feature2token())
        nodelist.append(node)


    # sentenceNodeManager.
    import sklearn.cluster as SC

    ap = SC.AffinityPropagation()
    c_res = ap.fit_predict(veclist)
    # ap.preference()
    clusters = {}
    for i in range(len(c_res)):
        if clusters.get(c_res[i]):
            clusters[c_res[i]].append(sentlist[i])
        else:
            clusters[c_res[i]] = [sentlist[i]]
    open(fout_path, 'w').write(json.dumps(clusters, ensure_ascii=False))
    print 'APcluster result:%s' % fout_path


def DBSCANcluster(sentenceNodeManager, fout_path):
    veclist = []
    sentlist = []
    labellist = []
    tokenlist = []
    nodelist = []
    sentenceNodeManager.normalize_all_sentnodes()
    veclist.extend(sentenceNodeManager.get_vec_list())
    sentlist.extend(sentenceNodeManager.get_sent_list())
    for node in sentenceNodeManager.node_list:
        labellist.append(node.extra)
        tokenlist.append(node.feature2token())
        nodelist.append(node)


    # sentenceNodeManager.
    import sklearn.cluster as SC

    dbscan = SC.DBSCAN()
    c_res = dbscan.fit_predict(veclist)
    clusters = {}
    for i in range(len(c_res)):
        if clusters.get(c_res[i]):
            clusters[c_res[i]].append(sentlist[i])
        else:
            clusters[c_res[i]] = [sentlist[i]]
    open(fout_path, 'w').write(json.dumps(clusters, ensure_ascii=False))
    print 'DBSCANcluster result:%s' % fout_path

