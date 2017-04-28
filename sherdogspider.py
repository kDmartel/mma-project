from __future__ import print_function
import datetime
import scrapy

#Scrapy spider for crawling Sherdog fight database

fighters = {}
fights = set()

MAX_DEPTH = 20

fights_file = open('fights.csv', 'w')
fighter_file = open('fighter_file.csv', 'w')
                    
class SherdogSpider(scrapy.Spider):
    name = 'sherdogspider'
    start_urls = ['http://www.sherdog.com/organizations/Ultimate-Fighting-Championship-2']

    def parse(self, response):
        for url in response.xpath("//a/@href").extract():
            if url.startswith("/events/UFC-"):
                url = response.urljoin(url)                
                yield scrapy.Request(url, self.parse_event)

    def parse_event(self, response):
        fighters_l = set()
        for s in response.xpath("//tr"):
            for t in s.xpath('td[contains(@class, "text")]'):
                fighter = t.xpath("div/a/@href").extract()
                if len(fighter) == 1:
                    fighters_l.add(fighter[0])
        for f in fighters_l:
            if f in fighters:
                continue
            req = scrapy.Request(response.urljoin(f), self.parse_fighter)
            req.meta["fighter"] =  f
            req.meta["dpth"] =  0
            yield req
            

    def parse_fighter(self, response):       
        fighter = response.meta["fighter"]
        print (response.meta["dpth"], response.meta["fighter"], fighter in fighters)
        depth = response.meta["dpth"]
        if fighter in fighters:
            return
        nationality = response.xpath('//strong[contains (@itemprop,"nationality")]/text()').extract()
        if len(nationality) == 1:
            nationality = nationality[0]
        else:
            nationality = ""

        weight  = response.xpath('//span[contains (@class,"item weight")]/strong/text()').extract()
        if len(weight) == 1:
            weight = weight[0]
        else:
            weight = ""
        
        height = response.xpath('//span[contains (@class,"item height")]/text()').extract()
        if len(height) >= 1:
            height = height[2].strip()
        else:
            height = ""

        wc = response.xpath('//h6[contains (@class,"item wclass")]/strong[contains (@class,"title")]/a[contains (@href,"/stats")]/text()').extract()
        if len(wc) == 1:
            wc = wc[0]
        else:
            wc = ""
    
        birthday = response.xpath('//span[contains (@itemprop,"birthDate")]/text()').extract()
        if len(birthday) == 1:
            birthday = birthday[0]
        else:
            birthday = ""
        
        #test = response.xpath('//span[contains (@class,"item height")]/text()').extract()
        #if len(test) >= 1:
        #    test = test[2].strip()
        #else:
        #    test = ""
        
        #img = response.xpath('//div/img[contains(@itemprop,"image")]/@src').extract()
        #if len(img) == 1:
        #    img = img[0]
        #else:
        #    img = ""

        fighters[fighter] = {"nationality" : nationality}
        fighters[fighter] = {"weight" : weight}
        fighters[fighter] = {"wc" : wc}
        fighters[fighter] = {"height" : height}
        fighters[fighter] = {"birthday" : birthday}
        #fighters[fighter] = {"test" : test}
        #fighters[fighter] = {"img" : img}
        #fighter_file.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (fighter,nationality,wc,weight,height, birthday,img))
        #fighter_file.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (fighter,nationality,wc,weight,height,birthday,test))
        fighter_file.write("%s\t%s\t%s\t%s\t%s\t%s\n" % (fighter,nationality,wc,weight,height,birthday))
        
        for s in response.xpath("//tr"):
            res = s.xpath('td/span[contains(@class, "final")]/text()').extract()
            if res != []:
                try:
                    res = res[0]
                    tds = s.xpath("td")
                    opponent = tds[1].xpath("a/@href").extract()[0]
                    dt = tds[2].xpath("span/text()").extract()[0]
                    fight = tuple(sorted([fighter, opponent])), dt
                    if fight in fights:
                        continue
                    else:
                        fights.add(fight)
                    method = tds[3].xpath("text()").extract()[0]
                    round = tds[4].xpath("text()").extract()[0]
                    min = tds[5].xpath("text()").extract()[0]
                    data = [fighter, opponent, res, method, round, min, dt]
                    fights_file.write("\t".join([d.strip() for d in data]))
                    fights_file.write("\n")
                    
                    if (opponent not in fighters) and response.meta["dpth"] < MAX_DEPTH:
                        req = scrapy.Request(response.urljoin(opponent), self.parse_fighter)
                        req.meta["fighter"] =  opponent
                        req.meta["dpth"] = depth + 1 
                        yield req                    
                except Exception as e:
                    pass
                
                
                
