import re
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup

def match(word, matchword):
    word = word[1:]
    #print("Word "+word)
    if len(word) > len(matchword):
        size = len(matchword)
    else:
        size = len(word)
    for i in range(0,size):
        if not word[i].lower() == matchword[i].lower():
            return False
    return True
# starting url. replace google with your own url.
starting_url = 'http://www.americantowns.com/'
# a queue of urls to be crawled
unprocessed_urls = deque([starting_url])
# set of already crawled urls for email
processed_urls = set()
# a set of fetched emails
emails = set()
urlparts = urlsplit(starting_url)
domain = urlparts.netloc
# process urls one by one from unprocessed_url queue until queue is empty
while len(unprocessed_urls):
    try:
        # move next url from the queue to the set of processed urls
        url = unprocessed_urls.popleft()
        pageEligibleForCrawl = False
        processed_urls.add(url)
        if ".pdf" in url or "#" in url or "@" in url or "?" in url or ".mp3" in url:
            continue
        # extract base url to resolve relative links
        parts = urlsplit(url)
        processingDomain = parts.netloc
        if not processingDomain == domain:
            continue
        base_url = "{0.scheme}://{0.netloc}".format(parts)
        path = url[:url.rfind('/')+1] if '/' in parts.path else url
        if not "/" == parts.path and not "" == parts.path:
            #matchwords = set(re.findall(r"/\b(about(us)?)\b/", url, re.RegexFlag.I))
            if parts.path and (match(parts.path,"about") or match(parts.path,"contact")):
                pageEligibleForCrawl = True
        else:
            pageEligibleForCrawl = True   
        
        if pageEligibleForCrawl:
            # get url's content
            print("Crawling URL %s" % url)
            try:
                response = requests.get(url)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                # ignore pages with errors and continue with next url
                continue
         
            # extract all email addresses and add them into the resulting set
            # You may edit the regular expression as per your requirement
            new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.RegexFlag.I))
            emails.update(new_emails)
            print(emails)
            # create a beutiful soup for the html document
            soup = BeautifulSoup(response.text, 'lxml')
         
            lists = soup.findAll(href=True)
            # Once this document is parsed and processed, now find and process all the anchors i.e. linked urls in this document
            for anchor in soup.find_all("a"):
                # extract link url from the anchor
                link = anchor.attrs["href"] if "href" in anchor.attrs else ''
                # resolve relative links (starting with /)
                if link.startswith('/'):
                    link = base_url + link
                elif not link.startswith('http'):
                    link = path + link
                # add the new url to the queue if it was not in unprocessed list nor in processed list yet
                if not link in unprocessed_urls and not link in processed_urls:
                    unprocessed_urls.append(link)
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
        print("Exception")
        continue