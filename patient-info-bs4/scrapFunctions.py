import requests, lxml, re, logging
from tqdm import tqdm
from bs4 import BeautifulSoup
from lxml import etree
from re import T


def scrape_website(url_list, headers):
    session_object = requests.Session() 
    scraped_posts =[]
    for url in url_list:
        scraped_urls, topic = scrape_urls_by_topic(url, headers, session_object)
        scraped_posts_topic, fieldnames = scrape_topic(scraped_urls, topic, headers, session_object)
        scraped_posts.append(scraped_posts_topic)
    return scraped_posts, fieldnames

def scrape_urls_by_topic(url, headers, session_object):
    #Use a session to avoid making one request per page + 
    #          saving time & the server's ressources

    post_urls = []
    post_url = 0
    topic = None
    page_num = None
    response = session_object.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    dom = etree.HTML(str(soup))

    try:
        page_num = dom.xpath(f'/html/body/div[1]/div/div[2]/div[1]/div/div/div/div[1]/div/div[2]/form/select/option[1]/text()')[0]
        page_num = re.findall("1\/([1-9]*)", page_num)
        page_num = int(page_num[0])
        topic = dom.xpath(f"/html/body/div[1]/div/div[2]/header/div[2]/div/div/h1/text()")[0]
        topic = re.sub("\s","",topic)
    except: 
        if page_num is not None and topic is None:
            print("Couldn't find topic name")
        if page_num is None and topic is None:
            print("Couldn't find either final page number or topic name")
        if page_num is None and topic is not None:
            print("Couldn't find final page number for this topic :", topic)
    print("Crawling", url)
    for i in tqdm(range(page_num-1)): 
    
        #Do NOT crawl the entire forum unless necessary. 
        #The final results are on github. If you want to test the code, simply use a range(1,2)
    
        page_url = url + f"?page={i}#group-discussions"
        
        response = session_object.get(page_url, headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
    
        for j in range(1, 37):
            if j == 8:
                continue
            XPATH = f"/html/body/div[1]/div/div[2]/div[1]/div/div/div/div[1]/div/ul/li[{j}]/div/div[2]/article/h3/a/@href"
            
            dom = etree.HTML(str(soup))
            try:
                post_url = 'https://patient.info' + dom.xpath(XPATH)[0]
                post_urls.append(post_url)
            except:
                print("An exception was thrown for the topic, ", topic, "at page :",i, " previously searched url :", post_url, "and xpath :", dom.xpath(XPATH))
                continue
    
    page_url = url + f"?page={page_num}#group-discussions"
    response = session_object.get(page_url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    
    for j in range(1, 37):
            if j == 8:
                continue
            XPATH = f"/html/body/div[1]/div/div[2]/div[1]/div/div/div/div[1]/div/ul/li[{j}]/div/div[2]/article/h3/a/@href"
            
            dom = etree.HTML(str(soup))
            try:
                post_url = 'https://patient.info' + dom.xpath(XPATH)[0]
                post_urls.append(post_url)
            except:
                #print("An exception was thrown for the topic, ", topic, "at page",i, " with this url ", post_url, "and xpath", dom.xpath(XPATH))
                print("End of page") #Need a proper way to take factor in the end of a page before the 37 post limit
                break
            
    return post_urls, topic

def scrape_topic(post_urls, topic, headers, session_object):

    post_dict = []
    fieldnames = ["Topic","Date","Title","URL","Main_Post"]
    print("Scraping topics")
    for i in tqdm(range(len(post_urls))): 

        #Do NOT crawl the entire URL list unless necessary. 
        #The final results are on github. If you want to test the code, simply use a range(1,5)

        response = session_object.get(post_urls[i], headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
        webpage = etree.HTML(str(soup))

        try:
            text = webpage.xpath('.//*[@id="post_content"]/input')[0]
            text = text.attrib["value"]
            text = re.sub(r"\r", "", text)
            text = re.sub(r"\n", "", text)
            text = re.sub(r"<p>", "", text)
            text = re.sub(r"</p>", "", text)

        except: 
            print("Couldn't recover text at :", post_urls[i], ", skipping post.")
            continue

        try: 
            date = webpage.xpath('/html/body/div[1]/div/div[2]/div[1]/div/div/div/div[1]/article/p/span[1]/time')[0]
            date = date.attrib['datetime']
        except:
            print("Couldn't recover datetime at :", post_urls[i])
        
        try:
            title = webpage.xpath('/html/body/div/div/div[2]/div[1]/div/div/div/div[1]/article/div[1]/h1/text()')[0]      
        except:
            print("Couldn't recover title at :", post_urls[i])


        post_dict.append({"Topic" : topic, "Date" : date, "Title" : title, "URL": post_urls[i], "Main_Post": text})
    return post_dict, fieldnames

