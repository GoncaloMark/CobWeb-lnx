# CobWeb

CobWeb is a Python library for web scraping. The library consists of two classes: Spider and Scraper.

## Spider

The Spider class is used to crawl a website and identify internal and external links. It has the following methods:

    __init__(self, url, max_hops = 0): Initializes a Spider object with the given URL and maximum number of links to follow from the initial URL.
    getLinks(self): Crawls the website and identifies internal and external links.
    showLinks(self): Returns the set of internal and external URLs found during crawling.
    __str__(self): Returns a string representation of the Spider object.
    __repr__(self): Returns a string representation of the Spider object.

## Scraper

The Scraper class extends the functionality of the Spider class by scraping HTML content from web pages based on user-defined parameters. It has the following methods:

    __init__(self, config): Initializes a Scraper object with the given configuration parameters.
    run(self): A public method to scrape HTML content from web pages based on user-defined parameters.
    __str__(self): Returns a string representation of the Scraper object.
    __repr__(self): Returns a string representation of the Scraper object.

## Installation

You can install CobWeb using pip:

```bash

        pip install CobWeb

```

## Config

Config is either an object in memory or a YAML file you can build by installing YAMLbuilder or by using the provided template!
Example of a complete object:

 ```python 

        config = {
                    "url": 
                    "hops": 
                    "tags":
                    "classes":
                    "attrs":
                    "attrV":
                    "IDv":
                    "selectors":
                }
```

Example of YAML file (If you choose this path call the config_parser function and give it a valid path!):

```yaml
        IDv:
        attrV: []
        attrs: []
        classes: []
        hops: 
        selectors: []
        tags:
        - 
        - 
        url: 
```

## Example Usage

```python

        from CobWeb import Spider, Scraper

        # Create a Spider object with a URL and maximum number of hops
        spider = Spider("https://example.com", max_hops=10)

        # Get the internal and external links
        internal_links, external_links = spider.showLinks()

        # Create a Scraper object with a configuration dictionary
        # hops defines how deep it will scrape, it uses the Spider internally to get more links and scrape from those pages! If you just want to scrape from a single page set it to 0 or don't provide hops
        config = {
            "url": "https://example.com",
            "hops": 2,
            "tags": ["h1", "p"]
        }
        scraper = Scraper(config)

        # Scrape HTML content from web pages based on user-defined parameters
        results = scraper.run()

        # Print the results it shall be a dictionary with arrays of scraped content separated by element, attributes, etc provided in the config!
        print(results)


```
