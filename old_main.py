import os

import requests
import sendgrid
from bs4 import BeautifulSoup
from sendgrid.helpers.mail import Content, Email, Mail, To


def ppoc_scraper(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic.

    Args:
    ----
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    email = os.environ.get("email")
    password = os.environ.get("password")
    email_api_key = os.environ.get("email_api_key")

    # set header and urls
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
    }
    ppoc_url = "https://beta.ppoc.club"
    login_url = f"{ppoc_url}/login"
    threshold_url = f"{ppoc_url}/api/thresholds"
    product_api_url = f"{ppoc_url}/api/recommended/campaigns"
    product_main_url = f"{ppoc_url}/product-tests"

    # set sendgrid variables
    sg = sendgrid.SendGridAPIClient(api_key=email_api_key)
    from_email = Email("digestiblecontents@gmail.com")
    to_email = To("issactranloo@gmail.com")
    subject = "PPOC Products Available!"

    # scrape PPOC website
    with requests.Session() as sess:
        login_response = sess.get(login_url, headers=headers)

        login_response_soup = BeautifulSoup(login_response.text, "html.parser")
        login_token = login_response_soup.find("input", {"name": "_token"}).attrs["value"]
        payload = {
            "_token": login_token,
            "email": email,
            "password": password,
        }

        # login with token, email, and password
        sess.post(login_url, data=payload)

        # if threshold for product testings is met, don't continue to check for products
        threshold_json = sess.get(threshold_url).json()
        p_thresh = threshold_json["product_tests"]
        if p_thresh["done"] < p_thresh["threshold"]:
            product_json = sess.get(product_api_url).json()
            product_main_response = sess.get(product_main_url)
            product_main_soup = BeautifulSoup(product_main_response.text, "html.parser")

            # if there are no products, don't continue
            product_list = product_json["data"]
            if product_list:
                # loop through products, order by price, and set up email content
                email_product_list = []
                for product in product_list:
                    product_price = product["price"]
                    product_name = product["product_test"]["three_words"]
                    product_link = f"{ppoc_url}{product['claim_url']}"
                    email_product_list.append((product_name, product_price, product_link))
                email_product_list = sorted(email_product_list, key=lambda tup: tup[1], reverse=True)
                email_product_content = [
                    f"Name: {p_info[0]}\n Price: {p_info[1]}\n Link:{p_info[2]}" for p_info in email_product_list
                ]
                email_product_content = f"{product_main_url}\n\n" + "\n\n".join(email_product_content)

                # send email
                content = Content("text/plain", email_product_content)
                mail = Mail(from_email, to_email, subject, content)
                mail_json = mail.get()
                sg.client.mail.send.post(request_body=mail_json)

                # click on the first product link
                sess.get(email_product_list[0][2])
            else:
                product_main_response = sess.get(product_main_url)
                product_main_soup = BeautifulSoup(product_main_response.text, "html.parser")
                see_job = product_main_soup.find(text="See Job Details")
                see_product = product_main_soup.find(text="See Product Details")
                if see_job or see_product:
                    # send email
                    email_product_content = f"{product_main_url}\n\n There is a potential Job!"
                    content = Content("text/plain", email_product_content)
                    mail = Mail(from_email, to_email, subject, content)
                    mail_json = mail.get()
                    sg.client.mail.send.post(request_body=mail_json)
                else:
                    print("No products currently available.")
        else:
            print("Reached max product testing threshold, no products will show.")
