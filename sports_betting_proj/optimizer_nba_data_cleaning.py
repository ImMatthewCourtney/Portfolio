import pandas as pd
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load your credentials from the credentials.json file
credentials = service_account.Credentials.from_service_account_file("credentials.json")

# The ID and range of a sample spreadsheet.
sheet_id = "XXXXXXXXXXXXXX"  # Replace with the ID of your Google Sheet
range_name = "A5"  # Update the starting cell if necessary

# Load the CSV files into pandas DataFrames
prizePicks = pd.read_csv('prizePicks_nba.csv', header=None)
pinnacle = pd.read_csv('pinnacle_nba.csv', header=None)
draftkings = pd.read_csv('draftkings_nba.csv', header=None)

# Define the column names
ppcolumn_names = ["Sport", "Name", "Category", "PrizePicks Line"]
column_names = ["Name", "Category", "Over", "Over_Line", "Over_Odds", "Over_%_to_Hit", "Under", "Under_Line", "Under_Odds", "Under_%_to_Hit"]

# Assign the column names to the DataFrame
prizePicks.columns = ppcolumn_names
pinnacle.columns = column_names
draftkings.columns = column_names


def find_matching_rows(prizePicks_row, df):
    return df[(df['Name'] == prizePicks_row['Name']) & (df['Category'] == prizePicks_row['Category'])]

merged_data = pd.DataFrame(columns=["Name", "Type", "Category", "PrizePicks Line", "Line_Value", "Pinnacle Odds", "DraftKings Odds", "Avg_Odds", "No_Vig_Fair_Value"])

for _, pp_row in prizePicks.iterrows():
    pinnacle_row = find_matching_rows(pp_row, pinnacle)
    draftkings_row = find_matching_rows(pp_row, draftkings)

    for line_type in ["Over", "Under"]:
        line_key = f"{line_type}_Line"
        odds_key = f"{line_type}_Odds"
        hit_key = f"{line_type}_%_to_Hit"

        if not pinnacle_row.empty:
            p_row = pinnacle_row.iloc[0]
            pin_odds = p_row[odds_key]
            pin_hit = float(p_row[hit_key])
            line_value = p_row[line_key]
        else:
            pin_odds = None
            pin_hit = None

        if not draftkings_row.empty:
            dk_row = draftkings_row.iloc[0]
            dk_odds = dk_row[odds_key]
            dk_hit = float(dk_row[hit_key])
            line_value = dk_row[line_key]
        else:
            dk_odds = None
            dk_hit = None

        if pin_odds is not None and dk_odds is not None:
            avg_odds = (pin_odds + dk_odds) / 2
        elif pin_odds is not None:
            avg_odds = pin_odds
        else:
            avg_odds = dk_odds

        if avg_odds is not None:
            probability = round(100 * (abs(avg_odds) / (abs(avg_odds) + 100)), 2)
            # probability = str(probability) + "%"  
        else:
            probability = None

        if pin_hit is not None and dk_hit is not None:
            avg_hit = (pin_hit + dk_hit) / 2
        elif pin_hit is not None:
            avg_hit = pin_hit
        else:
            avg_hit = dk_hit

        if pin_odds is not None or dk_odds is not None:
            new_row = pd.DataFrame([{
                "Name": pp_row["Name"],
                "Type": line_type,
                "Category": pp_row["Category"],
                "PrizePicks Line": pp_row["PrizePicks Line"],
                "Line_Value": line_value,
                "Pinnacle Odds": pin_odds,
                "DraftKings Odds": dk_odds,
                "Avg_Odds": avg_odds,
                "No_Vig_Fair_Value": probability,  # Add the No_Vig_Fair_Value column here
            }])
            merged_data = pd.concat([merged_data, new_row], ignore_index=True)

# Sort the merged_data DataFrame by %_to_Hit in descending order
sorted_data = merged_data.sort_values(by="Avg_Odds", ascending=True).reset_index(drop=True)

def create_google_sheet(sheet_name, credentials):
    try:
        service = build('sheets', 'v4', credentials=credentials)
        spreadsheet = {
            'properties': {
                'title': sheet_name
            }
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet,
                                                     fields='spreadsheetId').execute()
        print(f'Spreadsheet ID: {spreadsheet.get("spreadsheetId")}')
        return spreadsheet.get('spreadsheetId')
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def clear_data_below_header(sheet_id, sheet_range, credentials):
    try:
        service = build('sheets', 'v4', credentials=credentials)

        # Use the clear method to clear the data below the header row
        result = service.spreadsheets().values().clear(spreadsheetId=sheet_id, range=sheet_range).execute()
        print(f'{result.get("clearedRange")} has been cleared.')

    except HttpError as error:
        print(f'An error occurred: {error}')

def append_data_to_sheet(sheet_id, range_name, data, credentials):
    try:
        service = build('sheets', 'v4', credentials=credentials)

        body = {
            'range': range_name,
            'values': data
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=sheet_id, range=range_name,
            valueInputOption='RAW', insertDataOption='INSERT_ROWS', body=body).execute()
        print(f'{result.get("updates").get("updatedCells")} cells appended.')

    except HttpError as error:
        print(f'An error occurred: {error}')

def get_first_sheet_id(sheet_id, credentials):
    try:
        service = build('sheets', 'v4', credentials=credentials)
        result = service.spreadsheets().get(spreadsheetId=sheet_id).execute()
        sheets = result.get('sheets', [])
        first_sheet = sheets[0] if len(sheets) > 0 else None
        return first_sheet['properties']['sheetId'] if first_sheet else None
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def update_formatting(sheet_id, range_name, first_sheet_id, credentials):
    try:
        service = build('sheets', 'v4', credentials=credentials)

        # Set the background color to white and text color to black
        cell_format = {
            "backgroundColor": {
                "red": 225,
                "green": 225,
                "blue": 225
            },
            "textFormat": {
                "foregroundColor": {
                    "red": 1,
                    "green": 1,
                    "blue": 1
                }
            }
        }

        # Create a repeatCell request to update the formatting
        repeat_cell_request = {
            "repeatCell": {
                "range": {
                    "sheetId": first_sheet_id,
                    "startRowIndex": 4,
                    "startColumnIndex": 0,
                    "endColumnIndex": 9
                },
                "cell": {
                    "userEnteredFormat": cell_format
                },
                "fields": "userEnteredFormat(backgroundColor,textFormat)"
            }
        }

        # Create an updateDimensionProperties request to set the default row height
        row_height_request = {
            "updateDimensionProperties": {
                "range": {
                    "sheetId": first_sheet_id,
                    "dimension": "ROWS",
                    "startIndex": 4,
                    "endIndex": 4 + len(data_to_append) - 1  # Adjust endIndex based on the number of rows to format
                },
                "properties": {
                    "pixelSize": 21  # Set the default row height (in pixels)
                },
                "fields": "pixelSize"
            }
        }

        conditional_format_rule = {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": first_sheet_id,
                            "startRowIndex": 4,
                            "startColumnIndex": 3,  # 0-based index for column D
                            "endColumnIndex": 5     # 0-based index for column E (exclusive)
                        }
                    ],
                    "booleanRule": {
                        "condition": {
                            "type": "CUSTOM_FORMULA",
                            "values": [
                                {
                                    "userEnteredValue": "=IF(AND($D5=\"\", $E5=\"\"), FALSE, $D5=$E5)"
                                }
                            ]
                        },
                        "format": {
                            "backgroundColor": {
                                "red": 0,
                                "green": 0,
                                "blue": 50
                            },
                            "textFormat": {
                                "bold": True
                            }
                        }
                    }
                },
                "index": 0
            }
        }
        color_scale_format_rule = {
            "addConditionalFormatRule": {
                "rule": {
                    "ranges": [
                        {
                            "sheetId": first_sheet_id,
                            "startRowIndex": 4,
                            "startColumnIndex": 8,  # 0-based index for column I
                            "endColumnIndex": 9     # 0-based index for column J (exclusive)
                        }
                    ],
                    "gradientRule": {
                        "minpoint": {
                            "color": {
                                "red": 1,
                                "green": 0,
                                "blue": 0
                            },
                            "type": "NUMBER",
                            "value": "50"
                        },
                        "midpoint": {
                            "color": {
                                "red": 0,
                                "green": 0,
                                "blue": 0
                            },
                            "type": "NUMBER",
                            "value": "54.25"
                        },
                        "maxpoint": {
                            "color": {
                                "red": 0.2,
                                "green": 0,
                                "blue": 0.4
                            },
                            "type": "NUMBER",
                            "value": "60"
                        }
                    }
                },
                "index": 1
            }
        }
        
        # Execute the requests
        result = service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id, body={"requests": [repeat_cell_request, row_height_request, conditional_format_rule, color_scale_format_rule]}).execute()


    except HttpError as error:
        print(f'An error occurred: {error}')

# Convert the sorted_data DataFrame to a list of lists, including the header
data_to_append = [sorted_data.columns.tolist()] + sorted_data.values.tolist()

# Set the range to clear the data below the header row
clear_range = "A5:I"  # Adjust the column range (Z) if needed

# Clear the data below the header row
clear_data_below_header(sheet_id, clear_range, credentials)

first_sheet_id = get_first_sheet_id(sheet_id, credentials)
if first_sheet_id is None:
    print("Could not get the sheetId of the first sheet.")
else:
    # Append the data without the header row
    append_data_to_sheet(sheet_id, range_name, data_to_append[1:], credentials)

    # Update the formatting of the appended data
    update_formatting(sheet_id, range_name, first_sheet_id, credentials)

    print("The sorted data has been added to the Google Sheet with the desired formatting.")