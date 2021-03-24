import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import ServisItem
from itemloaders.processors import TakeFirst
import datetime
pattern = r'(\xa0)?'

class ServisSpider(scrapy.Spider):
	name = 'servis'
	now = datetime.datetime.now()
	year = now.year
	start_urls = [f'https://www.servisfirstbank.com/news?year={year}']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news"]/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = 'https://www.servisfirstbank.com/news?year={}'
		if self.year >= 2014:
			self.year -= 1
			yield response.follow(next_page.format(self.year), self.parse)


	def parse_post(self, response):
		date = response.xpath('//div[@id="story_date"]/text()').get().strip()
		title = response.xpath('//div[@id="story_title"]/text()').get().strip() + response.xpath('//div[@id="story_subtitle"]/text()').get().strip()
		content = response.xpath('//div[@id="story_copy_holder"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=ServisItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
