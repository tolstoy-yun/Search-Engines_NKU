from whoosh.index import create_in
from whoosh.fields import *
from jieba.analyse import ChineseAnalyzer
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import defaultdict
import pickle
import jieba
from whoosh.index import open_dir
import numpy as np

class Index:
    url_all=set()# url集合
    url_anchor_dict=defaultdict()#url对应的锚文本
    url_relatedurl_dict=defaultdict(list)# url与指向的其他url的映射
    url_content_dict=defaultdict()#url对应的文本内容
    url_id_dict=defaultdict()# url到id的映射
    id_url_dict=defaultdict()#id到url的映射
    url_all_content_dict=defaultdict() #url相关的所有内容
    url_title_dict=defaultdict() #保存url的title
    url_docvector_dict=defaultdict()#url对应的文档向量
    url_vectorlen_dict=defaultdict()#url对应的文档向量的长度
    url_pagerank_dict=defaultdict() #保存url的pagerank值
    ix=None #索引
    data_dir="./data/"
    tfidfVectorizer=None #tfidf模型
    
    def __init__(self):
        self.ix= open_dir('./index')
        with open(self.data_dir+"url","rb") as f:
            self.url_all=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_anchor_dict.txt","rb") as f:
            self.url_anchor_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_relatedurl_dict.txt","rb") as f:
            self.url_relatedurl_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_content_dict","rb") as f:
            self.url_content_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_id_dict","rb") as f:
            self.url_id_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"id_url_dict.txt","rb") as f:
            self.id_url_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_title_dict","rb") as f:
            self.url_title_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_pagerank_dict.txt","rb")as f:
            self.url_pagerank_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_all_content_dict.txt","rb")as f:
            self.url_all_content_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_docvector_dict.txt","rb")as f:
            self.url_docvector_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_vectorlen_dict.txt","rb")as f:
            self.url_vectorlen_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"tfidfVectorizer.txt","rb")as f:
            self.tfidfVectorizer=pickle.load(f)
            f.close()

    #建立索引
    def create_index(self):
        # 创建schema, stored为True表示能够被检索
        schema = Schema(urlid=NUMERIC(stored=True),
                    content=TEXT(stored=True, analyzer=ChineseAnalyzer())
                    )
        # 存储schema信息至indexdir目录
        indexdir = './index/'
        self.ix = create_in(indexdir, schema)
        # 按照schema定义信息，增加需要建立索引的文档
        writer = self.ix.writer()
        for urlid in self.url_all_content_dict.keys():
            all_content = self.url_all_content_dict[urlid]
            writer.add_document(urlid=urlid,content=all_content)
        writer.commit()
    
    #查询
    def query(self):
        # 创建一个检索器
        searcher = self.ix.searcher()
        while(1):
            sentence=input("请输入要查询的内容：")
            if sentence=="close":
                break
            results = searcher.find("content", sentence,limit=None)
            print('一共发现%d份文档：' % len(results))
            best_result=self.result_rank(results,sentence) #评分
            #输出排名前十的答案
            for i in range(0,min(15,len(best_result))):
                result_id=best_result[i][0]
                result_url=self.id_url_dict[result_id]
                print(result_url)
    
    #结巴分词
    def get_words_jieba(self,text):
        words_after_jieba=jieba.cut(text,cut_all=False)
        return words_after_jieba
    
    #结果排序
    def result_rank(self,results,sentence):
        sentence_array=self.query_vector(sentence)
        url_value={}
        #综合考虑向量模型和pagerank
        for i in range(len(results)):
            id=(results[i].fields())[u"urlid"]
            url_docv=self.url_docvector_dict[id]
            length=self.url_vectorlen_dict[id]
            cos=np.sum(url_docv*sentence_array)/length
            url_value[id]=cos+self.url_pagerank_dict[id] #向量模型夹角+pagerank的值
        url_value=sorted(url_value.items(), key=lambda item:item[1], reverse=True)
        return url_value
    
    #查询词的向量
    def query_vector(self,sentence):
        sentence_after_jieba=self.get_words_jieba(sentence)
        sentence_t=self.tfidfVectorizer.transform(sentence_after_jieba)
        sentence_array=sentence_t.toarray()
        return sentence_array

if __name__=='__main__':
    index=Index()
    #index.create_index()
    index.query()