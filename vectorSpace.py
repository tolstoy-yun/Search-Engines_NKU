from sklearn.feature_extraction.text import TfidfVectorizer
import jieba
import re
from collections import defaultdict
import pickle
import numpy as np

class VectorSpace:
    url_all=set()# url集合
    url_id_dict=defaultdict()# url到id的映射
    id_url_dict=defaultdict()#id到url的映射
    url_all_content_dict=defaultdict() # url相关的所有内容
    data_dir="./data/"
    url_content_after_jieba_dict=defaultdict()#url对应的分词后的文档
    url_docvector_dict=defaultdict()#url对应的文档向量
    url_vectorlen_dict=defaultdict()#url对应的文档向量的长度
    tfidfVectorizer=None #向量模型
    text_dimension=None #文档维度
    text_matrix=None #文档向量
    
    def __init__(self):
        with open(self.data_dir+"url","rb") as f:
            self.url_all=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_id_dict","rb") as f:
            self.url_id_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"id_url_dict.txt","rb") as f:
            self.id_url_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_all_content_dict.txt","rb")as f:
            self.url_all_content_dict= pickle.load(f)
            f.close()

    #结巴分词
    def get_words_jieba(self,text):
        words_after_jieba=jieba.cut(text,cut_all=False)
        content=" ".join(words_after_jieba)
        return content

    #向量空间模型
    def doc_vector(self):
        allcontent=[]
        dimension_id={}
        #将所有url的内容合成一个list
        for url in self.url_all:
            id=self.url_id_dict[url]
            content=self.url_all_content_dict[id]
            content_deal= re.sub(" ", "",content)
            content_deal= re.sub("\n", "",content)
            content_final=self.get_words_jieba(content_deal)
            self.url_content_after_jieba_dict[id]=content_final
            dimension_id[len(allcontent)]=id
            allcontent.append(content_final)
        self.text_dimension=dimension_id

        #构建向量空间模型
        self.tfidfVectorizer = TfidfVectorizer(use_idf=True,smooth_idf=True,norm=None)#设置解析方法
        tfidf_matrix = self.tfidfVectorizer.fit_transform(allcontent)
        vector_array=tfidf_matrix.toarray()

        #获取每个文档的向量和向量长度，并建立url与其的映射
        self.text_matrix=np.array(vector_array)
        for dimension in range(len(vector_array)):
            uid=dimension_id[dimension]
            doc_array=np.array(vector_array[dimension])
            self.url_docvector_dict[uid]=doc_array
            array_len=np.linalg.norm(doc_array)   
            self.url_vectorlen_dict[uid]=array_len
        
        #存储
        with open(self.data_dir+"url_docvector_dict.txt","wb")as f:
            pickle.dump(self.url_docvector_dict,f)
            f.close()
        with open(self.data_dir+"url_vectorlen_dict.txt","wb")as f:
            pickle.dump(self.url_vectorlen_dict,f)
            f.close()
        with open(self.data_dir+"tfidfVectorizer.txt","wb") as f:
            pickle.dump(self.tfidfVectorizer,f)
            f.close()
        with open(self.data_dir+"text_matrix.txt","wb") as f:
            pickle.dump(self.text_matrix,f)
            f.close()

vectorspace=VectorSpace()
vectorspace.doc_vector()