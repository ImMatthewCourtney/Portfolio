from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import os

def saveToFile(dictionary_Str):
    # #Create a CSV file
    with open('prizePicks_nba.csv', 'a') as f:
        writer = csv.DictWriter(f, fieldnames=dictionary_Str.keys())
        writer.writerow(dictionary_Str)

def deleteCSVFile():
    csv_file_path = 'prizePicks_nba.csv'
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
        print(f"{csv_file_path} has been deleted.")
    else:
        print(f"{csv_file_path} does not exist.")

with sync_playwright() as p:
        browser = p.chromium.launch(
               headless=False, 
               slow_mo=50
               )
        page = browser.new_page()
        deleteCSVFile()
        page.goto('https://www.prizepicks.com/')
        page.get_by_role('link', name='Log In').click()
        page.fill('input#email-input', 'XXXXXXX@gmail.com')
        page.fill('input[type=password]', 'XXXXXXX')
        page.click('button[type=submit]')
        page.get_by_role('button', name='Sounds Good').click()

        League_soup = BeautifulSoup(page.content(), 'html.parser')
        num_league_tags = League_soup.find_all('div', class_=lambda x: x in ['league', 'league selected'])

        count = len(num_league_tags)
        for leagueI in range(0, count):

            if page.query_selector("div[class='league']"):
                page.wait_for_selector("div[class='league']")
                league_tags = page.query_selector_all("div[class='league']")
            page.wait_for_selector("div[class='league selected']")
            league_sel_tags = page.query_selector_all("div[class='league selected']")
            league_tags.append(league_sel_tags)

            pLeague = num_league_tags[leagueI].find('div', class_='name')

            if pLeague.get_text() == 'NBA':
                statCount = 0
                num_stat2_tags = []
                num_stat_tags = []

                if len(num_stat2_tags) != 0:
                    for e in num_stat2_tags:
                        print("removing e in List : ")
                        num_stat2_tags.remove(e)

                if len(num_stat_tags) != 0:
                    for s in num_stat_tags:
                        print("removing s in List : ")
                        num_stat_tags.remove(s)

                if page.query_selector("div[class='stat ']"):
                        page.wait_for_selector("div[class='stat ']")
                        num_stat_tags = page.query_selector_all("div[class='stat ']")
                page.wait_for_selector("div[class='stat stat-active']")         
                num_stat2_tags = page.query_selector_all("div[class='stat stat-active']")
                num_stat_tags.append(num_stat2_tags)
                print(len(num_stat_tags))
                statCount = len(num_stat_tags)
                if statCount > 1:
                    for i in range(0, statCount):
                        page.wait_for_selector("div[class='projection']")         
                        projections = page.query_selector_all("div[class='projection']")
                        projCount = len(projections)
                        for p in range(0, projCount):
                            my_dictionary = dict()
                            page.wait_for_selector("div[class='projection']")         
                            proj_tags = page.query_selector_all("div[class='projection']")

                            inner_html = proj_tags[p].inner_html()
                            soup = BeautifulSoup(inner_html, 'html.parser')
                            pName = soup.find('div', class_='name')
                            pScore = soup.find('span', class_='strike-red')
                            pType = soup.find('div', class_='text')
                            print(pLeague.get_text() + ',' + pName.get_text().rstrip() + ',' + pType.get_text() + ',' + pScore.get_text())
                            my_dictionary.update({'sport': pLeague.get_text(), 'name': pName.get_text().rstrip(), 'type': pType.get_text(), 'score': pScore.get_text()})
                            saveToFile(my_dictionary)

                        page.wait_for_timeout(1000)
                        if page.query_selector("div[class='stat ']"):
                            page.wait_for_selector("div[class='stat ']")
                            stat_tags = page.query_selector_all("div[class='stat ']")
                        page.wait_for_selector("div[class='stat stat-active']")
                        sel_stat_tag = page.query_selector_all("div[class='stat stat-active']")
                        stat_tags.append(sel_stat_tag)

                        print("stat tags i = " + str(i))
                        if i < statCount-1:
                            stat_tags[i].click()
                        else:
                            break

                else:
                    page.wait_for_selector("div[class='projection']")
                    projections = page.query_selector_all("div[class='projection']")
                    projCount = len(projections)
                    for p in range(0, projCount):
                        my_dictionary = dict()
                        page.wait_for_selector("div[class='projection']")         
                        proj_tags = page.query_selector_all("div[class='projection']")
                        inner_html = proj_tags[p].inner_html()
                        soup = BeautifulSoup(inner_html, 'html.parser')
                        pName = soup.find('div', class_='name')
                        pScore = soup.find('span', class_='strike-red')
                        pType = soup.find('div', class_='text')
                        print(pLeague.get_text() + ',' + pName.get_text().rstrip() + ',' + pType.get_text() + ',' + pScore.get_text())
                        my_dictionary.update({'sport': pLeague.get_text(), 'name': pName.get_text().rstrip(), 'type': pType.get_text(), 'score': pScore.get_text()})
                        saveToFile(my_dictionary)
                    page.wait_for_timeout(1000)

            if leagueI < count-1:
                league_tags[leagueI].click()
            else:
                break