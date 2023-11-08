import requests
from bs4 import BeautifulSoup
import json


def get_structured_text(url):
    """
    Scrape a webpage and return a json of structured text.
    """

    # get soup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # scrape projects page
    structured_text = {}

    """
    # get general information from elements without preceding headers (currently buggy)
    structured_text = {'General Information': {'text': [], 'links': []}}
    for element in soup.find_all(['span']):
        # check if this element is preceded by a header
        if element.find_previous_siblings(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            continue  # If there's a header, it's already been processed

        # get text and links from elements without preceding headers
        txt = element.get_text(strip=True)
        if txt not in structured_text['General Information']['text'] and txt != "":
            structured_text['General Information']['text'].append(txt)
        links = element.find_all('a', href=True)
        for link in links:
            structured_text['General Information']['links'].append({'text': link.get_text(strip=True), 'url': link['href']})
    """

    # find all header tags and corresponding text
    for header_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        for header in soup.find_all(header_tag):
            # header text as key
            header_text = header.get_text(strip=True)
            
            # initialize a list to hold paragraph texts and links
            content = {'text': [], 'links': []}

            # check if the header itself contains links
            for link in header.find_all('a', href=True):
                if not link['href'].startswith('#'):
                    content['links'].append({'text': link.get_text(strip=True), 'url': link['href']})
            
            # get following siblings that are paragraphs or divs
            for sib in header.find_next_siblings(['p', 'div', 'span', 'ul']):
                content['text'].append(sib.get_text(strip=True))
                
                # find all 'a' tags within the sibling and get their hrefs
                links = sib.find_all('a', href=True)
                for link in links:
                    content['links'].append({'text': link.get_text(strip=True), 'url': link['href']})
            
            # combine text and links under the header in the dictionary
            structured_text[header_text] = content

    return structured_text


def gather():

    # download cv pdf file
    cv_url = 'https://raw.githubusercontent.com/mingxuan-he/mingxuan-he/master/Mingxuan_He_CV.pdf'
    response = requests.get(cv_url)
    with open('knowledge/cv.pdf', 'wb') as f:
        f.write(response.content)


    # scrape pages from personal website using bs4
    website_base_url = 'https://mingxuanhe.xyz'

    website_data = {}
    for page in ['home', 'projects', 'writings', 'resources']:
        url = website_base_url + '/' + page
        structured_text = get_structured_text(url)
        website_data[page] = structured_text
        with open('knowledge/personal_website.json', 'w') as f:
            json.dump(website_data, f, indent=4)

    # TODO: gather coding stats and github repos




if __name__ == '__main__':
    gather()

