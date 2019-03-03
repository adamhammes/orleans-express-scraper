import datetime
import json

import scrapy

AJAX_URL = "https://www.orleansexpress.com/wp-admin/admin-ajax.php?lang=en"
NUM_DAYS_TO_SCRAPE = 120


def format_date(date):
    return datetime.datetime.strftime(date, "%Y-%m-%d")


class OrleansSpider(scrapy.Spider):
    name = "orleans"

    def start_requests(self):
        today = datetime.datetime.now()

        for num_days_in_future in range(0, NUM_DAYS_TO_SCRAPE, 3):
            # The API gives results in 3 day windows centered around the
            # requested date.
            date = today + datetime.timedelta(days=num_days_in_future + 1)

            form_data = {
                "action": "action_get_complete_schedules",
                "o": "QUE",
                "d": "MTL",
                "carriers": "oexp",
                "outboundDate": format_date(date),
                "returnDate": "",
            }

            yield scrapy.http.FormRequest(url=AJAX_URL, formdata=form_data)

    def parse(self, response):
        data = json.loads(response.text)
        yield data
