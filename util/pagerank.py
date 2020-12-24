import helpers as hlp

DAMPING = 0.85
SAMPLES = 10000

def generate_page_rank(data):
    corpus = hlp.get_corpus(data)

    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    # # If page has links
    if len(corpus[page]) > 0:
        p = {'random': (1 - damping_factor) / len(corpus),
            'on_page': damping_factor / len(corpus[page])}

    # If page has no links
    if len(corpus[page]) == 0:
        p = {'random': 1 / len(corpus), 
            'on_page': 0}

    probability = {}

    # All pages have equal random chance
    for i in corpus.keys():
        probability[i] = p['random']

    # Add on page chance to those linked to
    for i in corpus[page]:
        probability[i] += p['on_page']

    return probability


def sample_pagerank(corpus, damping_factor, n):
    """ 
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # List all pages
    pages = list(corpus)

    # Generate random number 
    num = random.randrange(len(pages))

    # Return random page
    page = pages[num]

    # Counter for page occurance
    counter = {page : 0 for page in pages}    

    # Iterate n samples
    for _i in range(n):
        # Get new model based on page
        model = transition_model(corpus, page, damping_factor)

        weights = [i for i in model.values()]
        
        # Iterate counter
        counter[page] += 1

        # Get new page
        page = random.choices(pages, weights=weights, k=1)[0]

    # Calculate page rank ratios
    page_rank = {page: score / n for page, score in counter.items()}
    
    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # List all pages
    pages = list(corpus)

    # Set pagerank equally
    page_rank = {page : 1 / len(pages) for page in pages}

    # Initalise dictionary to store links to current page
    linked_from = {page : set() for page in pages}

    # If page has no links, add all pages as links
    for page in corpus:
        if not corpus[page]:
            corpus[page] = pages

    # Get links to the page
    for page in pages:
        for link in corpus:
            if page in corpus[link]:
                linked_from[page].add(link)

    changes = {page : 0 for page in corpus}
    
    # while changes still exist
    while changes:
        for page in corpus:
            if page in changes:
                probability = []

                # For each page that links to page
                for link in linked_from[page]:
                    
                    # Probability is (page_rank / links)
                    probability.append(page_rank[link] / len(corpus[link]))

                # New page rank is (1 - d)/n + d(sum of links)
                pr_score = ((1 - damping_factor) / len(corpus)) + (damping_factor * sum(probability))

                # Change is absoulte value of current score minus new score
                change = abs(round(page_rank[page] - pr_score, 8))

                # If change is less than 0.001, remove page
                if change < 0.001:
                    del changes[page]
                else:
                    changes[page] = change

                # Update page rank
                page_rank[page] = pr_score

    return page_rank