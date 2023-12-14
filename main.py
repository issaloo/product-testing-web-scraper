from multiprocessing import Process, Queue

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraper.spiders.main_spider import MainSpider


def product_testing_web_scraper(event, context):
    """Cloud Function entry point function."""

    def script(queue):
        try:
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
            queue.put(None)
        except Exception as e:
            queue.put(e)

    queue = Queue()

    # Wrap the spider in a child process
    main_process = Process(target=script, args=(queue,))
    main_process.start()
    main_process.join()

    result = queue.get()
    if result is not None:
        raise result
    # TODO: update here, update for whether products are available
    comment = "Did not find products to test at this time."
    return f"Run Successful! {comment}"
