import json
import os

from scrapy import Request, Spider
from scrapy.http import FormRequest

from ..items import ProductItem

# TODO: Uncomment for Local Development, o/w keep commented
# from dotenv import load_dotenv
# load_dotenv()
# SITE_URL = os.getenv("SITE_URL")
# SITE_USER = os.getenv("SITE_USER")
# SITE_PASS = os.getenv("SITE_PASS")

# TODO: Uncomment for Production, o/w keep commented
SITE_URL = os.environ.get("SITE_URL")
SITE_USER = os.environ.get("SITE_USER")
SITE_PASS = os.environ.get("SITE_PASS")

SITE_LOGIN_URL = f"{SITE_URL}/login"
SITE_THRESHOLD_API = f"{SITE_URL}/api/thresholds"
SITE_PRODUCT_API = f"{SITE_URL}/api/recommended/campaigns"
SITE_PRODUCT_URL = f"{SITE_URL}/product-tests"


class MainSpider(Spider):

    """Spider to scrape for product testing details."""

    name = "main_scraper"

    def __init__(self):
        """
        Initialize attributes.

        Attributes
        ----------
            lc (str): A string containing lowercase alphabetic characters 'abcdefghijklmnopqrstuvwxyz' for xpath translate
            uc (str): A string containing uppercase alphabetic characters 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' for xpath translate
            base_url (str): The base URL for product testing website.
        """
        self.lc = "abcdefghijklmnopqrstuvwxyz"
        self.uc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def start_requests(self):
        """
        Generate initial requests for scraping product testing information.

        This method prepares and yields a series of Scrapy requests to fetch data from product testing website.

        Returns
        -------
            generator: Yields login request
        """
        yield Request(
            url=SITE_LOGIN_URL,
            callback=self.login,
        )

    def login(self, response):
        """
        Login to product testing website.

        Args:
        ----
            response (http.Response): The response object containing the webpage content.

        Returns:
        -------
            generator: Yields form filling
        """
        yield FormRequest.from_response(
            response,
            formdata={"email": SITE_USER, "password": SITE_PASS},
            callback=self.request_threshold,
        )

    def request_threshold(self, response):
        """
        Request threshold from threshold url.

        Args:
        ----
            response (http.Response): The response object containing the webpage content.

        Returns:
        -------
            generator: Yields threshold request
        """
        yield Request(url=SITE_THRESHOLD_API, callback=self.parse_threshold)

    def parse_threshold(self, response):
        """
        Parse threshold from threshold url.

        Args:
        ----
            response (http.Response): The response object containing the webpage content.

        Returns:
        -------
            generator: Yields product api request
        """
        threshold_json = json.loads(response.text)
        is_threshold_met = threshold_json["product_tests"]["done"] == threshold_json["product_tests"]["threshold"]
        yield Request(
            url=SITE_PRODUCT_API, callback=self.parse_product_api, meta={"is_threshold_met": is_threshold_met}
        )

    def parse_product_api(self, response):
        """
        Parse products from product api.

        Args:
        ----
            response (http.Response): The response object containing the webpage content.

        Returns:
        -------
            generator: Yields product url
        """
        product_json = json.loads(response.text)
        product_api_list = []
        for product in product_json["data"]:
            if product["claim_url"][-1] != "#":
                product_price = product["price"]
                product_name = product["product_test"]["three_words"]
                product_link = f"{SITE_URL}{product['claim_url']}"
                product_api_list.append((product_name, product_price, product_link))
        yield Request(
            url=SITE_PRODUCT_URL,
            callback=self.parse_product_page,
            meta={"is_threshold_met": response.meta["is_threshold_met"], "product_api_list": product_api_list},
        )

    def parse_product_page(self, response):
        """
        Parse product information from product page url and create product item.

        Args:
        ----
            response (scrapy.http.Response): The response object containing the webpage content.

        Returns:
        -------
            generator: Yields product items with the extracted information.
        """
        xpath_job_str = '//text()[contains(translate(., "{self.uc}", "{self.lc}"), "see job detail") or contains(translate(., "{self.uc}", "{self.lc}"), "see product detail")]'

        job_list = response.xpath(xpath_job_str).getall()
        is_product_on_page = False
        if job_list:
            is_product_on_page = True

        product_item = ProductItem()
        product_item["is_product_on_page"] = is_product_on_page
        product_item["is_threshold_met"] = response.meta["is_threshold_met"]
        product_item["product_api_list"] = response.meta["product_api_list"]
        yield product_item
