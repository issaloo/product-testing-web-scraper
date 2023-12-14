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

## Contributing

### General Guidelines

Please take a look at the following guides on writing code:

- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/) for Python

### Set Up Development Environment

1. Clone and navigate to the repository

```shell
cd ~/GitHub/issaloo
git clone git@github.com:issaloo/product-testing-web-scraper.git
cd product-testing-web-scraper
```

2. Install pdm globally

```shell
pip install pdm
```

3. Install general & development packages with pdm

```shell
pdm install --dev
```

> :information_source: This will install packages [pre-commit](https://pre-commit.com/), [commitizen](https://commitizen-tools.github.io/commitizen/), and [gitlint](https://jorisroovers.com/gitlint/latest/)

(Optional) Install only the general packages

```shell
pdm install
```

3. Activate the virtual environment

```shell
eval $(pdm venv activate)
```

> :information_source: Virtual environment will use the same python version as the system

(Optional) Deactivate the virtual environment

```shell
deactivate
```

### Running Locally

1. Set Up Environment Files

   1. Copy `.env.template` to environment file

      ```Shell
      cp .env.local.template .env
      ```

   2. Fill in configs for `.env`

2. Comment out production settings and uncomment development settings in the code

### Set Up Standardized Version Control

1. Automate scripts (i.e., linting and autoformatting)
   ```shell
   pre-commit install
   ```
2. Enforce template at commit with pre-commit
   ```shell
   gitlint install-hook
   ```

### Test It Out

1. **Check if `commitizen` is working**

   - :mag_right: Try using commitizen in command line
     1. Add files to staging
     2. Run commitizen
        ```shell
        git cz c
        ```
        Or, if possible
        ```shell
        cz c
        ```
   - :white_check_mark: You should get structured commits

2. **Check if `gitlint` is working**

   - :mag_right: Try writing a bad commit
     1. Add files to staging
     2. Write a bad commit (e.g., `git commit -m 'WIP: baD commit'`)
   - :white_check_mark: You should get a question on whether to continue the commit.

3. **Check if `pre-commit` is working**

   - :mag_right:
     1. Add files to staging, where at least one python file is not formatted well
     2. Run commitizen
        ```shell
        git cz c
        ```
        Or, if possible
        ```shell
        cz c
        ```
   - :white_check_mark: You should get automatic fixes to poorly formatted python files with some errors

   > :information_source: Ctrl+C to exit commit template
