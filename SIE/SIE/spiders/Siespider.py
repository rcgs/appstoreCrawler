from SIE.items import SieItem
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from lxml import  html
from datetime import datetime
from datetime import date
import scrapy
import pymysql.cursors
from scrapy import log
import  re

class SieSpider(scrapy.Spider):
    name = "SIE"
    allowed_domains = ["apple.com"]
    start_urls = [
    
     
    ]
    #start_urls=["https://itunes.apple.com/jp/genre/ios-gemu/id6014?letter=R&mt=8&page=5"]
    #rules = [Rule(LinkExtractor(),callback='parse_data)]
    SerialID =None
    VerID = None
    EvalID = None
    use_tables ={
        "SI":"titledb",
        "SIV":"versiondb",
        "SIE":"evaldb",
       
    }
    start_number=0
    connection =None
    cursor =None

    def __init__(self,*args,**kwargs):

        
        self.connection = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            db="appstore",
            charset ="utf8",
            autocommit=True
        )
        self.cursor = self.connection.cursor()

    def parse(self, response):
        for sel in response.xpath('//div[@id="selectedgenre"]//div/ul/li'):
            #self.logger.info(response.url)
            link = sel.xpath('a/@href').extract()
            link = self.fair_str(link)
            
            
            yield scrapy.Request(url=link,callback=self.parse_page)

        

        xpath_next = "//div[2]/ul[2]/li/a[@class='paginate-more']/@href"
        nextpage = response.xpath(xpath_next).extract()
        next=nextpage
        #log.msg("nextpage is" + nextpage, levenl=log.DEBUG)
        if nextpage :
            next_url = str(nextpage)
            next_url = re.sub(r"[~\[\']", "", next_url)
            next_url = re.sub(r"[\'\]$]", "", next_url)
            request = scrapy.Request(url=next_url)
            yield request

 



    def parse_page(self, response):
        #for sel in response.xpath('//div[@id="main"]'):
        #self.SerialID=self.get_ID(100,"AP") 
        item = appallItem()
        #titleDB

            #正規表現抽出
        item['URL'] = self.fair_str(response.url)
        item['title'] = self.fair_str(response.xpath('.//h2[@id="softTitle"]/text()').extract())
        item['maker'] = self.fair_str(response.xpath('.//p[@id="makerName"]/text()').extract())
        item['date'] = self.fair_str(response.xpath('.//td[@id="releaseDate"]/text()').extract())
        item['price'] = self.fair_str(response.xpath('.//td[@id="softPrice"]/text()').extract())
        item['genre'] = self.fair_str(response.xpath('.//td[@id="releaseDate"]/text()').extract())
        item['platform'] = self.fair_str(response.xpath('.//td[@id="platform"]/text()').extract())
        item['style'] = self.fair_str(response.xpath('.//td[@id="format"]/text()').extract())
        item['rating'] = self.fair_str(response.xpath('.//a[@id="ceroAge"]/img/@alt').extract())
        item['ratecategory'] = self.fair_str(response.xpath('.//td[@class="category-type"]//span/text()').extract())
        item['player'] = self.fair_str(response.xpath('.//td[@id="player"]/text()').extract())
        item['copyright'] = self.fair_str(response.xpath('.//div[@id="software-copyright-area"]/text()').extract())
        item['descript'] = self.fair_str(response.xpath('.//div[@class="about-info type-text"]/.').extract())
        item['otherpac'] = self.fair_str(response.xpath('.//div[@id="explain-link"]/a/@alt').extract())
        item['info'] = self.fair_str(response.xpath('.//div[@id="explain-vitaicon-area"]//img/@alt').extract())
        item['timestamp'] = self.fair_str(datetime.datetime.utcnow() + datetime.timedelta(hours=9)) # 現在時間。日本時間にして突っ込む。
        #return item
        #item['SerialID'] = self.SerialID()
                #有無判定
        #item['gotDate'] = str(date.today())
        #item['gotDate'] = self.fair_str(response.xpath('//li[@class="release-date"]/span/text()').extract(),self.check_date)
            #正規表現抽出
            #正規表現抽出
        #//div[5]/div/div/div/div/div/a/div[@class="artwork"]/img/@src
        
#有無判定
     

        #VersionDB
        #item['VerID']=self.VerID()
        #item['version'] = self.fair_str(response.xpath('//ul/li[4]/span[@itemprop="softwareVersion"]/text()').extract())
        #item['lastUpdate']
        #item['contents']

        #EvaluationDB
        #item['EvalID']=self.EvalID()
                #有無判定
        #item['currentEval'] = self.fair_str(response.xpath('//div[3]/div[2]/div[@class ="rating"][1]/@aria-label[1]').extract(),self.check_none)
                #有無判定
        #item['allEval'] = self.fair_str(response.xpath('//div[3]/div[2]/div[@class ="rating"][2]/@aria-label[1]').extract(),self.check_none)
                #有無判定
                #yield item
        return item




        #for sel in response.xpath('//div[@id="selectedgenre"]//div/ul/li'):
        #    item = appItem()
        #    item['title'] = sel.xpath('a/text()').extract()
        #    item['link'] = sel.xpath('a/@href').extract()

        #    log.msg("WORKING\n", level=log.DEBUG)

        #    yield item

        """
        scrapyのデータを時価で取得すると['   ']という感じで行末行頭に余分な文字が
        発生するため削除を行う関数
        """

    def fair_str(self,string,function=None,regexp=None):
        #余分な文字列を削除

        string = re.sub(r"[~\[\']", "", str(string)) 
        string = re.sub(r"[\'\]$]", "", str(string))
        
        if function is not None and regexp is None:#追加の関数があった場合
            string = function(string) 
        

        if function is not None and regexp is not None:#正規表現のパターンが入力されていた場合
            string =function(string,regexp)
        

        return string 

    def check_none(self,string):
        if string is "":
            string = ";none"
        return string

    def regexp(self,string,regexp):
        match = re.search(regexp,string)
        if match is not None:
            string = match.group()
            log.msg(string,level = log.DEBUG)
        else:
            string = ";none"
        return string
    
    def check_bit(self,string):
        if string is "" :
            return 0
        else:
            return 1
    def check_int(self,string):
        match = re.search(r"[0-9]+",string)
        if match is not None:
            string =match.group() 
            return string
        else:
            string ="0"
            return string

    def check_date(self,string):
        match = re.search(r'[0-9]{4}.[0-9]+.[0-9]+',string)
        re_string = None
        if match is not None:
            re_string = match.group()
            #log.msg(re_string,level=log.DEBUG)
            re_string = re.sub(r"([一-龥])","-",re_string)
            #log.msg(re_string,level=log.DEBUG)
        #else:
            #log.msg(match.group(),level=log.DEBUG)
        return re_string


