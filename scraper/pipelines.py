import os

import scrapy
from dotenv import load_dotenv
from itemadapter import ItemAdapter
from scrapy import Request
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Content, Email, Mail, To

load_dotenv()

# TODO: Uncomment for Local Development, o/w keep commented
SITE_PRODUCT_URL = os.getenv("SITE_PRODUCT_URL")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
SENDGRID_TO_EMAIL = os.getenv("SENDGRID_TO_EMAIL")


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
        product_email_content = ["{SITE_PRODUCT_URL}\n\n"]
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
        product_api_content = adapter.get("product_content")

        # set up emails
        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
        from_email = Email(SENDGRID_FROM_EMAIL)
        to_email = To(SENDGRID_TO_EMAIL)
        subject = "Product Tests Available!"

        # send email
        if product_api_list or is_product_on_page:
            content = Content("text/plain", product_api_content)
            mail = Mail(from_email, to_email, subject, content)
            mail_json = mail.get()
            sg.client.mail.send.post(request_body=mail_json)
            yield Request(url=product_api_list[0][2])
        return None

    # ADD BELOW TO THE Pipelines for after getting necessary data Item
    # def send_email(self, response):
    #          # set sendgrid variables
    #     sg = sendgrid.SendGridAPIClient(api_key=email_api_key)
    #     from_email = Email("digestiblecontents@gmail.com")
    #     to_email = To("issactranloo@gmail.com")
    #     subject = "Products Available!"
    #     if email_product_list:
    #         email_product_list = sorted(email_product_list, key=lambda tup: tup[1], reverse=True)
    #         email_product_content = [f"Name: {p_info[0]}\n Price: {p_info[1]}\n Link:{p_info[2]}" for p_info in email_product_list]
    #         email_product_content = f"{SITE_PRODUCT_URL}\n\n" + '\n\n'.join(email_product_content)

    #         # send email
    #         content = Content("text/plain", email_product_content)
    #         mail = Mail(from_email, to_email, subject, content)
    #         mail_json = mail.get()
    #         response = sg.client.mail.send.post(request_body=mail_json)

    #         # click on the first product link
    #         first_product_response = sess.get(email_product_list[0][2])
    #            else:
    #                 product_main_response = sess.get(product_main_url)
    #                 product_main_soup = BeautifulSoup(product_main_response.text, "html.parser")
    #                 see_job = product_main_soup.find(text="See Job Details")
    #                 see_product = product_main_soup.find(text="See Product Details")
    #                 if see_job or see_product:
    #                      # send email
    #                      email_product_content = f"{product_main_url}\n\n There is a potential Job!"
    #                      content = Content("text/plain", email_product_content)
    #                      mail = Mail(from_email, to_email, subject, content)
    #                      mail_json = mail.get()
    #                      response = sg.client.mail.send.post(request_body=mail_json)
    #                 else:
    #                      print("No products currently available.")
    #       else:
    #            print("Reached max product testing threshold, no products will show.")
