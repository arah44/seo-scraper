# Questions this app can answer
- what pages are missing meta info
- pages and/or images that missing image alt info
- number of links on a page
- number of links to a page
- what is the value of a page?

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
