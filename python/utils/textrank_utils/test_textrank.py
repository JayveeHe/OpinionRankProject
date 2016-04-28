# coding=utf-8
import json

__author__ = 'jayvee'
import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

import codecs

from textrank4zh import TextRank4Keyword, TextRank4Sentence

text = codecs.open('/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/test', 'r', 'utf-8').read()
jsontext = codecs.open(
    '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/crawler/JD_Parser/1461599394-战地吉普AFSJEE-parser_result.json',
    'r', 'utf-8').read()
jsobj = json.loads(jsontext)
jst = ''
for comm in jsobj['comments']:
    jst += comm['content'] + '。'

tr4w = TextRank4Keyword()
#
tr4w.analyze(text=jst, lower=True, window=2)  # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象

print('关键词：')
for item in tr4w.get_keywords(20, word_min_len=1):
    print item.word, item.weight
#
# print()
print('关键短语：')
aa = tr4w.get_keyphrases(keywords_num=20, min_occur_num=2)
for phrase in aa:
    print(phrase)

tr4s = TextRank4Sentence()
tr4s.analyze(text=jst, lower=True, source='all_filters')

print('摘要：')
for item in tr4s.get_key_sentences(num=20):
    print item.weight, item.sentence
