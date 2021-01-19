## Introduction

The program provides a simple way to sync the contents of a CSV file with an iFormBuilder page. The intended use case is updating and creating lookup tables. While the iFormBuilder website provides a GUI for uploading CSV files to forms, the only automated way to sync lookup tables is through the iFormBuilder API. To date, a number of wrappers have been created around the iFormBuilder API, such as:

	- [ifb-wrapper](https://github.com/jhsu98/ifb-wrapper) by Jonathan Hsu of Zerion Software provides a Python interface. This wrapper is used by this program.
	- [iformr](https://github.com/bdevoe/iformr) by Are Strom and Bill DeVoe provides an R interface, including functions for syncing forms and option lists.

However, all of these options require some ability in a given program language and also have dependencies that must be installed. As such, this project aims to package a form syncing procedure as a stand-alone binary for ease of use.

## License

This program is distributed freely under an MIT license by Bill DeVoe. 

## Directory contents

- `ifb_form_syncer.exe` - Windows executable, compiled using PyInstaller for Windows 10 x64.
- `ifb_form_syncer.py` - source code in Python 3.7.
- `settings.ini` - example configuration file, using all settings.
- `ifb_form_syncer.bat` - An example batch file used to call the program.
- `README.md` - This file; documentation in Markdown format.

## Usage

### Overview

The form name provided in the INI file should not be present in iFormBuilder the first time the program is run for a given form. 

During the first sync, the program will create the form name provided in the settings file and populate it with the fields from the input CSV file. The elements created in the new page will all be text elements, as is best practice for lookup tables. The element length will be set by the `field_length` setting in the INI file. Data in the input CSV longer than this value will be truncated.

On subsequent syncs, the created form will be synced with the input CSV using one of two methods:

	- The data in the source form is entirely deleted and overwritten with the new data. This is a good option for sporadic updates to a lookup table with completely different values. An example use case would be updating a lookup table with sample stations for a new season of field work, where the column names were the same but mostly new stations were being used. This option can be a poor choice for automatically scheduled updates, as it uses considerably more API calls.
	- The second option uses a provided unique identifier column to compare the CSV file data with the data currently in the iFormBuilder page and appends new data to iFormBuilder. It also optionally updates data already in iFormBuilder where the incoming data has different values for any field. Data in iFormBuilder not present in the incoming data can also be optionally deleted. This option is best used for recurring automatic updates. An example use case would be updating a lookup table of license holders from a CSV exported from an internal database nightly.

In both cases, if column names exist in the input CSV that do not have a match in the existing iFormBuilder form, a warning will be produced indicating that those fields will not be loaded.

### Input CSV file

The input CSV file containing data to sync with iFormBuilder should ideally contain column names formatted for use in iFormBuilder - no whitespace, punctuation, and all lowercase. The program will attempt to reformat column names not meeting this criteria. Column names that are reserved words in iFormBuilder will be detected and will produce an error. The reserved field names will be returned to the console by the program. For a list of iFormBuilder reserved words, see [here](https://iformbuilder.zendesk.com/hc/en-us/articles/201698530-Reserved-Words-What-words-cannot-be-used-as-data-column-names-)

### Configuration file

The program is controlled by an external INI configuration file. The example `settings.ini` file includes comments for each of these options. 

### Program execution

The executable file `ifb_form_syncer.exe` requires two command line arguments:
	1 - The directory containing the input INI file.
	2 - The filename of the input INI file.

The included batch file `ifb_form_syncer.BAT` demonstrates how to call the executable, using the `%CD%` variable to dynamically retrieve the current program directory. A `pause` statement is also included to prevent the console window from closing, allowing the viewer to observe the program feedback. If placing this batch file on Task Scheduler, removing the `pause` statement is recommended. Using a batch file also allows the program to be called multiple times to sync various forms using different INI inputs.

## API Consumption

The number of API calls used by this program is as follows:

	- Each time the program runs:
		- 1 call to generate an API access token.
		- 1 call to get a list of all pages in the profile.
		- 1 call to get a list of fields in the page.
	- If the program needs to create a new page:
		- 1 call to create a new page.
		- 1 call to add elements to the page.
	- If no unique ID column (overwriting the entire page):
		- 1 call to delete all records from the page.
		- 1 call per 1000 records appended to the page.
	- Else if using unique ID column:
		- 1 call per 1000 records appended to the page.
		- 1 call per 1000 records updated on the page.
		- 1 call per record deleted.

The number of API calls used is reported in the console each time the program runs.