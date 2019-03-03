import json

import scrapy

AJAX_URL = "https://www.orleansexpress.com/wp-admin/admin-ajax.php?lang=en"
HOME_URL = "https://www.orleansexpress.com/en/select-the-outbound-trip/"


class OrleansSpider(scrapy.Spider):
    name = "orleans"

    def start_requests(self):
        outbound_date = "2019/03/09"
        form_data = {
            "action": "action_get_complete_schedules",
            "o": "QUE",
            "d": "MTL",
            "carriers": "oexp",
            "outboundDate": outbound_date,
            "returnDate": "",
        }

        yield scrapy.http.FormRequest(url=AJAX_URL, formdata=form_data)

    def parse(self, response):
        data = json.loads(response.text)
        yield data
