from itemadapter import ItemAdapter
from pyairtable import Table
import os
from dotenv import load_dotenv


class VivoscraperPipeline:
    def process_item(self, item, spider):

        # load the .env file for token and base
        load_dotenv()

        PERSONAL_ACCESS_TOKEN = os.getenv('PERSONAL_ACCESS_TOKEN')
        BASE_ID = os.getenv('BASE_ID')
        TABLE_NAME = 'product-data'

        product_exists = False

        my_table = Table(api_key=PERSONAL_ACCESS_TOKEN, base_id=BASE_ID, table_name=TABLE_NAME)

        # retrieve products from the airtable
        records = my_table.all()
                
        # check and update records
        for record in records:
            if all(item[key] == record['fields'][key] for key in ['product_name', 'product_url']):
                if all(item[key] == record['fields'][key] for key in ['product_price', 'product_description', 'product_price']):
                    print('Product Already Exist')
                else:
                    my_table.update(record['id'], dict(item))
                    print('Product updated')
                product_exists = True

        # add new product
        if not product_exists:
            my_table.create(dict(item))
            print('New product added')

        return item
