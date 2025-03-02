import scrapy


class QuotesSpider(scrapy.Spider):
        name = "quotes"


        def start_requests(self):
            url = 'http://quotes.toscrape.com/'
            tag = getattr(self, 'tag', None)
            if tag is not None:
                url = url + 'tag/' + tag
            yield scrapy.Request(url, self.parse)

        def parse(self, response):
            for quote in response.css('div.quote'):
                yield{
                    'text': quote.css('span.text::text').get(),
                    'author': quote.css('small.author::text').get(),
                    # 'tags': quote.css('div.tags a.tag::text').getall(),
                }

            # fetch next page
            next_page = response.css('li.next a::attr(href)').get()

            # if next page exists, goto the next page and parse it
            # using response.follow instead of scrapy.Request uses relative url.
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)



class AuthorSpider(scrapy.Spider):
        name = 'author'

        start_urls = ['http://quotes.toscrape.com/']

        def parse(self, response):
            author_page_links = response.css('.author + a')
            yield from response.follow_all(author_page_links, self.parse_author)

            pagination_links = response.css('li.next a')
            yield from response.follow_all(pagination_links, self.parse)

        def parse_author(self, response):
            def extract_with_css(query):
                return response.css(query).get(default='').strip()

            yield {
                'name': extract_with_css('h3.author-title::text'),
                'birthdate': extract_with_css('.author-born-date::text'),
                'bio': extract_with_css('.author-description::text'),
            }


class TripSpider(scrapy.Spider):
    name = 'trip'

    # start_urls = [
    #     # 'https://sg.trip.com/travel-guide/attraction/singapore-53/tourist-attractions/?locale=en-SG&curr=SGD'
    #     # 'https://sg.trip.com/?locale=en-sg',
    #     'https://sg.trip.com/global-gssearch/searchlist/search?keyword='
    #               ]
    
    def __init__(self, search_term=None, *args, **kwargs):
        super(TripSpider, self).__init__(*args, **kwargs)
        if not search_term:
            raise ValueError("search_term must be provided")
        self.search_term = search_term

    def start_requests(self):
        url = f"https://sg.trip.com/global-gssearch/searchlist/search?keyword={self.search_term}"
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        target_link = None
        for link in response.css('div.gl-search-result_list div.content a'):
            if link.attrib.get('title') == self.search_term:
                target_link = link.attrib.get('href')
                break

        if target_link:
            yield response.follow(target_link, callback=self.nagivate_to_attractions)
        else:
            self.logger.warning(f"Link with title '{self.search_term}' not found.")

    def nagivate_to_attractions(self, response):
        original_url = response.url
        modified_url = original_url.replace('destination', 'attraction') + '/tourist-attractions'

        yield response.follow(modified_url, callback=self.parse_search_result)
        

    def parse_search_result(self, response):
        author_page_links = response.css('a.xt-link::attr(href)')
        yield from response.follow_all(author_page_links, self.parse_author)

    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()
        def extract_with_xpath(query):
            return response.xpath(query).get(default='').strip()
        
        def extract_with_css_cond(query):
            for element in response.css(query):
                title = element.css('::attr(title)').get() # Get the value of the title attribute
                text = element.css('::text').get(default='').strip() # Get the text content of the div.

                if title and title == text:
                    return text
                
            return ''
        
        def extract_ratings(): 
            rating_element = response.css('span.gl-poi-detail-rating')
            if rating_element:
                rating_parts = rating_element.css('span::text').getall()
                rating = ''.join(rating_parts).strip() if rating_parts else None
            else:
                rating = None

        def extract_review_count():
            # Extract the review count (1.5k Reviews)
            review_element = response.css('div.burited_point.gl-poi-detail_review_content')
            if review_element:
                review_count = review_element.css('::text').get(default='').strip()
            else:
                review_count = None
            
        
        yield {
            'name': extract_with_css('h1[class^="basicName"]::text'),
            'score': extract_with_css('span[class^="hotScore"]::text'),
            # 'rating': extract_ratings(),
            # 'numOfRating': extract_review_count(),
            'attractionType': extract_with_css('span[class^="page-tag"]::text'),
            'address': extract_with_css('div.address-des-info span.field::text'),
            # 'price': extract_with_css('div.book div[class^="TopPriceStyle"]  div.price-content div.tour-price span::text'),
            'openingHours': extract_with_css('div[class^="POITopInfo"] span.field::text'),
            'recommendedDuration': extract_with_css('div[class^="POITopInfo"] div.one-line span.field::text'),
            # 'review': extract_with_css('div.comment-box p::text'),
            'phone': extract_with_css_cond('div[class^="POITopInfo"] span.field')
        }
