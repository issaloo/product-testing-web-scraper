from scrapy.item import Field, Item


class ProductItem(Item):

    """
    Data from product website.

    Attributes
    ----------
        is_product_on_page: Boolean on whether there is an available product on the product page
        is_threshold_met: Boolean on whether daily product testing threshold has been met
        product_api_list: List of products details from the product api
        product_email_content: String content prepared for email
    """

    is_product_on_page = Field()
    is_threshold_met = Field()
    product_api_list = Field()
    product_email_content = Field()
