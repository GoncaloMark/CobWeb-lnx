import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import pathlib
import yaml

class Spider:
    def __init__(self, url, config_file):
        #Spider initializes instance with an url and a config, the config for the spider will only tell if you want internal links, external links or both!

        self.__url = url
        self.__config = self.__config_parser(config_file=config_file)

        #These are instance sets because every link will be unique, internal links link to another inside page, external links link to another different website!
        self.internal_urls = set()
        self.external_urls = set()

        isValid = self.__validateURL()
        if isValid is False:
            raise ValueError

    def __del__(self):
        print(f"Invalid URL {self.__url}")


    def __validateURL(self):
        parsed = urlparse(self.__url)
        return bool(parsed.netloc) and bool(parsed.scheme)

    def getLinks(self):
        page = requests.get(self.__url)
        domain_name = urlparse(self.__url).netloc
        soup = BeautifulSoup(page.content, "html.parser")

        for link_tag in soup.find_all("a"): #Find all <a/> html tags and get their href attribute
            href = link_tag.attrs.get("href") 

            if href == "" or href == None: #If there's no href return control to the beginning 
                continue

            href = urljoin(self.__url, href) #Join in case of relative paths!

            parse_href = urlparse(href) #Get the parts of the URL

            href = parse_href.scheme + "://" + parse_href.netloc + parse_href.path #Even if it was an absolute path and we accidentally joined it above this ensures all we get is an URL of this type!

            if not self.__validateURL(href):
                continue #If it's invalid return control to the beginning 

            if domain_name not in href: #Here we check if it's external link first, if it's not we can check if it's already in internal links and add it!
                if href not in self.external_urls:
                    self.external_urls.add(href)
                continue
            elif href not in self.internal_urls:
                self.internal_urls.add(href)
                continue

    def showLinks(self):
        return (self.internal_urls, self.external_urls)

    def __config_parser(self, config_file):
        file_extension = pathlib.Path('config_file').suffix

        if file_extension == "yml" or file_extension == "yaml":
            config = self.__parse_yaml(config_file=config_file)
            return config
        else:
            raise ValueError

    def __parse_yaml(self, config_file):
        
        try:
            with open(config_file, 'r') as stream:
                data = yaml.safe_load(stream)
                return data
        except yaml.YAMLError as e:
            print(f"ERROR {e}")
            raise ValueError


