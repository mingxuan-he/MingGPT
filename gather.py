import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta


def check_knowledge_updates():
    """
    check if knowledge base needs update
    """

    UPDATE_FREQUENCY = timedelta(days=7)
    update_needed = {}
    knowledge_files = os.listdir('knowledge/')
    knowledge_files.remove('tracking.json')
    for kf in knowledge_files:
        # check time last modified vs frequency
        last_mod = os.path.getmtime('knowledge/' + kf)
        update_needed[kf] = datetime.now() - datetime.fromtimestamp(last_mod) > UPDATE_FREQUENCY
    return update_needed


def get_cv():
    """
    get cv pdf file (download from github)
    """

    cv_url = 'https://raw.githubusercontent.com/mingxuan-he/mingxuan-he/master/Mingxuan_He_CV.pdf'
    response = requests.get(cv_url)
    with open('knowledge/cv.pdf', 'wb') as f:
        f.write(response.content)


def get_structured_text(url):
    """
    Scrape a webpage and return a json of structured text.
    """

    # get soup
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # scrape projects page
    structured_text = {}

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


def get_personal_website():
    """
    get personal website data (scrape pages using bs4 and store structured text in json)
    """

    website_base_url = 'https://mingxuanhe.xyz'
    website_data = {}
    for page in ['home', 'projects', 'writings', 'resources']:
        url = website_base_url + '/' + page
        structured_text = get_structured_text(url)
        website_data[page] = structured_text
        with open('knowledge/personal_website.json', 'w') as f:
            json.dump(website_data, f, indent=4)


def upload_knowledge(client, assistant_id, filename):
    """
    uploads a file to assitant's knowledge base
    """
    file = client.files.create(
        file=open("knowledge/" + filename, "rb"),
        purpose="assistants"
    )

    # TODO: does create overwrite existing files with same name?

    assistant_file = client.beta.assistants.files.create(
        assistant_id=assistant_id,
        file_id=file.id,
    )


def gather_knowledge(client, assistant_id):
    """
    main function for checking, updating, and uploading knowledge base
    client: openai client
    assistant_id: id of the assistant to upload knowledge to
    """

    # check for knowledge base updates
    update_needed = check_knowledge_updates()
    
    # update outdated files
    if update_needed['cv.pdf']:
        get_cv()
        upload_knowledge(client, assistant_id, filename='cv.pdf')
    
    if update_needed['personal_website.json']:
        get_personal_website()
        upload_knowledge(client, assistant_id, filename='personal_website.json')

    # TODO: gather coding stats and github repos

    # TODO: gather blog posts from medium

    # TODO: gather tweets

    # record update time in tracking file
    if any(update_needed.values()):
        with open("knowledge/tracking.json", 'w') as tracking_file:
            new_update_time = {
                "last_update" : datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            json.dump(new_update_time, tracking_file, indent=4)

