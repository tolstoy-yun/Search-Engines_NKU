import os
import networkx as nx
import pickle
from collections import defaultdict

#链接分析
class PageRank:
    url_all=set()
    url_anchor_dict=defaultdict()#url对应的锚文本
    url_relatedurl_dict=defaultdict(list)
    url_content_dict=defaultdict()#url对应的文本内容
    url_id_dict=defaultdict()# url与id的映射
    url_all_content_dict=defaultdict() #url相关的所有内容
    url_title_dict=defaultdict() #保存url的title
    url_pagerank_dict=defaultdict() #保存url的pagerank值
    data_dir="./data/"
    id_url_dict=defaultdict()#id与url的映射
    G=nx.DiGraph()

    def __init__(self):
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

    def rank(self):
        #pageRank
        for url in self.url_all:
            head=self.url_id_dict[url]
            id=self.url_id_dict[url]
            tails=self.url_relatedurl_dict[id]
            for tail in tails:
                self.G.add_edge(head,tail)
        pr=nx.pagerank(self.G,alpha=0.85)
        # 将每个url计算出的pagerank值与urlid建立映射
        for node, value in pr.items():
            self.url_pagerank_dict[node]=value
        #存入磁盘
        self.save()

    #存储
    def save(self):
        with open(self.data_dir+"url_pagerank_dict.txt","wb")as f:
            pickle.dump(self.url_pagerank_dict,f)
            f.close()

if __name__ == "__main__":
    pagerank=PageRank()
    pagerank.rank()