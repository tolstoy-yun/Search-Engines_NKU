from selenium import webdriver
from collections import defaultdict
import re
import pickle
import jieba
from string import punctuation

class Spider:
    url_all=set() #爬取到的所有url
    crawling_list = set() #将要爬取的url
    crawled_list = set() #爬取过的url
    url_anchor_dict=defaultdict() #url与锚文本对应的字典
    url_count=0 #已经爬到了几个url
    data_dir="./data/" #数据存储目录
    url_relatedurl_dict=defaultdict(list) #url指向的其他url
    url_title_dict=defaultdict() #保存url的title
    url_content_dict=defaultdict() #保存url的文本内容
    url_id_dict=defaultdict() #保存url的id号
    url_document_list=set() #文档类url
    doc_type=["doc","pdf","txt","pdf","docx", "xls","xlsx", "ppt", "pptx", "odt"]

    def __init__(self,start_url=None):
        self.crawling_list.add(start_url)
        self.url_all.add(start_url)
        self.url_count=1
        self.url_id_dict[start_url]=0
        self.url_anchor_dict[0]=""
        self.driver = webdriver.Firefox()

    # 获得当前url对应页面中所有的url
    def get_url(self,crawling_url):
        # 爬取url和锚文本
        try:
            self.driver.get(crawling_url)
            title= self.driver.title
            a_href=self.driver.find_elements_by_xpath('//a')
            print("当前正在爬取url："+crawling_url)
            print("url的title："+title)
            for a in a_href:
                url=a.get_attribute("href") # url
                anchor_text=a.text # 锚文本
                if url==None:
                    continue
                if self.url_count>3000:
                    print("已爬3000条url")
                    return 
                # 筛出符合条件的url，建立各种映射关系
                if "http" in url:
                    if "nankai" in url:
                        if url not in self.url_all:
                            for d_t in self.doc_type:
                                if d_t in url:
                                    self.url_document_list.add(url)
                            self.url_count+=1
                            print("第"+str(self.url_count)+"个url："+url)
                            id=self.get_url_id(url)
                            self.url_id_dict[url]=id #建立url与id的映射
                            self.url_relatedurl_dict[self.url_id_dict[crawling_url]].append(id) # 指向的url
                            self.url_anchor_dict[id]=anchor_text # 锚文本
                            self.url_all.add(url)
                            self.crawling_list.add(url)
            print("****************************************************************")
        except Exception:
            print("页面无法正常打开")

    def get_all_url(self):
        cur_crawling_list=self.crawling_list.copy()
        for url in cur_crawling_list:
            if self.url_count>=3000:
                print("已经爬了3000条url了，回去啦")
                return
            if url in self.url_document_list:
                self.crawling_list.remove(url) #将已爬过的url从将要爬的列表中删除
                self.crawled_list.add(url) #将这个url加入爬取过的url
                continue
            self.get_url(url) #获得该url对应页面中的所有url
            self.crawling_list.remove(url) #将已爬过的url从将要爬的列表中删除
            self.crawled_list.add(url) #将这个url加入爬取过的url
        print("已爬取的url个数为："+str(len(self.crawled_list)))
        if len(self.crawling_list)==0:
            return
        self.get_all_url()
    
    #获得url的title和文本内容
    def get_url_content(self):
        c=0
        for url in self.url_all:
            id=self.url_id_dict[url]
            result=""
            title=""
            if url in self.url_document_list:
                print(url+" 是文档类型的url")
            else:
                try:
                    self.driver.get(url)
                    #获取title
                    title= self.driver.title
                    #获取文本内容
                    raw_content=self.driver.find_elements_by_xpath('//div')
                    result=""
                    for r_c in raw_content:
                        content=r_c.text
                        if content!="":
                            result+=content
                except Exception:
                    print("页面无法正常打开")
            self.url_title_dict[id]=title
            c+=1
            print("爬到第"+str(c)+"个")
            print("已爬完第"+str(id)+"个url："+url)
            self.url_content_dict[id]=result
        self.driver.close()
            
    
    # 存储数据，包括url，url对应的anchor的字典，url对应的内容，url对应的title，url指向的其他url
    def store(self):
        with open(self.data_dir+"url","wb") as f:
            pickle.dump(self.url_all,f)
            f.close()
        with open(self.data_dir+"url_anchor_dict.txt","wb") as f:
            pickle.dump(self.url_anchor_dict,f)
            f.close()
        with open(self.data_dir+"url_relatedurl_dict.txt","wb") as f:
            pickle.dump(self.url_relatedurl_dict,f)
            f.close()
        with open(self.data_dir+"url_content_dict","wb") as f:
            pickle.dump(self.url_content_dict,f)
            f.close()
        with open(self.data_dir+"url_id_dict","wb") as f:
            pickle.dump(self.url_id_dict,f)
            f.close()
        with open(self.data_dir+"url_title_dict","wb")as f:
            pickle.dump(self.url_title_dict,f)
            f.close()
    
    def get_url_id(self,url):
        id=len(self.url_all)
        return id

if __name__=='__main__':
    spider = Spider("https://www.nankai.edu.cn/")
    spider.get_all_url() #获取url
    spider.get_url_content() #获取url对应的内容
    spider.store() #将结果存入磁盘