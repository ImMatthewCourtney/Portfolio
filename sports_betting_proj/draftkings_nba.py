from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import csv
import os
import math

def saveToFile(dictionary_Str):
    # #Create a CSV file
    with open('draftkings_nba.csv', 'a') as f:
        writer = csv.DictWriter(f, fieldnames=dictionary_Str.keys())
        writer.writerow(dictionary_Str)

def remove_substring(source_string, substring_to_remove):
    print(source_string)
    return source_string.replace(substring_to_remove, '')

def is_positive(string):
    if "+" in string:
        return True
    elif "-" in string:
        return False
    else:
        True

def get_probability(numb):
    #Decimal odds = (100 / (absolute value of moneyline odds)) + 1
    decimal_odds = (100 / float(numb)) + 1
    probability = 1 / decimal_odds
    return probability

def round_percent(value):
    rounded_value = math.ceil(value)
    formatted_percentage = "{}".format(rounded_value)
    return formatted_percentage

def remove_odd_neg(s: str) -> str:
    print(str)
    s = s.replace("−", "-")
    return s

def deleteCSVFile():
    csv_file_path = 'draftkings_nba.csv'
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
    deleteCSVFile()

    page = browser.new_page()
    page.goto('https://sportsbook.draftkings.com/leagues/basketball/nba')

    buttonList = ['game_category_Player Points', 'game_category_Player Rebounds', 'game_category_Player Assists', 'game_category_Player Threes', 'game_category_Player Turnovers']

    for i in range(0, len(buttonList)):
        print("loop i = " + str(i))
        target_element = page.query_selector(f'a.sportsbook-category-tab[id="{buttonList[i]}"]')
        if target_element:
            linkList = ['a[id="game_category_Player Points"]', 'a[id="game_category_Player Rebounds"]', 'a[id="game_category_Player Assists"]', 'a[id="game_category_Player Threes"]', 'a[id="game_category_Player Turnovers"]']
            player_points = linkList[i]
            page.click(player_points)
            if i > 0:
                page.reload()
            page.wait_for_timeout(1000)
            tbody_elements = page.query_selector_all('tbody.sportsbook-table__body')
            print("Number of tbody = " + str(len(tbody_elements)))
            typeList = ['Points', 'Rebounds', 'Assists', '3-PT Made', 'Turnovers']

            for item in tbody_elements:
                for tr in item.query_selector_all('tr'):
                    if not tr.get_attribute('class'):
                        name = tr.query_selector('span.sportsbook-row-name')
                        if name:
                            over_under = tr.query_selector_all('span.sportsbook-outcome-cell__label')
                            nums = tr.query_selector_all('span.sportsbook-outcome-cell__line')
                            odds = tr.query_selector_all('span.sportsbook-odds.american.default-color')

                            if is_positive(odds[0].text_content()):
                                overNumb = remove_substring(odds[0].text_content(), '+')
                            else:
                                overNumb = remove_substring(odds[0].text_content(), '−')
                            if is_positive(odds[1].text_content()):
                                underNumb = remove_substring(odds[1].text_content(), '+')
                            else:
                                underNumb = remove_substring(odds[1].text_content(), '−')

                            overProb = get_probability(float(overNumb))
                            underProb = get_probability(float(underNumb))
                            sumProb = overProb + underProb
                            trueOverOdds = (overProb / float(sumProb)) * 100
                            trueUnderOdds = (underProb / float(sumProb)) * 100


                            my_dictionary = {
                                'name': name.text_content(),
                                'type': typeList[i],
                                'Over': over_under[0].text_content(),
                                'Over_Num': nums[0].text_content(),
                                'Over_Odds': remove_odd_neg(remove_substring(odds[0].text_content(), '+')),
                                'True_Over_Odds': round_percent(trueOverOdds),
                                'Under': over_under[1].text_content(),
                                'Under_Num': nums[1].text_content(),
                                'Under_Odds': remove_odd_neg(remove_substring(odds[1].text_content(), '+')),
                                'True_Under_Odds': round_percent(trueUnderOdds)
                            }
                            saveToFile(my_dictionary)