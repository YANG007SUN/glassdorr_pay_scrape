
#####################################################################################
#
# The script is scraping GlassDoor pay rate information based on THREE input parameters
#
#####################################################################################

# import packages
from bs4 import BeautifulSoup as bs
from splinter import Browser
from config import username, password
import datetime
import time
import pandas as pd
import requests
from webdriver_manager.chrome import ChromeDriverManager
from collections import defaultdict
import sys


def init_browser(chromdriver_path):
    """input chromdriver path for *** MAC users ***
       chromdriver_path='/Users/yangsun/Downloads/chromedriver 5'
    """
    executable_path = {'executable_path': chromdriver_path}
    browser = Browser('chrome', **executable_path, headless=False)
    return browser

def sign_in_GlassDoor(username, password):
    """sign in
    """
    # visit url
    login_url='https://www.glassdoor.com/profile/login_input.htm'
    browser.visit(login_url)
    # sign in
    browser.find_by_id('inlineUserEmail').fill(username)
    browser.find_by_id('inlineUserPassword').fill(password)
    browser.find_by_xpath('//button[@type="submit"]').click()

def select_area(area_name):
    """select area from selector
    """
    browser.find_by_xpath('//button[@class="gd-ui-button d-none d-lg-inline-block css-pitbid"]').click()
    browser.find_by_xpath('//span[@class="SVGInline arrowDown"]')[1].click()
    browser.find_by_text(area_name).first.click()

def get_frontend_info(pay_list):
    """Extract front end job title information
           - front end title
           - avg total pay
           - additional pay
       Return: 
           {front end title:[avg base pay, base pay, additional pay]}
    """
    # front_end_info= {front end title:[avg base pay, base pay, additional pay, Number of reported salaries]}
    front_end_info=defaultdict(list)
    title=pay_list.a.strong.text
    # pay
    pay=pay_list.span.strong.text
    # additional pay
    tag=pay_list.find_all('span',text='Additional Pay')
    # check if additional pay tag exist
    if len(tag)==0:
        additional_pay=0
    else:
        additional_pay=tag[0].find_parent('div').strong.text
    # reports
    reports=pay_list.find_all('span',class_='css-kkqchx')[-1].text
    front_end_info[title]=[pay,additional_pay,reports]
    return front_end_info

def next_page():
    """click next page button
    """
    browser.find_by_xpath('//button[@class="nextButton css-1hq9k8 e13qs2071"]').click()

def get_current_page_info(pay_lists,res:list):
    """Extract current page pay information
    """
    for pay_list in pay_lists:
        title=pay_list.a.strong.text
        if title.lower() not in title_list:
            continue
        # get front data
        front_end_info=get_frontend_info(pay_list)
        res.append(front_end_info)
    return res

if __name__=='__main__':
    # define parameters
    area_name=sys.argv[1]
    glass_door_scraping_web=sys.argv[2]
    output_path=sys.argv[3]

    # open browser
    chromdriver_path='/Users/yangsun/Downloads/chromedriver 5'
    browser=init_browser(chromdriver_path)

    # sign in
    sign_in_GlassDoor(username, password)
    time.sleep(2)

    # visit the web
    browser.visit(glass_door_scraping_web)
    time.sleep(2)

    # filter to the area
    select_area(area_name)
    time.sleep(1)

    # total page number
    html=browser.html
    soup = bs(html, 'html.parser')
    page=int(soup.find_all('div',class_='paginationFooter')[0].text.split(' ')[-2])
    print(f'Total number of pages :{page}')

    # only look for 
    title_list = ['general manager',
                'assistant manager',
                'counter help',
                'counter helper',
                'shift leader',
                'cook',
                'shift lead',
                'kitchen help',
                'kitchen helper',
                'lead counter',
                'lead counter help',
                'front of house',
                'back of house',
                'cashier',
                'crew member',
                'chef',
                'pic',
                'FOH team member',
                'kitchen staff',
                'FOH']
    # scraping (get the first 20pages information)
    final_res=[]
    for p in range(20):
        # all pay list for the current page
        pay_lists=soup.find_all('div',class_='css-1u4lhyp')
        get_current_page_info(pay_lists,final_res)
        time.sleep(1)
        # next page
        next_page()
        time.sleep(2)
    # create a list for panda dataframe
    t=[list(d.keys())+list(d.values())[0] for d in final_res]
    final_data=pd.DataFrame(t,columns=['title','Average total pay','additional pay','creditbility'])
    final_data.to_csv(output_path)





