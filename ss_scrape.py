#!/usr/bin/env python3
#
# Written by Aditya Singgih
#
#


from bs4 import BeautifulSoup as bs
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options

from dotenv import load_dotenv, find_dotenv
from pathlib import Path
env_path = Path().absolute()/'.env'
load_dotenv(dotenv_path=str(env_path.resolve())) 

import re
import sys
import os
import subprocess

import pandas as pd
pd.set_option('display.width', 1000)
pd.set_option('display.max_columns', 1000)
pd.set_option('max_colwidth', 800)


def read_web_source():
    """
    returns selenium driver
    """
    base_url = "https://immi.homeaffairs.gov.au/"
    url = base_url + "visas/working-in-australia/skillselect/invitation-rounds"

    # create a new headless chrome session
    # headless means it doesn't open the browser GUI
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--incognito')

    driver = wd.Chrome(options=chrome_options)

    # keep "browser" open for 30s at most to allow page to laod
    driver.implicitly_wait(30)
    driver.get(url)

    return driver


def get_inv_date_and_table():
    """
    returns current invitation date and html occupation table in string
    """

    driver = read_web_source()

    soup = bs(driver.page_source, 'lxml')

    driver.quit()		# close the 'browser' once done with the scraping

    date_and_tables_soup = soup.find_all('div', {"class": "edit-text"})[1]

    # the header of the current invitation round
    h3 = str(date_and_tables_soup.find('h3'))
    match = re.search(r'\d+ \w+ [0-9]{4}', h3)
    current_inv_date = match.group(0)

    # extract table from html soup
    occ_table = str(date_and_tables_soup.find_all('table')[2])

    return current_inv_date, occ_table


def generate_table(occupation_list_table):
    """
    returns dataframe table of occupations list
    """

    # need to specify header=0 since thead is missing in the html_table string
    df = pd.read_html(occupation_list_table, header=0)[0]
    df.columns = ['Subclass', 'id', 'Occupation',
                  'Minimum_Points', 'Date_of_Effect']
    df = df.set_index('id')

    # Handling N/A values for the points and date of effect
    df['Minimum_Points'] = df['Minimum_Points'].fillna("N/A")
    df['Date_of_Effect'] = df['Date_of_Effect'].fillna("N/A")

    return df

def update_record(file, occ_table, invitation_date):
    """
    Write latest table to file
    """

    print("Updating list")
    list_table = generate_table(occ_table)
    file.write(invitation_date + "\n\n")

    make_pretty = {

        'Occupation': '{{:<{}s}}'.format(
            list_table['Occupation'].str.len().max()
        ).format,

        'Date_of_Effect': '{{:<{}s}}'.format(
            list_table['Date_of_Effect'].str.len().max()
        ).format

    }

    file.write(list_table.to_string(justify='center', formatters=make_pretty))

    file.write("\n\n\n")

    file.write("The data in this table is licenced under "
               "a Creative Commons attribution 3.0 Australia licence,\n"
               "attributed to Australian Government Department of Home Affairs")

    file.write("\n\n")

    return True

def broken_script_warning(file, message_content):
    """
    Send a reminder to fix broken script
    """

    file.truncate(0)
    file.write(message_content + "\n\n")

if __name__ == '__main__':

    email = os.getenv("MY_EMAIL")
        
    filename =  str(Path('current_list.txt').absolute())
    file_operation = 'r+'
    if not os.path.exists(filename):
        file_operation = 'w+'

    broken_content = "Fix the script" # message to send just in case script is broken

    try: # check if we can pull invitation date and the correct table
        invitation_date, occ_table = get_inv_date_and_table()
        
        new_record = False
        with open(filename, file_operation) as record:
            
            error_mess = "record update error"

            # check current record at hand
            content_title = record.readline().strip()
            
            if content_title == broken_content.strip():
                print("Fix the damn script - {}".format(error_mess))
            elif content_title == invitation_date.strip():
                print("No update")
                print("Current invitation round is {}".format(invitation_date))
            
            else:
                # put pointer to the beginning of file before writing
                record.seek(0)
                new_record = True
                try:
                    update_record(record, occ_table, invitation_date)
                    subject = "Skillselect Update"
                    
                except Exception as e:
                    broken_script_warning(record, broken_content)
                    subject = "Fix Skillselect Script - {}".format(error_mess)
                    print(subject)
    
    except Exception as e:
        
        with open(filename, file_operation) as record:

            error_mess = "record pulling error"

            if record.readline().strip() == broken_content.strip():
                print("Fix the damn script - {}".format(error_mess))
            
            else:
                new_record = True
                broken_script_warning(record, broken_content)
                subject = "Fix Skillselect Script - {}".format(error_mess)
                print(subject)

    if new_record:
        send_email_cmd = "(mutt -s '{}' {} < {})".format(subject, email, filename)
        subprocess.call(send_email_cmd, shell=True)
        print("Current invitation round is {}".format(invitation_date))

    
