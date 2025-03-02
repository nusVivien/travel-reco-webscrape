import scrapy


class QuotesSpider(scrapy.Spider):
        # Project Objective: `scrapy crawl toscrape-xpath -o xpath-scraper-results.json`
        name = "toscrape-xpath"


        def start_requests(self):
            url = 'http://quotes.toscrape.com/'
            tag = getattr(self, 'tag', None)
            if tag is not None:
                url = url + 'tag/' + tag
            yield scrapy.Request(url, self.parse)

        def parse(self, response):
            for quote in response.xpath('//*[contains(@class, "quote")]'):
                yield{
                    'text': quote.xpath('span[contains(@class, "text")]/text()').extract_first(),
                    'author': quote.xpath('span/small[contains(@class,"author")]/text()').extract_first(),
                }

            # fetch next page
            next_page = response.xpath('//*[contains(@class,"next")]/a').attrib['href']

            # if next page exists, goto the next page and parse it
            # using response.follow instead of scrapy.Request uses relative url.
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)



class AuthorSpider(scrapy.Spider):
        name = 'authors_xpath'

        start_urls = ['http://quotes.toscrape.com/']

        def parse(self, response):
            # author_page_links = response.css('.author + a')
            author_page_links = response.xpath('//*[contains(@class,"author")]/following-sibling::a')
            yield from response.follow_all(author_page_links, self.parse_author)

            pagination_links = response.css('li.next a')
            # pagination_links = response.xpath('//li[contains(@class,"next")]/a')
            yield from response.follow_all(pagination_links, self.parse)

        def parse_author(self, response):
            def extract_with_css(query):
                return response.css(query).get(default='').strip()
            
            def extract_with_xpath(query):
                return response.xpath(query).get(default='').strip()

            yield {
                # 'name': extract_with_css('h3.author-title::text'),
                'name': extract_with_xpath('//*/h3[contains(@class,"author-title")]/text()'),
                # 'birthdate': extract_with_css('.author-born-date::text'),
                'birthdate': extract_with_xpath('//*[contains(@class,"author-born-date")]/text()'),
                # 'bio': extract_with_css('.author-description::text'),
                'bio': extract_with_xpath('//*[contains(@class,"author-description")]/text()'),
            }
