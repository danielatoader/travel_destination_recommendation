from selenium.webdriver import Chrome
import pandas as pd
import time
import urllib.request
import numpy as np
from selenium.webdriver.common.by import By


def collect_urls(browser, home_path):
    """
    Get all href urls on a page that contains the specified path
    """
    urls = []
    links = [a.get_attribute('href')
             for a in browser.find_elements("tag name", 'a')]
    for link in links:
        if home_path in link and link not in urls:
            urls.append(link)
    return urls


def collect_all_data(browser, country_url,
                     country_collection, city_collection):
    """
    Collect summaries of the countries and cities of europe
    and insert into MongoDB collections
    """
    browser.get(country_url)
    country = collect_country_name(browser)
    country_summary = collect_country_summary(browser)
    
    # alternative to mongodb collection
    country_dict = {'country': country, 'country_summary': country_summary}
    # country_collection.insert_one(country_dict)
    country_collection[len(country_collection)] = country_dict
    
    time.sleep(np.random.randint(10, 60))
    print(f'Inserted {country} into country collection')
    city_path = '/europe/' + country.lower() + '/'
    city_urls = collect_urls(browser, city_path)
    for city in city_urls:
        collect_city_data(browser, city, country, city_collection)
        time.sleep(np.random.randint(10, 30))
    print(f'Completed scraping {country}')

    # return country_collection, city_collection


def collect_country_name(browser):
    """Collects the country name from ricksteves.com"""
    country_path = '//*[@id="body"]/div[2]/div[1]/div/h1'
    country = browser.find_element(By.XPATH, country_path).text
    return country


def collect_country_summary(browser):
    """Collects the country summary from ricksteves.com"""
    summary_path = '//*[@id="body"]/div[2]/div[1]/div/div[3]/p'
    country_summary = browser.find_element(By.XPATH, summary_path).text
    return country_summary


def collect_city_data(browser, city_url, country, city_collection):
    """
    Gather the city summary, photo, and url and add to the city
    MongoDB collection
    """
    browser.get(city_url)
    try:
        city = collect_city_name(browser)
        summary = collect_city_summary(browser)

        city_dict = {'city': city, 'country': country,
                     'city_summary': summary,
                     'city_url': city_url}
        # alternative to mongodb
        # city_collection.insert_one(city_dict)
        city_collection[len(city_collection)] = city_dict

        print(f'Inserted {city}, {country} into city collection')

        # return city_collection
    except:
        None


def collect_city_name(browser):
    """Collects the city name from ricksteves.com"""
    city_path = '//*[@id="body"]/div[2]/div[1]/div/h1'
    city = browser.find_element(By.XPATH, city_path).text
    return city


def collect_city_summary(browser):
    """
    Collects the city summary from ricksteves.com
    """
    summary_path = '//*[@id="body"]/div[2]/div[1]/div/div[3]/p'
    summary = browser.find_element(By.XPATH, summary_path).text
    return summary


def collect_city_photo(browser, country_url):
    """
    Collects the header photo from ricksteves.com
    """
    browser.get(country_url)
    country_path = '//*[@id="body"]/div[2]/div[1]/div/h1'
    country = browser.find_element(By.XPATH, country_path).text

    city_path = '/europe/' + country.lower() + '/'
    city_urls = collect_urls(browser, city_path)
    for city_url in city_urls:
        browser.get(city_url)
        time.sleep(np.random.randint(10, 30))
        try:
            city_path = '//*[@id="body"]/div[2]/div[1]/div/h1'
            city = browser.find_element(By.XPATH, city_path).text
            image_path = '//*[@id="slideshow1_s0"]/figure/img'
            image = browser.find_element(By.XPATH, image_path)
            img_url = image.get_attribute('src')
            filename = 'images/' + city.lower() + '.jpg'
            urllib.request.urlretrieve(str(img_url), filename=str(filename))
        except:
            continue


def get_wiki_description(browser, city, wiki_collection):
    """
    Get the wikipedia text entry of the city.
    If the city is not in wikipedia, it will raise an alert
    """
    url = 'https://en.wikipedia.org/wiki/' + city.replace(' ', '_')
    try:
        browser.get(url)
    except:
        print(f'{city} NOT found on Wikipedia')
    summary = ''
    for i in range(1, 100):
        paragraphs = '//*[@id="mw-content-text"]/div/p[' + str(i) + ']'
        try:
            summary += browser.find_element(By.XPATH, paragraphs).text
            summary += '\n'
        except:
            None
    wiki_dict = {'city': city, 'text': summary}

    # alternative to mongodb
    # wiki_collection.insert_one(wiki_dict)
    wiki_collection[len(wiki_collection)] = wiki_dict


def replace_df_text(browser, city, df):
    """
    Replaces text summaries in a data frame with the text
    from a wikipedia article
    """
    url = 'https://en.wikipedia.org/wiki/' + city[1].replace(' ', '_')
    browser.get(url)
    summary = ''
    for i in range(1, 100):
        paragraphs = '//*[@id="mw-content-text"]/div/p[' + str(i) + ']'
        try:
            summary += browser.find_element(By.XPATH, paragraphs).text
            summary += '\n'
        except:
            None
    df.loc[df['city'] == city[0], 'text'] = summary
