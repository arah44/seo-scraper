import os
import random
import re
import sys
import json

import helpers as hlp

from settings import *

def main():

    # Search current directory for json file
    file_exisits = False
    file_name = NAME + "_data.csv"
    for file in os.listdir():
        if file == file_name:
            file_exisits = True


    # If no json in current directory, create one
    if not file_exisits:
        data = hlp.generate_data(NAME, URL)

    else:
        with open(file_name, "r") as file:
            data = csv.load(file)

    # Check if "links-in" has been generated
    shape = list(data[URL].keys())
    if "links-in" not in shape:
        data = hlp.update_internal_links(data)
        hlp.save_as_file(data)

    if CHECK_REDIRECT_CHAINS:
        data = hlp.check_redirect_chains(data)

    hlp.save_as_file(data)

if __name__ == "__main__":
    main()
