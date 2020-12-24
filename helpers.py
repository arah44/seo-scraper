import requests
from bs4 import BeautifulSoup
import re
import tldextract as tld
import csv
import xmltodict
import pandas as pd

from settings import *


'''
TODO
- create decorator class to time a function - decorators.py
- Need to abstract out some functions so that they can take more flexible paramaters
- Add error handling

'''

def generate_data(name, url):
    '''
    Given a url, a json object is stored
    '''

    print("Starting page crawl...")
    data = get_all_pages(url)

    save_as_file(data)
    
    print("File complete.")

    return data

def save_as_file(data, name=NAME):

    # Create file name template
    file_name = name + "_data.csv"

    keys = ['url'] + list(data[list(data.keys())[0]].keys())

    df = pd.DataFrame.from_dict(data, orient='index')


    # df = df.rename(columns={df.iloc[:,0].name: 'URL'})

    df.to_csv(file_name, index=False)

def get_corpus(data):

    corpus = dict()

    # Generate corpus of links (do this from local memory, no need to crawl)
    for url in data:
        corpus[url] = data[url]['links_out']

    return corpus

def on_page_data(page):
    """
    Crawl a web page and return on page data 

    Ignores pages set to no-index and no-follow links

    - check only in body

    - block resource folders (.*/wp-.*)
    - Check for robots.txt file
    - - Check for redirect chain if r.history > 0
    """

    # Crawl page
    req = requests.get(page)

    # If status is 200
    if req.status_code == 200:
        soup = BeautifulSoup(req.text, "html.parser")
    else:
        return None

    # Get index status
    index = soup.find("meta", {"name":"robots"})
    if index == "no-index":
        return None

    # Get meta data
    title = soup.find("title")
    description = soup.find("meta", {"name":"description"})
    canonical = soup.find("link", {"rel":"canonical"})
    og_title = soup.find("meta",  {"property":"og:title"})
    og_description = soup.find("meta", {"property":"og:description"})


    # Find interal links only 
    num_links = 0 # total
    links = []
    num_links_out = 0 # number of links to interal pages
    external_links = []
    num_ext_out = 0 # number of links to external pages
    for link in soup.find_all('a'):
        num_links += 1
        destination = link.get('href')
        rel = link.get('rel')
        own_domain = tld.extract(page).domain

        # Handle none type
        if not destination:
            continue

        # Strip anchors and url parameters
        destination = destination.split("#")[0]
        destination = destination.split('?')[0]

        # If relative path match
        if re.match('/.*', destination):
            sub_domain = tld.extract(page).subdomain
            if sub_domain:
                destination = 'https://' + sub_domain + own_domain + '.' + tld.extract(page).suffix + destination
            else:
                destination = 'https://' + own_domain + '.' + tld.extract(page).suffix + destination

        # If external link
        if tld.extract(destination).domain != own_domain:
            num_ext_out += 1
            external_links.append(destination)
            continue

        if re.match("mailto:.*", destination) or re.match("tel:.*", destination):
            continue

        # If no-follow link
        if rel == 'no-follow':
            continue

        num_links_out += 1
        links.append(destination)

    # Get image data
    images = []
    num_images = 0
    missing_alt = 0
    for img in soup.find_all("img"):
        image_url = img.get("src")
        image_alt = img.get("alt")

        images.append(image_url)
        num_images += 1
        if not image_alt:
            missing_alt += 1

    # Get Schema data
    schema = soup.find("script", {"type": "application/ld+json"})
    schema = schema.text if schema else None

    # Get page headings
    h1 = []
    h2 = []
    h3 = []
    h4 = []
    h5 = []
    h6 = []
    for h_1 in soup.find_all("h1"):
        h1.append(h_1.text)
    for h_2 in soup.find_all("h2"):
        h2.append(h_2.text)
    for h_3 in soup.find_all("h3"):
        h3.append(h_3.text)
    for h_4 in soup.find_all("h4"):
        h4.append(h_4.text)
    for h_5 in soup.find_all("h5"):
        h5.append(h_5.text)
    for h_6 in soup.find_all("h6"):
        h6.append(h_6.text)

    # Build info about single page
    page_data = {
        "url": page,
        "links_out": links,
        "ext_links_out": external_links,
        "meta_title": str(title.text) if title else None,
        "meta_description": str(description["content"]) if description else None,
        "meta_canonical": str(canonical["href"]) if canonical else None,
        "meta_og_title": str(og_title["content"]) if og_title else None,
        "meta_og_desc": str(og_description["content"]) if og_description else None,
        "images": images,
        "missing_alt": missing_alt,
        'num_images': num_images,
        "schema": schema,
        "h1": h1 if h1 else None,
        "h1_count": len(h1),
        "h2": h2 if h2 else None,
        "h2_count": len(h2),
        "h3": h3 if h3 else None,
        "h3_count": len(h3),
        "h4": h4 if h4 else None,
        "h4_count": len(h4),
        "h5": h5 if h5 else None,
        "h5_count": len(h5),
        "h6": h6 if h6 else None,
        "h6_count": len(h6)
    }

    return page_data

def find_keys(d, key):
    '''
    Takes a dictonary and returns all nested values matching a key
    '''
    if isinstance(d, list):
        for i in d:
            for x in find_keys(i, key):
               yield x
    elif isinstance(d, dict):
        if key in d:
            yield d[key]
        for j in d.values():
            for x in find_keys(j, key):
                yield x

def links_from_sitemap(sitemap, links=None):
    '''
    Returns a set of all pages in a sitemap
    '''   
    # Get XML and save to dict
    resp = requests.get(sitemap)
    sitemap_dict = xmltodict.parse(resp.content)

    if not links:
        links = set()

    # Find all 'loc' keys in sitemap
    found = set(find_keys(sitemap_dict, 'loc'))

    # If another sitemap else add to links
    for url in found:
        if re.match(".*.xml", url):
            links = links.union(links_from_sitemap(url))
        else:
            links.add(url)
    return links

def get_all_pages(url, sitemap=sitemap):
    '''
    Takes a list of links and returns a set of pages 

    return dict of pages as keys and meta info as dict of values
    '''

    pages = set()

    # If sitemap start with these links
    if sitemap:
        crawl = links_from_sitemap(sitemap)
    else:
        crawl = set([url])

    data = dict()
    while crawl:
        
        # Get a new page to crawl
        page = crawl.pop()

        # Record page as page
        pages.add(page)

        # Get all internal links on page
        page_info = on_page_data(page)

        if not page_info:
            continue

        # Add page info to data
        data[page] = page_info
        page_links = page_info['links_out']

        # Create a set of links on page
        page_links = set(page_links)

        # Get pages that are not already in crawl or pages
        new_pages = page_links.difference(crawl, pages)

        # Add new pages to crawl
        crawl = crawl.union(new_pages)

    return data

def update_internal_links(data):
    '''
    Updates internal links to show inbound links
    '''
    
    # Check for other pages linking
    for page_1 in data:
        linked_from = []
        for page_2 in data:
            if page_1 == page_2:
                continue
            if page_1 in data[page_2]['links_out']:
                 linked_from.append(page_2)
        
        # Update internal links
        data[page_1]['links_in'] = linked_from if linked_from else None
        data[page_1]['links_in'] = len(linked_from)

    return data

def check_redirect_chains(data):
    '''
    Takes a dictonary and updates a count for how many redirects are on each page. Creates a csv s

    ..Opt..
    - clean url of parameters before checking and adding to set
    - Take a page url and a list of links instead
    '''

    # Don't check pages that are keys of data
    checked = set(data.keys())

    has_redirects = set()
    redirect_chains = set()

    # Check all known links
    for page in data:
        count = 0

        for url in data[page]['links_out']:
            try:
                # If redirect already found
                if url in has_redirects:
                    count += 1
                    continue
                elif url in checked:
                    continue

                r = requests.get(url)

                if len(r.history) > 0:
                    # Count a redirect
                    count += 1
                    chain = []

                    final_url = r.url
                    for resp in r.history:
                        chain.append(resp.url)

                        # Add urls already in a chain to checked
                        checked.add(resp.url)

                        if resp.url != final_url:
                            has_redirects.append(resp.url)

                    redirect_chains.add(chain)

            except requests.ConnectionError:
                print("Error: failed to connect.")
        
        # Save number of links
        data[page]["redirect_links"] = count

    # Save redirect chains to csv file
    with open(NAME + "_chains.csv", 'w') as f:
        writer = csv.writer(f)
        writer.writerow(redirect_chains)

    return data

    # Update links that are source
    for page in data:
        links = data[page]

if __name__ == '__main__':
    generate_data(NAME, URL)