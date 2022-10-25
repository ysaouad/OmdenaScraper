import csv, requests
from scrapFunctions import scrape_website

url_list = ["https://patient.info/forums/discuss/browse/depression-683","https://patient.info/forums/discuss/browse/bipolar-affective-disorder-271",
            "https://patient.info/forums/discuss/browse/ptsd-post-traumatic-stress-disorder-1721","https://patient.info/forums/discuss/browse/mental-health-1515",
            "https://patient.info/forums/discuss/browse/eating-disorders-862","https://patient.info/forums/discuss/browse/anxiety-disorders-70"]
#url_list = ["https://patient.info/forums/discuss/browse/alzheimer-s-disease-67"]
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    #Switch the User-agent regularly
}

session_object = requests.Session()

post_dict, fieldnames = scrape_website(url_list, headers)

  
with open('Results2.csv', 'w', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames,lineterminator = '\n', delimiter = ";")
    writer.writeheader()
    writer.writerows(post_dict)