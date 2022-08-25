from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import re
import os


# get base soup:
def getSoupAndDriver():
    chrome_options = webdriver.ChromeOptions()
    #prefs = {"profile.managed_default_content_settings.images": 2,
    #         "profile.default_content_setting_values.notifications" : 2}
    #chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    wait = WebDriverWait(driver, 20)
    action = ActionChains(driver)
    starting_link_to_scrape = "https://www.mobile.de/?lang=en"
    driver.get(starting_link_to_scrape)

    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Accept']"))).click()
    base_source = driver.page_source
    base_soup = BeautifulSoup(base_source,'html.parser')
    return base_soup,driver


def getMakeAndModels(base_soup,driver,make):
    make_list = base_soup.findAll('select', {'data-testid': 'qs-select-make'})[0]
    makes = make_list.findAll('option')
    car_make =[]
    id1=[]

    for i in range(len(makes)):
        car_make.append(makes[i].text.strip())
        try:
            id1.append(makes[i]['value'])
        except:
            id1.append('')

    car_base_make_data = pd.DataFrame({'car_make':car_make,'car_make_id':id1})
    car_make_filter_out = ['Any','Other','']
    car_base_make_data=car_base_make_data[~car_base_make_data.car_make.isin(car_make_filter_out)]
    car_base_make_data = car_base_make_data.drop_duplicates()
    # collecting all models:
    car_base_model_data = pd.DataFrame()
    if make in list(car_base_make_data['car_make']):
        make_id = car_base_make_data[car_base_make_data['car_make']==make]['car_make_id'].to_list()[0]
        driver.find_element_by_tag_name("select").find_element_by_xpath("//option[text()='{}']".format(make)).click()
        time.sleep(5)
        base_source = driver.page_source
        base_soup = BeautifulSoup(base_source, 'html.parser')
        model_list = base_soup.findAll('select', {'data-testid': 'qs-select-model'})[0]
        models = model_list.findAll('option')

        car_model = []
        id2 = []

        for i in range(len(models)):
            # print(car_model.append(models[i].text.strip()))
            car_model.append(models[i].text.strip())
            try:
                # print(models[i]['value'])
                id2.append(models[i]['value'])
            except:
                # print('')
                id2.append('')

        car_base_model_data_aux = pd.DataFrame({'car_model' : car_model, 'car_model_id' : id2})
        car_base_model_data_aux['car_make'] = make
        car_base_model_data_aux['car_make_id'] = int(make_id)
        car_base_model_data = pd.concat([car_base_model_data, car_base_model_data_aux], ignore_index=True)
        car_base_model_data = car_base_model_data.drop_duplicates()
        car_base_model_data = car_base_model_data[~car_base_model_data.car_model.isin(['Any','Other','Andere',''])]
        car_base_model_data = car_base_model_data[car_base_model_data.car_model_id.apply(lambda x: x.isnumeric())]
        car_base_model_data['car_model_id'] = pd.to_numeric(car_base_model_data['car_model_id'])
        car_base_model_data['car_make_id'] = pd.to_numeric(car_base_model_data['car_make_id'])
    return car_base_model_data


def addSearchLinks(df, fr=None, ft=None, ml_min=None, ml_max=None, price_min=None, price_max=None):
    ml=""
    p=""
    from_year=""
    fuel=""
    if fr is not None:
        from_year="fr={}&".format(fr)
    if ft is not None:
        if ft.lower()=='petrol':
            fuel = "ft={}&".format(ft.upper())
        if ft.lower()=='diesel':
            fuel = "ft={}&".format(ft.upper())
    if ml_min is not None:
        ml = "ml={}:&".format(ml_min)
    if ml_max is not None:
        ml = "ml=:{}&".format(ml_max)
    if ml_min is not None and  ml_max is not None:
        ml = "ml={}:{}&".format(ml_min,ml_max)
    if price_min is not None:
        p = "p={}:&".format(price_min)
    if price_max is not None:
        p = "p=:{}&".format(price_max)
    if price_min is not None and  price_max is not None:
        p = "p={}:{}&".format(price_min,price_max)
    for idx, row in df.iterrows():
        df.loc[idx, 'link'] = "https://suchen.mobile.de/fahrzeuge/search.html?dam=0&"+\
                              fuel+from_year+"isSearchRequest=true&"+ml+"ms=" + \
                               str(row['car_make_id']) + ";" + str(row['car_model_id']) +"&"+ \
                              p + "ref=quickSearch&sb=rel&vc=Car"
    return df




def getLinksPerMakeModel(make_model_link,make_model_df,save_to_csv=True):
    chrome_options = webdriver.ChromeOptions()
    #prefs = {"profile.managed_default_content_settings.images": 2,
    #         "profile.default_content_setting_values.notifications" : 2} # this is to not load images
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    #chrome_options.add_experimental_option("prefs", prefs)
    # start a driver
    driver = webdriver.Chrome( ChromeDriverManager().install(),chrome_options=chrome_options)
    wait = WebDriverWait(driver, 20)
    action = ActionChains(driver)

    driver.get(make_model_link)
    wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Einverstanden']"))).click()
    # get number of pages:
    make_model_last_page_src = driver.page_source
    make_model_link_soup = BeautifulSoup(make_model_last_page_src, 'html.parser')
    last_button = make_model_link_soup.findAll('span', {'class': 'btn btn--secondary btn--l'})

    try:
        print("This many pages found: ",last_button[len(last_button)-1].text)
        last_button_number = int(last_button[len(last_button)-1].text)
    except:
        last_button_number = int(1)

    driver.close()

    links_on_multiple_pages=[]

    for i in range(1,last_button_number+1):
        # start a new driver every time
        # we need this to avoid getting blocked by the website. If we don't do this, we will get captcha
        chrome_options = webdriver.ChromeOptions()
        #prefs = {"profile.managed_default_content_settings.images": 2,
        #         "profile.default_content_setting_values.notifications" : 2}  # this is to not load images
        #chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")

        # start a driver
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
        wait = WebDriverWait(driver, 20)
        action = ActionChains(driver)

        # we need to navigate to the page
        one_page_link = make_model_link + "&pageNumber=" + str(i)

        driver.get(one_page_link)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Einverstanden']"))).click()
        base_source = driver.page_source
        base_soup = BeautifulSoup(base_source, 'html.parser')

        # get all the links
        cars_add_list_all = base_soup.findAll('a', {'class': re.compile('^link--muted no--text--decoration')})

        links_on_one_page = []

        for i in range(len(cars_add_list_all)):

            link = cars_add_list_all[i]['href']

            if not link.endswith('SellerAd') and 'topSimilarSellerAd' not in link and \
                'action=topOfPage' not in link and 'action=topInCategory' not in link and \
                 'action=eyeCatcher' not in link:
                # filter out links that end with 'SellerAd' (these are links to ads and we do not need them)
                links_on_one_page.append(link)

        for elements in links_on_one_page:
            links_on_multiple_pages.append(elements)

        driver.close()  # close the driver

    links_on_one_page_df = pd.DataFrame({'car_ad_link' : links_on_multiple_pages})
    #drop duplicates
    links_on_one_page_df = links_on_one_page_df.drop_duplicates()
    links_on_one_page_df['car_make_model_link'] = make_model_link
    #datetime string
    now = datetime.datetime.now()
    datetime_string = str(now.strftime("%Y%m%d_%H%M%S"))
    links_on_one_page_df['download'] = now

    #check is the make and model is in the dataframe
    if isinstance(make_model_df, pd.DataFrame):
        #join the dataframes to get make and model information
        links_on_one_page_df = pd.merge(links_on_one_page_df, make_model_df, how = 'left', left_on= ['car_make_model_link'], right_on = ['link'])
        links_on_one_page_df = links_on_one_page_df.drop(['link'],axis=1)

    #save the dataframe if save_to_csv is True
    if save_to_csv:
        #check if folder exists and if not create it
        if not os.path.exists('../data/make_model_ads_links'):
            os.makedirs('../data/make_model_ads_links')
        links_on_one_page_df.to_csv(str('data/make_model_ads_links/links_on_one_page_df' + datetime_string + '.csv'),sep='|', index = False)

    return links_on_one_page_df




def zipcodeParser(zip_text):
    focus = zip_text.find('DE-')
    if focus ==-1:
        return 'F'
    zipcode = zip_text[focus + 3:focus + 8]
    if zipcode.startswith(tuple(['6','7','8','9'])):
        return 'T'
    return 'F'


def getRelevantCars(df,save_to_csv=True):
    mileages = []
    powers = []
    prices = []
    first_registrations = []
    zipcodes = []
    titles = []

    for idx,row in df.iterrows():
        chrome_options = webdriver.ChromeOptions()
        #prefs = {"profile.managed_default_content_settings.images": 2,
        #         "profile.default_content_setting_values.notifications" : 2}  # this is to not load images
        #chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("--headless")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
        # start a driver
        driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=chrome_options)
        wait = WebDriverWait(driver, 20)
        action = ActionChains(driver)
        driver.get(row['car_ad_link'])

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Einverstanden']"))).click()

        ad_source = driver.page_source
        ad_link_soup = BeautifulSoup(ad_source, 'html.parser')
        mil = ad_link_soup.findAll('div', {'id': 'mileage-v'})[0].text.replace('\xa0',' ')
        pow = ad_link_soup.findAll('div', {'id': 'power-v'})[0].text.replace('\xa0',' ')
        reg = ad_link_soup.findAll('div', {'id': 'firstRegistration-v'})[0].text.replace('\xa0',' ')
        price = ad_link_soup.findAll('span', {'data-testid': 'prime-price'})[0].text.replace('\xa0',' ')
        zipcode = ad_link_soup.findAll('p', {'id': 'db-address'})[0].text.replace('\xa0',' ')
        title = ad_link_soup.findAll('span',{'id':'sticky-ad-title'})[0].text.replace('\xa0',' ')

        mileages.append(mil)
        powers.append(pow)
        prices.append(price)
        first_registrations.append(reg)
        zipcodes.append(zipcode)
        titles.append(title)

        driver.close()
    df['car_title']=titles
    df['price'] = prices
    df['mileage']=mileages
    df['power']=powers
    df['first_registration']=first_registrations
    df['zipcode']=zipcodes
    df['zipcode_flag'] = [zipcodeParser (i) for i in df['zipcode']]

    if save_to_csv:
        #check if folder exists and if not create it
        if not os.path.exists('../data/make_model_ads_links'):
            os.makedirs('../data/make_model_ads_links')
        now = datetime.datetime.now()
        datetime_string = str(now.strftime("%Y%m%d_%H%M%S"))
        df.to_csv(str('data/make_model_ads_links/relevant_ads' + datetime_string + '.csv'),sep='|', index = False)

    df = df[['car_model_id', 'car_model', 'car_make_id', 'car_make', 'car_make_model_link',
             'car_title','first_registration','price', 'mileage', 'power', 'zipcode','zipcode_flag', 'car_ad_link','download']]

    return df


def mobileParser(car_make_str,car_model_str,ft, fr,ml_min, ml_max,price_min, price_max):
    base_soup, driver = getSoupAndDriver()
    df = getMakeAndModels(base_soup, driver, car_make_str)
    driver.close()
    df = addSearchLinks(df, ft=ft, fr=fr, ml_min=ml_min,ml_max=ml_max, price_min=price_min, price_max=price_max)
    my_model_link=""
    try:
        my_model_link = df[df['car_model'] == car_model_str]['link'].to_list()[0]
    except:
        print('No such model exists')
        return None
    df = getLinksPerMakeModel(my_model_link, df, False)
    df = getRelevantCars(df, False)
    return df




'''
# EXAMPLE of usage:
mobile = mobileParser(car_make_str="BMW",car_model_str="Z3",ft="petrol", fr=2002,ml_min=0,
        ml_max=70000,price_min=0, price_max=20000)
'''

'''
# EXAMPLE of usage:
base_soup,driver = getSoupAndDriver(getBrowserDriver(),"https://www.mobile.de/?lang=en")
df = getMakeAndModels(base_soup,driver,"BMW")
driver.close()
df = addSearchLinks(df,ft='petrol',fr=2002,ml_max=70000,price_max=20000)
# pick one model from the previous df
make_model_link = df['link'][150]
my_model_link = df[df['car_model'] == "Z3"]['link'].to_list()[0]

my_model_link = df['link'][len(df['link'])-1]


ad_links_df = getLinksPerMakeModel(make_model_link,df,False)
ad_links_df = getRelevantCars(ad_links_df,False)

'''
