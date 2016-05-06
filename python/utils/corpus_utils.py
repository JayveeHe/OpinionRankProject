import pickle
from gensim import models, corpora
from utils.gensim_utils.basic_utils import get_corpus_by_lists
from utils.nltk_utils.nltk_tools import stem_tokens

__author__ = 'jayvee'
from nltk.corpus import brown


def cal_idf():
    # brown.sents()
    total_wordlists = []
    doc_sents = []
    for f in brown.fileids():
        print f
        doc_wordlist = []
        doc_sentlist = brown.sents(fileids=[f])
        d_sents = ''
        for sent in doc_sentlist:
            s = ''
            # sent = stem_tokens(sent)
            for w in sent:
                w = w.lower()
                s += w + ' '
            d_sents += s + '\n'
            doc_wordlist.extend(sent)
        total_wordlists.append(doc_wordlist)
        doc_sents.append(d_sents)
    print 'start caling tfidf'

    from sklearn.feature_extraction.text import TfidfVectorizer
    corpus = doc_sents
    vectorizer = TfidfVectorizer(min_df=1)
    X = vectorizer.fit_transform(corpus)
    idf = vectorizer.idf_
    # print dict(zip(vectorizer.get_feature_names(), idf))
    pickle.dump(vectorizer, open('idf_vectorizer', 'w'))
    dictionary = corpora.Dictionary(total_wordlists)
    dic, corps = get_corpus_by_lists(total_wordlists)
    tfidf = models.TfidfModel(corps, id2word=dic)
    pickle.dump(tfidf, open('brown_tfidf', 'w'))


if __name__ == '__main__':
    cal_idf()
    tfidf = pickle.load(open('brown_tfidf', 'r'))
    print len(tfidf)
