import scrapy
import json
from daraz.items import DarazItem

class DarazApiSpider(scrapy.Spider):
    name = "daraz_api"
    allowed_domains = ["daraz.pk"]
    
    # configure your search
    search_query = "electronics"
    max_pages = 5  # number of pages to fetch
    
    custom_settings = {
        # gentle crawling, avoid ban
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "FEED_EXPORT_ENCODING": "utf-8"
    }

    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/117.0.0.0 Safari/537.36",
            "Accept": "application/json, text/javascript, /; q=0.01"
        }
        for page in range(1, self.max_pages + 1):
            url = (
               "https://www.daraz.pk/catalog/?ajax=true&isFirstRequest=true&page=1&q=electronics"
            )
            yield scrapy.Request(url, headers=headers, callback=self.parse_listing, dont_filter=True)

    def parse_listing(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON on %s", response.url)
            return

        # Uncomment to debug the JSON and inspect structure
        # import pprint; pprint.pp(data)
        # return

        items = data.get("mods", {}).get("listItems", [])
        if not items:
            # maybe data structure changed — log and stop
            self.logger.warning("No listItems found on %s", response.url)
            return

        for obj in items:
            item = DarazItem()
            # Example based on common fields; adjust after inspecting JSON
            item['title'] = obj.get("name") or obj.get("title")
            item['price'] = obj.get("price_show") or obj.get("price") or obj.get("price_raw")
            url_part = obj.get("productUrl")
            if url_part:
                # ensure full absolute URL
                item['url'] = url_part if url_part.startswith("http") else "https:" + url_part
            item['item_id'] = obj.get("nid") or obj.get("itemId") or obj.get("id")
            yield item