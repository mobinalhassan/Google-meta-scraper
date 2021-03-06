from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from src.scrap_counties_list import usa_county_list,local_listing,special_list
from selenium.webdriver.common.keys import Keys
from src.utils import get_full_path
from src.parser import keyword_map
from src.user_agents import user_agents
import random
from fake_useragent import UserAgent
from pyvirtualdisplay import Display
import xlsxwriter
display = Display(visible=0, size=(800, 600))
display.start()

class FenceInstallerScraper:
    fence_installers = []

    def __init__(self, county):
        self.pro_url = 'https://www.google.com'
        county_split = str(county).split(',')
        county_single = county_split[0]
        state = county_split[1]
        self.check_irrelevent=[]
        self.fance_installer = {'County': county_single, 'Company/Title': '', 'State': state, 'Website': '',
                                'Description': '', 'Rank': '',
                                'Ranked-page-url': ''}
        self.county = county
        self.rank_index = 1
        options = Options()
        options.add_argument("start-maximized")
        # ua = UserAgent()
        # useragent = ua.random
        useragent = random.choice(user_agents)
        print(f'User Agent ==> {useragent}')
        options.add_argument(f'user-agent={useragent}')
        options.add_argument('window-size=1600x900')
        options.add_argument('--no-sandbox')
        options.add_argument("--hide-scrollbars")
        options.add_argument("disable-infobars")
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=options)

    def __del__(self):
        print("Delete")
        self.driver.quit()

    def start(self):
        print('start')
        self.get_query_records()

    def set_cookies(self):
        try:
            sleep(5)
            self.driver.implicitly_wait(10)
            cookie = {'name': 'foo', 'value': 'bar'}
            self.driver.add_cookie(cookie)
            print(f"Cookies set ==> {cookie}")
        except Exception as error:
            print(f"Failed in setting cookies ==> {error}")

    def save_excel_file(self):
        dataframe = pd.DataFrame(self.fence_installers)
        dataframe.to_excel(get_full_path("../data/All_Fence_installers_facebook_37_c3.xlsx"), engine='xlsxwriter')
        print(f'File saved! Records ==> {len(self.fence_installers)}')

    def input_query(self):
        input_q = self.driver.find_element_by_css_selector('input.gLFyf')
        q_keyword = 'agricultural and farm fence installers '
        query = f'{q_keyword}{self.county} site:facebook.com'
        print(f'Query ==> {query}')
        input_q.send_keys(query)
        sleep(2)
        input_q.send_keys(Keys.RETURN)

    def special_ext(self, param):
        if param.split('.')[-1] in special_list or param.split('.')[-2] in special_list:
            return False
        return True

    def inrelevent(self,prami):
        for word in prami:
            if word in ['directory','pages']:
                return True

        return False

    def get_data_with_rank(self):
        list_of_q_result = self.driver.find_elements_by_css_selector('div.g:nth-of-type(n)')
        print(len(list_of_q_result))
        for q_result in list_of_q_result:
            self.fance_installer['Rank'] = str(self.rank_index)
            self.rank_index = self.rank_index + 1
            result_source_code = q_result.get_attribute("innerHTML")
            result_soup: BeautifulSoup = BeautifulSoup(result_source_code, 'html.parser')
            try:
                web_link_raw = result_soup.find('cite', class_='iUh30')

                web_link = str(web_link_raw.get_text()).split(' ')[0]
                try:
                    self.check_irrelevent=str(web_link_raw.get_text()).split(' ')[1:]
                except IndexError:
                    pass
                self.fance_installer['Website'] = str(web_link).strip(' ').strip()
                # print(f'Web link => {web_link}')
            except Exception as error:
                print(f'Error in getting Web Link {error}')

            try:
                ranked_page = result_soup.find('a').get('href')
                self.fance_installer['Ranked-page-url'] = str(ranked_page)
                # print(f'Ranked Page => {ranked_page}')

            except Exception as error:
                print(f'Error in getting Ranked page Link {error}')

            try:
                company_name_raw = result_soup.find('h3', class_='LC20lb')
                company_name = str(company_name_raw.get_text()).replace('...', '').encode('ascii', 'ignore').decode(
                    'utf-8')
                self.fance_installer['Company/Title'] = str(company_name)
                # print(f'Company Name => {company_name}')
            except Exception as error:
                print(f'Error in getting Ranked page Link {error}')

            try:
                description_raw = str(result_soup.find('span', class_='st').get_text())
                description = description_raw.replace('...', '').encode('ascii', 'ignore').decode('utf-8')
                self.fance_installer['Description'] = str(description)
                # print(f'Description => {description}')
                # company_name=company_name_raw
                # print(f'Company Name => {company_name}')
            except Exception as error:
                print(f'Error in getting Ranked page Link {error}')

            if not self.inrelevent(self.check_irrelevent):
                if self.special_ext(self.fance_installer['Website']):
                    if keyword_map(self.fance_installer):
                        print()
                        self.fence_installers.append(self.fance_installer.copy())
                        print(self.fance_installer)
                        print('*' * 80)
                        print()

    def get_query_records(self):
        try:
            print(self.pro_url)
            self.driver.get(self.pro_url)
            user_agent = self.driver.execute_script("return navigator.userAgent;")
            print(f'Inner User aggent ==> {user_agent}')
            self.set_cookies()
            sleep(15)
            self.input_query()
            # input('Something..... = ')
            sleep(20)
            self.get_data_with_rank()
            for i in range(2):
                try:
                    next_link=self.driver.find_element_by_css_selector('#pnnext span:nth-of-type(2)')
                    next_link.click()
                    sleep(5)
                    self.get_data_with_rank()
                except NoSuchElementException:
                    print('No next page')

            self.save_excel_file()
            self.driver.quit()
        except Exception as error:
            print(f'Quitting form get pro link function ==> {error}')
            self.driver.quit()


def main():
    chi=1
    checker=19
    for county in usa_county_list:
        if chi>checker:
            print(f'Check list pars {checker} {chi}')
            checker=checker+19
            sleep(1000)
        print(f'Iteration NO => {chi}')
        fence_installer = FenceInstallerScraper(county)
        fence_installer.start()
        chi=chi+1


if __name__ == "__main__":
    main()

display.stop()
