## Introduction

The program provides a simple way to sync multiple option lists contained in a CSV file with an iFormBuilder profile. The intended use case is creating and updating option lists programmatically. While the iFormBuilder website provides a GUI for uploading CSV files to option lists, the only automated way to sync option lists is through the iFormBuilder API. To date, a number of wrappers have been created around the iFormBuilder API, such as:

	- [ifb-wrapper](https://github.com/jhsu98/ifb-wrapper) by Jonathan Hsu of Zerion Software provides a Python interface. This wrapper is used by this program.
	- [iformr](https://github.com/bdevoe/iformr) by Are Strom and Bill DeVoe provides an R interface, including functions for syncing forms and option lists.

However, all of these options require some ability in a given program language and also have dependencies that must be installed. As such, this project aims to package a option list syncing procedure as a stand-alone binary for ease of use.

## License

This program is distributed freely under an MIT license by Bill DeVoe. 

## Directory contents

- `ifb_list_syncer.exe` - Windows executable, compiled using PyInstaller for Windows 10 x64.
- `ifb_list_syncer.py` - source code in Python 3.7.
- `settings.ini` - example configuration file, using all settings.
- `ifb_list_syncer.bat` - An example batch file used to call the program.
- `README.md` - This file; documentation in Markdown format.

## Usage

### Overview

The input CSV file contains one or more option lists. Each option list is created if it does not yet exist. Options not present in the destination option list are added. Options already in the option list based on a matching `key_value` are updated if any of the other attributes (`label`, `sort_order`, or `condition_value`) are different in the source CSV.

No delete option is provided, as deleting options could adversely impact existing data. It is recommended that options no longer needed are disabled by setting the `condition_value` to `false` (or any statement that does not evaluate as `true`).

### Input CSV file

The input CSV file containing one or more option lists must contain the following fields:

- `name` - The name for each option list; this will repeat for each option within the list.
- `key_value` - The key value of each option within the list. These values must be unique for each unique `name`, or an error will be produced. Key values should contain no whitespace or special characters. The program will attempt to reformat any key values meeting this criteria.
- `label` - The label for each option.
- `sort_order` - The sort order for options within each unique `name` list. The sort order does not need to be zero-indexed or sequential, but each `sort_order` value must be unique within the list. For example, sort order values of `1, 3, 4, 6` for an option list would be valid and would create a sort order in the destination option list of `0, 1, 2, 3`. However, a sort order of `1, 1, 2, 3` would produce an error.
- `condition_value` - Any conditional logic to be applied to each option.

### Configuration file

The program is controlled by an external INI configuration file. The example `settings.ini` file includes comments for each of these options. 

### Program execution

The executable file `ifb_list_syncer.exe` requires two command line arguments:
	1 - The directory containing the input INI file.
	2 - The filename of the input INI file.

The included batch file `ifb_list_syncer.BAT` demonstrates how to call the executable, using the `%CD%` variable to dynamically retrieve the current program directory. A `pause` statement is also included to prevent the console window from closing, allowing the viewer to observe the program feedback. If placing this batch file on Task Scheduler, removing the `pause` statement is recommended.

## API Consumption

The number of API calls used by this program is as follows:

	- Each time the program runs:
		- 1 call to generate an API access token.
		- 1 call to get a list of all option lists in the profile.
	- For each unique option list:
		- If the program needs to create a new option list:
			- 1 call to create a new option list.
			- 1 call per 1000 options added to the option list.
		- Else if the option list already exists:
			- 1 call per 1000 options added to the option list.
			- 1 call per 1000 options updated in the option list.

The number of API calls used is reported in the console each time the program runs.