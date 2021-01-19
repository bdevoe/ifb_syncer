#-------------------------------------------------------------------------------
# Name:        ifb_form_syncer
# Purpose:     Syncs an input CSV to iFormBuilder page for use in lookup tables.
#
# Author:      Bill DeVoe, Maine Department of Marine Resources
#
# Created:     09/22/2020
# Copyright:   (c) Bill DeVoe 2020
# License:     MIT
#-------------------------------------------------------------------------------
from ifb import IFB
import configparser
import pandas as pd
import os
import sys
import math

print()
print("-----------------------------------------------------------------------")
print("iFormBuilder Option List Syncer")
print("Created by Bill DeVoe, 2020. Distributed under MIT License")
print("For questions, see the included documentation.")
print("Contact: william.devoe@maine.gov or bdevoe@gmail.com")
print("-----------------------------------------------------------------------")
print()

# Get current directory from command line
try:
    cur_dir = sys.argv[1]
    #cur_dir = os.path.dirname(__file__)
except:
    sys.exit(("The program directory was either not provided or does not exist."
    "Please provide program directory as command line argument."))

if os.path.exists(cur_dir):
    print("Running from directory: %s" % (os.path.basename(cur_dir)))
else:
    sys.exit(("The program directory was either not provided or does not exist."
    "Please provide program directory as command line argument."))

try:
    config_fn = sys.argv[2]
    #config_fn = 'settings.ini'
except:
    config_fn = "config.ini"
    print("Config file name not provided, defaulting to config.ini...")

# Class handler to parse INI file
class settings():
    def __init__(self):
        configfile = os.path.join(cur_dir, config_fn)
        if os.path.exists(configfile) != True:
            sys.exit(("Configuration file could not be found. "
                "File must be located in same directory as program."))
        # Read INI file
        config = configparser.ConfigParser()
        config.read(configfile)
        ## API Options
        # Server Name
        try:
            self.server_name = config.get("API", "server_name")
        except Exception as e:
            print(e)
            sys.exit("INI file is missing server_name option.")
        # Profile ID
        try:
            self.profile_id = config.getint("API", "profile_id")
        except:
            sys.exit("INI file is missing profile_id option.")
        # IFB API Key
        try:
            self.ifb_key = config.get("API", "ifb_key")
        except:
            sys.exit("INI file is missing ifb_key option.")
        # IFB API Secret
        try:
            self.ifb_secret = config.get("API", "ifb_secret")
        except:
            sys.exit("INI file is missing ifb_secret option.")
        ## Parse List options
        # CSV file name
        try:
            self.csv_in = config.get("List", "csv_in")
            if os.path.exists(os.path.join(cur_dir, self.csv_in)) != True:
                sys.exit(("Input CSV file could not be found. "
                          "File must be located in same directory as program."))
        except Exception as e:
            sys.exit("INI file is missing csv_in option.")
        # Update options
        try:
            self.update = config.getboolean("List", "update")
        except:
            self.update = True
            print("INI file is missing valid update option, defaulting to True...")

# Loads CSV to Pandas dataframe
def load_csv(csv_in):
    # Read CSV
    df = pd.read_csv(os.path.join(cur_dir, csv_in), na_filter = False)
    # All columns to string
    df = df.astype(str)
    # Check that column names are correct
    req_cols = ['name', 'key_value', 'label', 'sort_order', 'condition_value']
    missing = [col for col in req_cols if col not in df.columns]
    if (len(missing) > 0):
        sys.exit("ERROR: Input CSV is missing one or more required columns:")
        for m in missing:
            print("     %s" % m)
    # Format option list names and key values
    df['name'] = df['name'].str.strip().str.lower().str.replace(' ', '_').str.extract('(\w+)', expand = False)
    df['key_value'] = df['key_value'].str.strip().str.replace(' ', '_').str.extract('(\w+)', expand = False)
    return df

# Sends new options to IFB
def send_options(options, option_list_id, api, settings):
    # Organize options df into list of dicts
    body = list()
    for index, row in options.iterrows():
        body.append({'key_value': row['key_value'], 'label': row['label'],
                        'sort_order': row['sort_order'], 'condition_value': row['condition_value']})
    api.createOptions(settings.profile_id, option_list_id, body)

# Retrieves options from option list as pandas df
def retrieve_options(option_list_id, api, settings):
    ## Get options from API
    # List of fields for options needed, collapse to comma sep list for grammar
    flds = ['id', 'key_value', 'label', 'sort_order', 'condition_value']
    flds_str = ','.join([str(fld) for fld in flds])
    options = api.readAllOptions(settings.profile_id, option_list_id, grammar = flds_str)
    # Blank dictionary
    df_dict = {}
    # For option field, make a list of all the data for that field and append to dict
    for fld in flds:
        df_dict[fld] = [option[fld] for option in options]
    # Make dict df
    df = pd.DataFrame.from_dict(df_dict)
    # Replace NAs
    df = df.fillna('')
    return df

# Updates options from input options as pandas df
def send_update(options, option_list_id, api, settings):
    # Organize options df into list of dicts
    body = list()
    for index, row in options.iterrows():
        body.append({'id': row['id'], 'key_value': row['key_value'], 'label': row['label'],
                'sort_order': row['sort_order'], 'condition_value': row['condition_value']})
    # Submit update
    api.updateOptions(settings.profile_id, option_list_id, body)

# Main program
def main():
    # Counter for total API calls used
    calls = 0
    # Parse INI file
    print("Parsing INI...")
    global s
    s = settings()
    # Get token for IFB API
    print("Connecting to iFormBuilder API...")
    try:
        api = IFB(s.server_name + ".iformbuilder.com", s.ifb_key, s.ifb_secret)
    except:
        sys.exit(("ERROR: Could not connect to the IFB API. This is likely due to"
                    "invalid credentials or no internet connection."))
    calls += 1
    # Get all the option lists in the profile
    print("Retrieving all option lists in profile...")
    all_lists = api.readAllOptionLists(s.profile_id)
    all_names = [op['name'] for op in all_lists]
    all_ids = [op['id'] for op in all_lists]
    calls += math.floor(len(all_lists) / 100)
    # Load CSV file
    print("Loading CSV file %s" % (s.csv_in))
    df = load_csv(s.csv_in)
    # For each unique list names
    for op_list in sorted(set(df['name'].tolist())):
        # Subset option list data
        op_df = df[df['name'] == op_list]
        # Check that all keys are unique
        if len(op_df['key_value'].tolist()) != len(set(op_df['key_value'].tolist())):
            print("     ERROR: Option list %s contains duplicate key values, skipping..." % op_list)
            continue
        # Check that all sort orders are unique
        if len(op_df['sort_order'].tolist()) != len(set(op_df['sort_order'].tolist())):
            print("     ERROR: Option list %s contains duplicate sort order values, skipping..." % op_list)
            continue
        # Check if option list name already exists in profile
        if op_list in all_names:
            # Get the ID
            op_list_id = all_ids[all_names.index(op_list)]
            # Retrieve options, add _cur suffix
            cur_ops = retrieve_options(op_list_id, api, s).add_suffix('_cur')
            calls += math.floor(len(cur_ops.index) / 1000)
            ## Append new options
            append_df = op_df[~op_df['key_value'].isin(cur_ops['key_value_cur'].tolist())]
            if len(append_df.index) > 0:
                print("     Appending %s new options to list %s..." % (len(append_df.index), op_list))
                send_options(options = append_df, option_list_id = op_list_id, api = api, settings = s)
                calls += math.floor(len(append_df.index) / 1000)
            ## Update options
            if s.update:
                op_joined = pd.merge(op_df, cur_ops, left_on = 'key_value', right_on = 'key_value_cur')
                # Filter where cols not equal to find options to update
                diff_q = ('label != label_cur or sort_order != sort_order_cur'
                        ' or condition_value != condition_value_cur')
                update_df = (op_joined
                    .astype(str)
                    .query(diff_q)
                    .filter(['id_cur', 'key_value', 'label', 'sort_order', 'condition_value'])
                    .rename(columns = {'id_cur': 'id'}))
                # If any rows send update
                if len(update_df.index) > 0:
                    print("     Updating %s options in list %s..." % (len(update_df.index), op_list))
                    send_update(options = update_df, option_list_id = op_list_id, api = api, settings = s)
                    calls += math.floor(len(update_df.index) / 1000)
        else:
            # Create new option list
            print("     Creating new option list %s..." % op_list)
            op_list_id = api.createOptionList(s.profile_id, body = {'name': op_list})['id']
            # Check valid option list id
            if op_list_id == 0:
                print("     ERROR: Option list %s could not be created, skipping..." % op_list)
                continue
            # Push all options as new
            send_options(options = op_df, option_list_id = op_list_id, api = api, settings = s)
            calls += math.floor(len(op_df.index) / 1000)
    # Complete
    print("Syncing complete. Syncing used %s API calls." % calls)


if __name__ == '__main__':
    main()
