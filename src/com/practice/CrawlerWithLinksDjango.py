import re
import requests.exceptions
import csv
from urllib.parse import urlsplit
from collections import deque
from bs4 import BeautifulSoup
import xlsxwriter
from _socket import timeout
wb = xlsxwriter.Workbook('I:\Srinivas_Spring18\E-Survey\Result.xlsx')
ws = wb.add_worksheet()

def match(word, matchword):
    wordsArray = []
    wordsArray = word.split("/")
    word = wordsArray[len(wordsArray)-1]
    if not word:
        return False
    if len(word) > len(matchword):
        size = len(matchword)
    else:
        size = len(word)
    for i in range(0,size):
        if not word[i].lower() == matchword[i].lower():
            return False
    return True

# starting url. replace google with your own url.
#file = 'I:\Srinivas_Spring18\E-Survey\WebAddresses.csv'
file = 'I:\Srinivas_Spring18\E-Survey\Test.csv'
try:
    with open(file,encoding='utf-8-sig') as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            counter = 0
            for row in csvReader:
                if counter == 0:
                    ws.write(counter, 0, 'Company Name')
                    ws.write(counter, 1, 'Web Address')
                    counter += 1
                    continue
                ws.write(counter, 0, str(row[0]))
                ws.write(counter, 1, str(row[1]))
                starting_url = 'http://'+str(row[1])+'/'
                # a queue of urls to be crawled
                unprocessed_urls = deque([starting_url])
                # set of already crawled urls for email
                processed_urls = set()
                # a set of fetched emails
                emailset = set()
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
                        testpath = url[:url.rfind('/')] if '/' in parts.path else url
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
                                response = requests.get(url, timeout=5)
                                # extract all email addresses and add them into the resulting set
                                # You may edit the regular expression as per your requirement
                                new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.RegexFlag.I))
                                emailset.update(new_emails)
                                #print(emails)
                                # create a beutiful soup for the html document
                                soup = BeautifulSoup(response.text, 'lxml')
                             
                                lists = soup.findAll(href=True)
                                # Once this document is parsed and processed, now find and process all the anchors i.e. linked urls in this document
                                for anchor in soup.find_all("a"):
                                    # extract link url from the anchor
                                    link = anchor.attrs["href"] if "href" in anchor.attrs else ''
                                    link = link.replace(" ","")
                                    # resolve relative links (starting with /)
                                    if link.startswith('/'):
                                        link = base_url + link
                                    elif not link.startswith('http'):
                                        link = path + link
                                    # add the new url to the queue if it was not in unprocessed list nor in processed list yet
                                    if not link in unprocessed_urls and not link in processed_urls:
                                        unprocessed_urls.append(link)
                                    
                            except requests.exceptions.RequestException as e:
                                print(e)
                                #ws.write(counter, 2, "Timeout")
                                continue
                    except Exception as e:
                        print(e)
                        continue
                emailcounter = 0
                for email in emailset:
                    ws.write(counter, emailcounter+2, email)
                    emailcounter += 1
                if emailcounter == 0:
                    ws.write(counter, emailcounter+2, "N/A")
                counter += 1
except Exception as e:
    print(e)
wb.close()