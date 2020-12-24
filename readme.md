# Questions this app can answer
- what pages are missing meta info
- pages and/or images that missing image alt info
- number of links on a page
- number of links to a page
- what is the value of a page?


# TODO
- Connect to search console api (pull external links, SERP metrics)
    -- how could we train a model on this information
- read json in jupyter notebook
    - How many pages are missing meta?
    - how many images are missing alt
    - how many internal links
        - pages with low num links on it
        - pages with low num links to it
        
- move pagerank to own library
- Create a more modular structure
    - Run pagerank on the json object
    - Have an app generate an object and then read it with other methods
    - collect a raw file and then generate the file for analysis from the raw file

## Optimisation
- Create decerator that counts requests
- Create decorator that times a function
- Save meta and all links to start
    - generate internal links from corpus of all links

## Data created
- average images per page
- correlate values with gse / analytics data (i.e. number of internal links, or number of images to value from search console and ga) (do this to replicate )

# CSV
data = {
    
    "page_url_1" : {
        meta_title: str,
        meta_description: str,
        meta_og_title: str,
        meta_og_description: str,
        links_in: [], 
        links_out: [],
        schema: str, 
        images: [],
        missing_alt: 0,
        missing_title: 0,
        redirect_links: 0,
        broken_links: 0

        <!-- add this -->
        canonical: str,
        robots_tag: str,
        x_robots : str,
        keywords: str,
        word_count: 0,
        language: str,
        total_links_out: int,
        internal_links_out: int

    }
}

# Notebook
- What metrics are needed?
-- Num links (in, internal_out, ext_out, total)
-- Number of images
-- 