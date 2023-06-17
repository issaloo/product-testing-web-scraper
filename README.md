# Product Testing Web Scraper

## Background

A product testing website has limited product testing spots. As soon as a product test is available, spots are taken up within the next 5 to 10 minutes. After securing the spot, there are some quick additional steps that are needed to get the product (i.e., confirming that the product should be shipped to a certain address).

## Project Overview

This Web Scraper was built to secure a product testing spot and send me personal email alerts. It checks the website at 15 minute intervals and accounts for cases where there are multiple product tests - securing the most expensive products due to a daily product testing limit.

## Technologies
- Cloud Function
    - Execute code using serverless compute
- Cloud Scheduler
    - Schedule execution of code
- SendGrid
    - Email delivery service