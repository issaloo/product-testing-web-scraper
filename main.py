from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraper.spiders.main_spider import MainSpider


def product_testing_web_scraper(event, context):
    """Cloud Function entry point function."""
    settings = get_project_settings()
    settings.setdict(
        {
            "LOG_LEVEL": "ERROR",
            "LOG_ENABLED": True,
        }
    )

    process = CrawlerProcess(settings)
    process.crawl(MainSpider)
    process.start()

    return "Run Successful!"


# TODO: Uncomment for Local Development, o/w keep commented
# if __name__ == "__main__":
#     product_testing_web_scraper(event=None, context=None)
