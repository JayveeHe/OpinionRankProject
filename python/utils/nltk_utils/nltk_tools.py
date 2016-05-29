from collections import defaultdict
# import pickle
import cPickle
import string
from nltk import pos_tag, stem
from nltk.tokenize import word_tokenize
from utils.CommonUtils import PROJECT_PATH
import nltk

__author__ = 'jayvee'

idf_vectorizer = None

def tokenize_sents(sent):
    tokens = []
    for token in word_tokenize(sent):
        tokens.append(token)
    return tokens


def stem_tokens(tokens):
    stemmer = stem.SnowballStemmer("english")
    res = []
    for token in tokens:
        res.append(stemmer.stem(token))
    return res


def tag_sents(sent):
    # tags = []
    tokens = tokenize_sents(sent)
    # tags.append()
    return pos_tag(tokens, tagset='universal')


def python():
    t = string.maketrans('dicEuvyaOe', 'adhSonsuTy')
    print 'OcuaydviEavve'.translate(t)


def cal_en_tfidf(sent):
    global idf_vectorizer
    if not idf_vectorizer:
        print 'init idf'
        idf_vectorizer = cPickle.load(
            open('%s/utils/idf_vectorizer' % PROJECT_PATH, 'r'))
    tokens = tokenize_sents(sent)
    idf = idf_vectorizer.idf_
    freq_dict = defaultdict(int)
    res = []
    for token in tokens:
        t = token.lower()
        freq_dict[t] += 1
    for token in tokens:
        t = token.lower()
        tid = idf_vectorizer.vocabulary_.get(t)
        if tid:
            res.append((t, freq_dict[t] * idf[tid]))
    return res


if __name__ == '__main__':
    pass
    python()
    sent = "This is a beautiful place."
    tokens = tokenize_sents(
        sent)
    tags = tag_sents(sent)
    print tags
    # print tag_sents(stem_tokens(tokens))
    # idf_vec = pickle.load(
    #     open('/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/utils/idf_vectorizer', 'r'))
    # print cal_tfidf(sent, idf_vec)
