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
print("iFormBuilder Lookup Form Syncer")
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
    #config_fn = 'settings_o.ini'
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
        ## Parse Form options
        # CSV file name
        try:
            self.csv_in = config.get("Form", "csv_in")
            if os.path.exists(os.path.join(cur_dir, self.csv_in)) != True:
                sys.exit(("Input CSV file could not be found. "
                          "File must be located in same directory as program."))
        except Exception as e:
            sys.exit("INI file is missing csv_in option.")
        # Form name
        try:
            self.form_name = config.get("Form", "form_name")
        except Exception as e:
            sys.exit("INI file is missing form_name option.")
        # Form label
        try:
            self.form_label = config.get("Form", "form_label")
        except Exception as e:
            sys.exit("INI file is missing form_label option.")
        # Form field length
        try:
            self.field_length = config.getint("Form", "field_length")
        except:
            sys.exit("INI file is missing field_length option.")
        # Optional unique identifier column
        try:
            self.uid_col = config.get("Form", "uid_col")
            self.has_uid = True
        except:
            self.has_uid = False
        # Optional update flag
        try:
            if self.has_uid:
                self.update = config.getboolean("Form", "update")
        except:
            pass
        # Optional delete flag
        try:
            if self.has_uid:
                self.delete = config.getboolean("Form", "delete")
        except:
            pass

def reserved_dcn_check(dcns):
    # List of reserved column names in IFB
    reserved_names = ['abort', 'absolute', 'access', 'action', 'add', 'after', 'all', 'allocate', 'alter', 'analyse', 'analyze', 'and', 'any', 'are', 'array', 'as', 'asc', 'asensitive', 'assertion', 'asymmetric', 'at', 'atomic', 'attach', 'audit', 'authorization', 'autoincrement', 'avg', 'before', 'begin', 'between', 'bigint', 'binary', 'bit', 'bit_length', 'blob', 'boolean', 'both', 'breadth', 'by', 'call', 'called', 'cascade', 'cascaded', 'case', 'cast', 'catalog', 'change', 'char', 'char_length', 'character', 'character_length', 'check', 'class', 'client_id', 'clob', 'close', 'cluster', 'coalesce', 'collate', 'collation', 'column', 'comment', 'commit', 'compress', 'condition', 'conflict', 'connect', 'connection', 'constraint', 'constraints', 'constructor', 'contains', 'continue', 'convert', 'corresponding', 'count', 'create', 'cross', 'cube', 'current', 'current_date', 'current_default_transform_group', 'current_path', 'current_role', 'current_time', 'current_timestamp', 'current_transform_group_for_type', 'current_user', 'cursor', 'cycle', 'data', 'database', 'databases', 'date', 'day', 'day_hour', 'day_microsecond', 'day_minute', 'day_second', 'deallocate', 'dec', 'decimal', 'declare', 'default', 'deferrable', 'deferred', 'delayed', 'delete', 'depth', 'deref', 'desc', 'describe', 'descriptor', 'detach', 'deterministic', 'diagnostics', 'disconnect', 'distinct', 'distinctrow', 'div', 'do', 'domain', 'double', 'drop', 'dual', 'dynamic', 'each', 'element', 'else', 'elseif', 'enclosed', 'end', 'equals', 'escape', 'escaped', 'except', 'exception', 'exclusive', 'exec', 'execute', 'exists', 'exit', 'explain', 'external', 'extract', 'fail', 'FALSE', 'fetch', 'file', 'filter', 'first', 'float', 'float4', 'float8', 'for', 'force', 'foreign', 'found', 'free', 'freeze', 'from', 'full', 'fulltext', 'function', 'general', 'get', 'glob', 'global', 'go', 'goto', 'grant', 'group', 'grouping', 'handler', 'having', 'high_priority', 'hold', 'hour', 'hour_microsecond', 'hour_minute', 'hour_second', 'id', 'identified', 'identity', 'if', 'ignore', 'ilike', 'immediate', 'in', 'increment', 'index', 'indexed', 'indicator', 'infile', 'initial', 'initially', 'inner', 'inout', 'input', 'insensitive', 'insert', 'instead', 'int', 'int1', 'int2', 'int3', 'int4', 'int8', 'integer', 'intersect', 'interval', 'into', 'is', 'isnull', 'isolation', 'iterate', 'join', 'key', 'keys', 'kill', 'language', 'large', 'last', 'lateral', 'leading', 'leave', 'left', 'level', 'like', 'limit', 'lines', 'load', 'local', 'localtime', 'localtimestamp', 'locator', 'location', 'lock', 'long', 'longblob', 'longtext', 'loop', 'low_priority', 'lower', 'map', 'match', 'max', 'maxextents', 'mediumblob', 'mediumint', 'mediumtext', 'member', 'merge', 'method', 'middleint', 'min', 'minus', 'minute', 'minute_microsecond', 'minute_second', 'mlslabel', 'mod', 'mode', 'modifies', 'modify', 'module', 'month', 'multiset', 'names', 'national', 'natural', 'nchar', 'nclob', 'new', 'next', 'no', 'no_write_to_binlog', 'noaudit', 'nocompress', 'none', 'not', 'notnull', 'nowait', 'null', 'nullif', 'number', 'numeric', 'object', 'octet_length', 'of', 'off', 'offline', 'offset', 'old', 'on', 'online', 'only', 'open', 'optimize', 'option', 'optionally', 'or', 'order', 'ordinality', 'out', 'outer', 'outfile', 'output', 'over', 'overlaps', 'pad', 'parameter', 'partial', 'partition', 'path', 'pctfree', 'placing', 'plan', 'position', 'pragma', 'precision', 'prepare', 'preserve', 'primary', 'prior', 'privileges', 'procedure', 'public', 'purge', 'query', 'raid0', 'raise', 'range', 'raw', 'read', 'reads', 'real', 'recursive', 'ref', 'references', 'referencing', 'regexp', 'reindex', 'relative', 'release', 'rename', 'repeat', 'replace', 'require', 'resignal', 'resource', 'restrict', 'result', 'return', 'returns', 'revoke', 'right', 'rlike', 'role', 'rollback', 'rollup', 'routine', 'row', 'rowid', 'rownum', 'rows', 'savepoint', 'scale', 'schema', 'schemas', 'scope', 'scroll', 'search', 'second', 'second_microsecond', 'section', 'select', 'sensitive', 'separator', 'sequence', 'session', 'session_user', 'set', 'sets', 'share', 'show', 'signal', 'similar', 'size', 'smallint', 'some', 'soname', 'space', 'spatial', 'specific', 'specifictype', 'sql', 'sql_big_result', 'sql_calc_found_rows', 'sql_small_result', 'sqlcode', 'sqlerror', 'sqlexception', 'sqlstate', 'sqlwarning', 'ssl', 'start', 'starting', 'state', 'static', 'straight_join', 'submultiset', 'substring', 'successful', 'sum', 'symmetric', 'synonym', 'sysdate', 'system', 'system_user', 'table', 'tablesample', 'temp', 'temporary', 'terminated', 'then', 'time', 'timestamp', 'timezone_hour', 'timezone_minute', 'tinyblob', 'tinyint', 'tinytext', 'to', 'trailing', 'transaction', 'translate', 'translation', 'treat', 'trigger', 'trim', 'TRUE', 'type', 'uid', 'under', 'undo', 'union', 'unique', 'unknown', 'unlock', 'unnest', 'unsigned', 'until', 'update', 'upgrade', 'upper', 'usage', 'use', 'user', 'using', 'utc_date', 'utc_time', 'utc_timestamp', 'vacuum', 'validate', 'value', 'values', 'varbinary', 'varchar', 'varchar2', 'varcharacter', 'varying', 'verbose', 'view', 'virtual', 'void', 'when', 'whenever', 'where', 'while', 'window', 'with', 'within', 'without', 'work', 'write', 'x509', 'xor', 'year', 'year_month', 'zerofill', 'zone', 'created_date', 'created_by', 'created_location', 'created_device_id', 'modified_date', 'modified_by', 'modified_location', 'modified_device_id', 'parent_record_id', 'parent_page_id', 'parent_element_id']
    # Check dcns in reserved names
    reserved = [dcn for dcn in dcns if dcn in reserved_names]
    # If no reserved, exit function
    if len(reserved) == 0:
        return 1
    # Message and exit program
    else:
        print("ERROR: Input CSV contains column names that are iFormBuilder reserved names.")
        print("The following column names are reserved:")
        for r in reserved:
            print("     %s" % r)
        sys.exit()

# Loads CSV to Pandas dataframe
def load_csv(csv_in):
    # Read CSV
    df = pd.read_csv(os.path.join(cur_dir, csv_in), na_filter = False)
    # All columns to string
    df = df.astype(str)
    # Cleanup messy column names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('[^\w\s]','')
    # Truncate data to field length
    for col in df.columns:
        df[col] = df[col].str[:s.field_length]
    # Check for reserved column names
    reserved_dcn_check(df.columns)
    return df

# Converts a dataframe to the IFB format for inserting records
def df_to_ifb(df):
    dcns = list(df.columns)
    parsed = list()
    for index, row in df.iterrows():
        flds = list()
        for dcn in dcns:
            flds.append({'element_name': dcn, 'value': row[dcn]})
        parsed.append({'fields': flds})
    return parsed

# Converts a dataframe to the IFB format for updating records
def df_to_ifb_u(df):
    dcns = list(df.columns)
    if 'id' not in dcns:
        sys.exit("ERROR: id column is missing from update data.")
    parsed = list()
    for index, row in df.iterrows():
        flds = list()
        for dcn in dcns:
            if dcn == 'id':
                continue
            flds.append({'element_name': dcn, 'value': row[dcn]})
        parsed.append({'id': row['id'], 'fields': flds})
    return parsed

# Converts a dictionary of IFB records to a Pandas df
def ifb_to_df(ifb_dict):
    # Get field names from keys of first record
    flds = ifb_dict[0].keys()
    # Blank dictionary
    df_dict = {}
    # For each key, make a list of all the data for that field and append to dict
    for fld in flds:
        df_dict[fld] = [record[fld] for record in ifb_dict]
    # Make dict df
    df = pd.DataFrame.from_dict(df_dict)
    return df

# Send a dataframe of records to IFB, in chunks if over the API limit
def send_records(df, api, settings):
    # If less than 1000 records push all
        if len(df.index) < 1000:
            api.createRecords(settings.profile_id, settings.page_id,
                                body = df_to_ifb(df))
        # Else push records in chunks
        else:
            nrow = len(df.index)
            # Iterate over in chunks of 999
            print("More than 1000 rows in data, uploading in chunks...")
            start = 0
            end = 999
            while True:
                if end > nrow - 1:
                    end = nrow - 1
                print("     Uploading rows %s to %s..." % (start + 1, end + 1))
                api.createRecords(settings.profile_id, settings.page_id,
                                    body = df_to_ifb(df[start:end + 1]))
                if end == nrow - 1:
                    break
                start += 1000
                end += 1000


def main():
    # Counter for total API calls used
    calls = 0
    # Parse INI file
    print("Parsing INI...")
    global s
    s = settings()
    # Get token for IFB API
    print("Connecting to iFormBuilder API")
    try:
        api = IFB(s.server_name + ".iformbuilder.com", s.ifb_key, s.ifb_secret)
    except:
        sys.exit(("ERROR: Could not connect to the IFB API. This is likely due to"
                    "invalid credentials or no internet connection."))
    calls += 1
    # Load CSV file
    print("Loading CSV file %s" % (s.csv_in))
    df = load_csv(s.csv_in)
    # Data column name list
    dcns = list(df.columns)
    # Get list of all pages
    page_list_dict = api.readPages(profile_id = s.profile_id)
    calls += 1
    page_list = [page['name'] for page in page_list_dict]
    # If form name does not yet exist, create it
    if s.form_name not in page_list:
        # Create form
        print("Creating new page %s." % (s.form_name))
        s.page_id = api.createPage(profile_id = s.profile_id,
            body = {'name': s.form_name, 'label': s.form_label})['id']
        calls += 1
        if s.page_id <= 0:
            sys.exit("ERROR: Could not create new page %s" % (s.form_name))
        # Add fields to page
        body = [{'name': col, 'label': col, 'data_type': 1, 'data_size': s.field_length} for col in dcns]
        api.createElements(s.profile_id, page_id, body)
        calls += 1
    else:
        # Get page ID from page_list_dict
        for page in page_list_dict:
            if page['name'] == s.form_name:
                s.page_id = page['id']
                break
        # If no uid_col, delete all records from the existing page
        if s.has_uid == False:
            print("No unique ID column provided, all records in form will be overwritten.")
            api.deleteAllRecords(s.profile_id, s.page_id)
            calls += 1
    # List the fields in the form
    element_dict = api.readElements(s.profile_id, s.page_id)
    calls += 1
    element_list = [element['name'] for element in element_dict]
    # Check that all fields in input data are in destination form
    missing_flds = [dcn for dcn in dcns if dcn not in element_list]
    if len(missing_flds) > 0:
        print(("WARNING: not all fields in input CSV have a match in the destination page."
                "The following fields will not be loaded:"))
        for fld in missing_flds:
            print("     %s" % fld)
    # Now push all records to form
    print("Pushing records to form...")
    # If UID col is present in settings
    if s.has_uid:
        # Check that uid columns in in df columns in in IFB page
        if s.uid_col not in dcns:
            sys.exit("ERROR: Unique ID column %s is missing from input data." % s.uid_col)
        if s.uid_col not in element_list:
            sys.exit("ERROR: Unique ID column %s is missing from source IFB page." % s.uid_col)
        # Check that values in uid column are unique
        source_uids = df[s.uid_col].tolist()
        if len(source_uids) != len(set(source_uids)):
            sys.exit("ERROR: Unique ID column %s contains duplicate values." % s.uid_col)
        ## Get all records from API
        # Collapse IFB elements to comma sep list for API call
        flds = ','.join([str(element) for element in element_list])
        # Get all records
        ifb_records = api.readAllRecords(s.profile_id, s.page_id, grammar = 'id,' + flds)
        calls += 1
        # List of unique IDs in IFB
        ifb_uids = [record[s.uid_col] for record in ifb_records]
        # Append records in df not in IFB
        append = df[~df[s.uid_col].isin(ifb_uids)]
        if len(append.index) > 0:
            print("     Appending %s new records..." % len(append.index))
            send_records(df = append, api = api, settings = s)
            calls += math.floor(len(append.index) / 1000)
        # If update, find records in df different than in IFB and send update
        if s.update:
            # IFB records to pd
            ifb_records_df = ifb_to_df(ifb_records)
            # First find matches on all columns between df and ifb_records
            same = pd.merge(df, ifb_records_df[dcns], on = dcns)
            # The unique IDs that are not in the same df but are in the IFB and
            # source data are the ones to update
            same_uids = same[s.uid_col].tolist()
            diff_uids = list(set(source_uids) - set(same_uids))
            # Then filter source df by these unique ids
            update = df[df[s.uid_col].isin(diff_uids)]
            # Then inner join to IFB records to get record ID and remove records
            # that are not in IFB
            update_df = pd.merge(update, ifb_records_df[['id', s.uid_col]], on = s.uid_col)
            if len(update_df.index) > 0:
                print("     Updating %s records..." % len(update.index))
                api.updateAllRecords(s.profile_id, s.page_id, body = df_to_ifb_u(update_df))
                calls += math.floor(len(update_df.index) / 1000)
        # If delete, get records in IFB not in df and delete
        if s.delete:
            del_ids = [ifb_records[i]['id'] for i in range(0, len(ifb_records)) if ifb_records[i][s.uid_col] not in df[s.uid_col].tolist()]
            if len(del_ids) > 0:
                print("     Deleting %s records..." % len(del_ids))
                for del_id in del_ids:
                    api.deleteRecord(s.profile_id, s.page_id, del_id)
                    calls += 1
    # Else push ALL records
    else:
        send_records(df, api, s)
        calls += math.floor(len(df.index) / 1000)
    # Complete
    print("Syncing complete. Syncing used %s API calls." % calls)

if __name__ == '__main__':
    main()

