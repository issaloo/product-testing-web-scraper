import os

import scrapy
from itemadapter import ItemAdapter
from scrapy import Request
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, To

# TODO: Uncomment for Local Development, o/w keep commented
# from dotenv import load_dotenv
# load_dotenv()
# SITE_URL = os.getenv("SITE_URL")
# SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
# SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
# SENDGRID_TO_EMAIL = os.getenv("SENDGRID_TO_EMAIL")

# TODO: Uncomment for Production, o/w keep commented
SITE_URL = os.environ.get("SITE_URL")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.environ.get("SENDGRID_FROM_EMAIL")
SENDGRID_TO_EMAIL = os.environ.get("SENDGRID_TO_EMAIL")

SITE_PRODUCT_URL = f"{SITE_URL}/product-tests"


class PrepareProductContentPipeline:

    """Prepare product content for email form."""

    def process_item(self, item: scrapy.Item, spider: scrapy.Spider):
        """
        Process an item to ensure the product content field is added.

        Args:
        ----
            item (scrapy.Item): The item to be processed.
            spider (scrapy.Spider): The spider that generated the item.

        Returns:
        -------
            scrapy.Item: The processed item if all required fields are present.
        """
        adapter = ItemAdapter(item)
        product_api_list = adapter.get("product_api_list")
        is_product_on_page = adapter.get("is_product_on_page")

        product_api_list = sorted(product_api_list, key=lambda tup: tup[1], reverse=True)
        adapter["product_api_list"] = product_api_list
        product_api_content = [
            f"Name: {p_info[0]}\n Price: {p_info[1]}\n Link:{p_info[2]}" for p_info in product_api_list
        ]
        product_email_content = [f"{SITE_PRODUCT_URL}"]
        if product_api_list:
            product_email_content.extend(product_api_content)
        if is_product_on_page:
            product_email_content.append("There is a potential Job, check the website!")
        adapter["product_email_content"] = "\n\n".join(product_email_content)
        return item


class SendEmailPipeline:

    """Send out emails."""

    def process_item(self, item: scrapy.Item, spider: scrapy.Spider):
        """
        Prepare and send out emails.

        Args:
        ----
            item (scrapy.Item): The item to be processed.
            spider (scrapy.Spider): The spider that generated the item.
        """
        adapter = ItemAdapter(item)
        product_api_list = adapter.get("product_api_list")
        is_product_on_page = adapter.get("is_product_on_page")
        product_email_content = adapter.get("product_email_content")

        # set up emails
        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
        from_email = Email(SENDGRID_FROM_EMAIL)
        to_email = To(SENDGRID_TO_EMAIL)
        subject = "Product Tests Available!"

        # send email
        if product_api_list or is_product_on_page:
            content = Content("text/plain", product_email_content)
            mail = Mail(from_email, to_email, subject, content)
            mail_json = mail.get()
            sg.client.mail.send.post(request_body=mail_json)
            Request(url=product_api_list[0][2])
            return "Product tests available!"
        else:
            return "No products tests."
