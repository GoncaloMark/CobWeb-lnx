"""
@file crawler.py
@author Gonçalo Marques (_lnx)
This script defines the Spider and Scraper classes for web scraping.
The Spider class is used to crawl a website and identify internal and external links.
The Scraper class extends the functionality of the Spider class by scraping HTML content from web pages based on user-defined parameters.
"""

from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import yaml
from os import path
import itertools
import asyncio
import aiohttp
import timeit


## This class defines a web crawler that can identify internal and external links on a given website.

class Spider:
    """
    Constructor method for the Spider class.
    @param url The URL of the website to be crawled.
    @param max_hops The maximum number of links to follow from the initial URL.
    @throws ValueError if the provided URL is invalid.
    """
    def __init__(self, url, max_hops = 0):

        ## The maximum number of links to follow from the initial URL.
        self.hops = int(max_hops)

        ## The URL of the website to be crawled.
        self._url = url
        
        ## A set of internal URLs found during crawling.
        self._internal_urls = set()

        ## A set of external URLs found during crawling.
        self._external_urls = set()

        isValid = self.__validateURL(self._url)
        if isValid is False:
            raise ValueError

        """Validates that the provided URL is in a valid format.
        @param url The URL to be validated.
        @returns True if the URL is valid, False otherwise.
        """
    def __validateURL(self, url):
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    ## Crawls the website and identifies internal and external links.
    async def _getLinks(self, session = aiohttp.ClientSession):
        page = await session.request("GET", self._url)
        page.raise_for_status()
        domain_name = urlparse(self._url).netloc
        html = await page.text()
        soup = BeautifulSoup(html, "lxml")
        #TODO: throw netwrok errors like 403 forbidden

        # Loop over all <a> tags and get their href attributes.
        for link_tag in soup.find_all("a")[0:self.hops]:
            href = link_tag.attrs.get("href") 

            # If there is no href, continue to the next link.
            if href == "" or href == None:
                continue

            # Join the href with the base URL in case of relative paths.
            href = urljoin(self._url, href)

            # Get the parts of the URL.
            parse_href = urlparse(href)

            # Reconstruct the URL with the scheme, netloc, and path.
            href = parse_href.scheme + "://" + parse_href.netloc + parse_href.path

            # If the URL is invalid, continue to the next link.
            if not self.__validateURL(href):
                continue

            # If the domain name is not in the URL, it is external. Otherwise, it is internal.
            if domain_name not in href:
                if href not in self._external_urls:
                    self._external_urls.add(href)
                continue
            elif href not in self._internal_urls:
                self._internal_urls.add(href)
                continue

    """Returns the set of internal and external URLs found during crawling.
    @returns A tuple containing the set of internal URLs and the set of external URLs, or just the set of internal URLs or external URLs if one of them is empty.
    """
    def _showLinks(self):
        if self._internal_urls and self._external_urls:
            return (self._internal_urls, self._external_urls)
        elif self._internal_urls:
            return self._internal_urls
        elif self._external_urls:
            return self._external_urls
        
    """Crawls the requested website with the specifiend number of hops"""
    async def __crawl(self):
        async with aiohttp.ClientSession() as session:
            if self.hops != 0:
                await self._getLinks(session)
    
    """Runs the event loop and returns the urls found in the page!"""
    def run(self):
        asyncio.run(self.__crawl())
        return self._showLinks()


    def __str__(self):
        """
        Returns a string representation of the Spider object.

        Returns:
            str: A string containing the URL and hops of the Spider object.

        """
        return f"Spider Object with URL: {self._url} and Hops: {self.hops}"
    
    def __repr__(self):
        """
        Returns a string representation of the Spider object.

        Returns:
            str: A string containing the URL and hops of the Spider object.

        """
        return f"Spider(url={self._url}, max_hops={self.hops})"
        

class Scraper(Spider):

    def __init__(self, config):
        """
        A class to represent a web scraper.

        Parameters:
            config (dict): A dictionary containing the configuration parameters for the scraper.

        """

        if config.get("hops") is None:
            config["hops"] = 0

        super().__init__(config["url"], config["hops"])

        self.__config = config
        self.__Ilinks = []
        self.__cache = {}

    async def __get_html(self, link, session = aiohttp.ClientSession):
        """
        A private method to download and parse the HTML from the URLs in the Spider object.

        Returns:
            BeautifulSoup: A BeautifulSoup object containing the parsed HTML.

        """
        if link not in self.__cache:
            page = await session.request("GET", link)
            page.raise_for_status()
            html = await page.text()
            soup = BeautifulSoup(html, "lxml")
            self.__cache[link] = soup
            return self.__cache[link]
            
    async def __parse(self, link, session = aiohttp.ClientSession):
        html = await self.__get_html(link, session)
        scrape_list = [[x for x in self.__scrapeByElem(html)], [x for x in self.__scrapeByAttr(html)], [x for x in self.__scrapeByClassName(html)], [x for x in self.__scrapeBySelector(html)]]
        return (link, {
            "By_Element": scrape_list[0],
            "By_Attribute": scrape_list[1],
            "By_Class": scrape_list[2],
            "By_Selector": scrape_list[3]
        })

    def __scrapeByElem(self, html):
        """
        A private method to scrape elements from the HTML using element tags.

        Returns:
            List[Tag]: A list of Tag objects containing the scraped elements.

        """
        if self.__config.get("tags") is None or len(self.__config["tags"]) == 0:
            return
        
        for tag in self.__config["tags"]:
            result = html.find_all(tag)

            for el in result:
                yield el

    def __scrapeBySelector(self, html):
        """
        A private method to scrape elements from the HTML using CSS selectors.

        Returns:
            List[Tag]: A list of Tag objects containing the scraped elements.

        """
        if self.__config.get("selectors") is None or len(self.__config["selectors"]) == 0:
            return
        result = []
        for selector in self.__config["selectors"]:
            if selector == "id":
                for value in self.__config["IDvalue"]:
                    result.append(html.select_one("#"+value))
            result.append(html.select(selector))
            for el in result:
                yield el

    def __scrapeByClassName(self, html):
        """
        A private method to scrape elements from the HTML using class names.

        Returns:
            List[Tag]: A list of Tag objects containing the scraped elements.

        """
        if self.__config.get("classes") is None or len(self.__config["classes"]) == 0:
            return
        
        for tag, clsName in itertools.product(self.__config["tags"], self.__config["classes"]):
            result = html.find_all(tag, class_=str(clsName))

            for el in result:
                yield el

    def __scrapeByAttr(self, html):
        """
        A private method to scrape elements from the HTML using attributes.

        Returns:
            List[Tag]: A list of Tag objects containing the scraped elements.

        """
        if self.__config.get("attrs") is None or len(self.__config["attrs"]) == 0:
            return

        for tag, attrName, value in itertools.product(self.__config["tags"], self.__config["attrs"], self.__config["attrV"]):
            result = html.find_all(tag, attrs={attrName:value})

            for el in result:
                yield el

    async def __scrape(self):
        """
        A public method to return all the scraped content and prints it.

        Returns:
            Dict with arrays of scraped content

        """
        async with aiohttp.ClientSession() as session:
            if self.__config["hops"] != 0:
                await self._getLinks(session)
                links = self._showLinks()
                if type(links) == tuple:
                    internal, external = links
                    self.__Ilinks = [self.__config["url"], *internal, *external]
                else:
                    self.__Ilinks = [self.__config["url"], *links]
            else:
                self.__Ilinks = [self.__config["url"]]
            tasks = []
            for link in self.__Ilinks:
                tasks.append(
                    self.__parse(link, session=session)
                )
            result = [await asyncio.gather(*tasks)]
            return result
            
        
    def run(self):
        result = asyncio.run(self.__scrape())
        return result


    def __str__(self):
        """
        Returns a string representation of the Scraper object.

        Returns:
            str: A string containing the URL, hops and config of the Scraper object.

        """
        return f"Scraper Object with URL: {self._url} and Hops: {self.hops} and Config:{self.__config}"
    
    def __repr__(self):
        """
        Returns a string representation of the Scraper object.

        Returns:
            str: A string containing the URL, hops and config of the Scraper object.

        """
        return f"Scraper(url={self._url}, max_hops={self.hops}, config={self.__config})"
    
def config_parser(config_file):
        try:
            with open(config_file, 'r') as stream:
                data = yaml.safe_load(stream)
                stream.close()
                return data
        except yaml.YAMLError as e:
            raise e

if __name__ == "__main__":
    
    #SCRAPER TEST WITH FILE! 
    """ print("Specify config file (YAML) Path!")
    config_path = input()
    if path.exists(config_path) != True:
        raise ValueError """
    
    #SCRAPER TEST WITH CONFIG OBJECT! 
    """ config = {
            "url": "http://quotes.toscrape.com/",
            "tags": ["small", "h3"],
            "hops": 1000
        }  """

    #config = config_parser(config_file=config_path)
    #scrape = Scraper(config=config)
    #scrape._getLinks()
    #print(scrape._showLinks())
    #result = scrape.run()
    #print(result)
    #time = timeit.timeit(scrape.run, number=1)
    #print(time)
    
    # SPIDER TEST!
    spider = Spider("https://example.com", max_hops=10)
    # Get the internal and external links
    links = spider.run()
    print(links)