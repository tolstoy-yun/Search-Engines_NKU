from collections import defaultdict
import pickle
import jieba
import re

#增加id到url的映射，拼接url对应的锚文本、文本和title
class Processing:
    url_all=set()# url集合
    url_anchor_dict=defaultdict()#url对应的锚文本
    url_content_dict=defaultdict()#url对应的文本内容
    url_id_dict=defaultdict()# url到id的映射
    url_all_content_dict=defaultdict() #url相关的所有内容
    url_title_dict=defaultdict() #保存url的title
    data_dir="./data/"
    id_url_dict=defaultdict()#id到url的映射

    def __init__(self):
        with open(self.data_dir+"url","rb") as f:
            self.url_all=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_anchor_dict.txt","rb") as f:
            self.url_anchor_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_content_dict","rb") as f:
            self.url_content_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_id_dict","rb") as f:
            self.url_id_dict=pickle.load(f)
            f.close()
        with open(self.data_dir+"url_title_dict","rb") as f:
            self.url_title_dict=pickle.load(f)
            f.close()

    #建立id到url的映射
    def id_url(self):
        for url in self.url_all:
            id=self.url_id_dict[url]
            self.id_url_dict[id]=url
        with open(self.data_dir+"id_url_dict.txt","wb") as f:
            pickle.dump(self.id_url_dict,f)
            f.close()
    
    #对文档进行处理
    def deal_content(self):
        for url in self.url_all:
            id=self.url_id_dict[url]
            #去掉空格
            content=self.url_content_dict[id]
            content_deal= re.sub(" ", "",content)
            anchor=self.url_anchor_dict[id]
            anchor_deal=re.sub(" ","",anchor)
            title=self.url_title_dict[id]
            title_deal=re.sub(" ","",title)
            self.url_all_content_dict[id]=content_deal+anchor_deal+title_deal
        with open(self.data_dir+"url_all_content_dict.txt","wb")as f:
            pickle.dump(self.url_all_content_dict,f)

if __name__=='__main__':
    processing=Processing()
    processing.id_url()
    processing.deal_content()
