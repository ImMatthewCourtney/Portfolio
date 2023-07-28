from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import re
import os
import math

def saveToFile(dictionary_Str):
    # #Create a CSV file
    with open('pinnacle_nba.csv', 'a') as f:
        writer = csv.DictWriter(f, fieldnames=dictionary_Str.keys())
        writer.writerow(dictionary_Str)

def deleteCSVFile():
    csv_file_path = 'pinnacle_nba.csv'
    if os.path.exists(csv_file_path):
        os.remove(csv_file_path)
        print(f"{csv_file_path} has been deleted.")
    else:
        print(f"{csv_file_path} does not exist.")

def remove_substring(source_string, substring_to_remove):
    return source_string.replace(substring_to_remove, '')

def get_probability(numb):
    #Decimal odds = (100 / (absolute value of moneyline odds)) + 1
    decimal_odds = (100 / float(numb)) + 1
    probability = 1 / decimal_odds
    return probability

def round_percent(value):
    rounded_value = math.ceil(value)
    formatted_percentage = "{}".format(rounded_value)
    return formatted_percentage

def remove_plus_minus(s: str) -> str:
    s = s.replace("+", "")
    s = s.replace("-", "")
    return s

def give_type(source_string):
    pattern = r'\((.*?)\)'
    typeName = ''
    match = re.search(pattern, source_string)
    if match:
        inside_brackets = match.group(1)
    typeName = inside_brackets
    if inside_brackets == '3 Point FG':
        typeName = '3-PT Made'
    return typeName

def get_numb_from_str(source_str):
    number_pattern = re.compile(r'\d+(\.\d+)?')
    match = number_pattern.search(source_str)

    if match:
        extracted_number = float(match.group(0))
        print(extracted_number)
        return extracted_number
    else:
        print("No number found in the input string")
        return ''

def only_player_name(source_string):
    pattern = r'\((.*?)\)'
    match = re.search(pattern, source_string)
    if match:
        output_string = re.sub(pattern, '', source_string.strip())
    return output_string


with sync_playwright() as p:
        browser = p.chromium.launch(
               headless=False, 
               slow_mo=50
               )
        deleteCSVFile()
        page = browser.new_page()
        page.goto('https://www.pinnacle.com/en/basketball/nba/matchups#period:0')
        content = page.content()
        page.wait_for_selector("div[class='style_dropdown__12wIh style_button__2FVbj style_dropDownButton___iNk0']")
        page.query_selector("div[class='style_dropdown__12wIh style_button__2FVbj style_dropDownButton___iNk0']").click()
        page.wait_for_timeout(1000)
        page.wait_for_selector("li[class='style_not-selected__oDp2k']")
        page.query_selector("li[class='style_not-selected__oDp2k']").click()
        page.wait_for_timeout(1000)

        page.wait_for_selector("div[class='style_metadata__1FIzs']")
        games = page.query_selector_all("div[class='style_metadata__1FIzs']")

        for i in range(0, len(games)):
            page.wait_for_selector("div[class='style_metadata__1FIzs']")
            gameList = page.query_selector_all("div[class='style_metadata__1FIzs']")
            gameList[i].click()
            page.wait_for_timeout(1000)
            #click player props
            button = page.query_selector('#player-props')
            if button:
                page.locator("#player-props").click()

                page.wait_for_selector("div[class='style_primary__3IwKt style_marketGroup__1-qlF']")
                playerList = page.query_selector_all("div[class='style_primary__3IwKt style_marketGroup__1-qlF']")
                for p in range(0, len(playerList)):
                    theType = ''
                    innerHtml = playerList[p].inner_html()
                    soup = BeautifulSoup(innerHtml, "html.parser")
                    playerName = soup.find("div", class_="style_title__1lSes collapse-title style_collapseTitle__1bRAY").span.text
                    subPlayer = remove_substring(playerName, '(must play)')
                    theType = give_type(subPlayer)
                    playerName = only_player_name(subPlayer).rstrip()
                    print(playerName)

                    underText = ''
                    underNumber = ''
                    overText = ''
                    overNumber = ''

                    dataButtons = soup.find_all("button", class_="market-btn style_button__34Zqv style_pill__1NXWo style_horizontal__10PLW")
                    if dataButtons:
                        overText = dataButtons[0].find("span", class_="style_label__2KJur").text
                        overNumber = dataButtons[0].find("span", class_="style_price__15SlF").text
                        underText = dataButtons[1].find("span", class_="style_label__2KJur").text
                        underNumber = dataButtons[1].find("span", class_="style_price__15SlF").text

                        overProb = get_probability(remove_plus_minus(overNumber))
                        underProb = get_probability(remove_plus_minus(underNumber))
                        sumProb = overProb + underProb
                        trueOverOdds = (overProb / float(sumProb)) * 100
                        trueUnderOdds = (underProb / float(sumProb)) * 100

                        print(str(get_numb_from_str(underText)) + ' ' + underNumber + ' ' + str(get_numb_from_str(overText)) + ' ' + overNumber)
                        my_dictionary = dict()
                        my_dictionary.update({'name': playerName, 'type': theType, 'Over': 'O', 'Over_Num': get_numb_from_str(overText), 'Over_Odds': remove_substring(overNumber, '+'), 'Over_Prob': round_percent(trueOverOdds), 'Under': 'U', 'Under_Num': get_numb_from_str(underText), 'Under_Odds': remove_substring(underNumber, '+'), 'Under_Prob': round_percent(trueUnderOdds)})
                        saveToFile(my_dictionary)
            page.wait_for_timeout(5000)
            breadCrumb = page.query_selector("li[data-test-id='Breadcrumb-Item-League']")
            breadCrumb.click()
            page.wait_for_timeout(5000)