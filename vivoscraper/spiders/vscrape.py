import scrapy
from scrapy.http.request import Request
from ..items import VivoscraperItem
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class VscrapeSpider(scrapy.Spider):
    name = 'vscrape'

    # airtable = Airtable(api_key=PERSONAL_ACCESS_TOKEN, base_id=BASE_ID)

    def start_requests(self):
        base_url = 'https://www.vivobarefoot.com/us/{}'

        options = Options()
        options.add_argument("--headless")
        driver = Chrome(executable_path='E:\contents\Software\chrome_driver\chromedriver.exe', options=options)

        # available categories
        categories = ['mens', 'womens', 'kids']
        pages = list()

        for category in categories:
            # concatenate the category with the base url
            category_url = base_url.format(category) + '?p={}'
            page_number = 1
            while True:
                page_url = category_url.format(page_number)
                print(f'page url : {page_url}')
                driver.get(page_url)
                
                try:
                    has_product = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.product-item-link'))
                    )

                    pages.append({'page_url' : page_url, 'category' : category})
                    page_number += 1
                except:
                    break
        
        driver.quit()
                
        for page in pages:
            yield Request(page['page_url'], callback=self.link_collector, cb_kwargs={'category' : page['category']})


    def link_collector(self, response, category):
        if response.status == 200:
            products = response.css('.product-item-link::attr(href)').extract()
            if products:
                for product_url in products:
                    if "?" in product_url:
                        product_url = product_url.split("?")[0]
                    print(product_url)
                    yield response.follow(product_url, callback=self.scraper, cb_kwargs={
                            'product_url' : product_url,
                            'product_category' : category
                        })
                        
                print(f'there were {len(products)} products')
                

    def scraper(self, response, product_url, product_category):
        items = VivoscraperItem()

        selectors = {
            'product_name' : 'span.base',
            'product_price' : 'span[data-price-type="finalPrice"] .price',
            'product_description' : '//div/strong[text()="Description"]/../div',
            'product_description_2' : '//div/strong[text()="Description"]/../div/*'
        }

        if response.status == 200:
            items['product_name'] = response.css(selectors['product_name']).css('::text').get()
            items['product_url'] = product_url
            product_price = response.css(selectors['product_price']).css('::text').get()
            if product_price != None:
                items['product_price'] = float(product_price.split('$')[1])
            else:
                items['product_price'] = 0.00

            items['product_description'] = response.xpath(selectors['product_description'] + '/text()').get()

            if not items.get('product_description') or len(items['product_description']) < 5:
                items['product_description'] = response.xpath(selectors['product_description_2'] + '/text()').get()

            items['product_category'] = product_category

            yield items

