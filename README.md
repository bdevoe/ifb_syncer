## Introduction

These programs provide a simple way to sync the contents of a CSV file with an iFormBuilder page or iFormBuilder option lists. The intended use case is updating and creating lookup tables and option lists. While the iFormBuilder website provides a GUI for uploading CSV files to forms, the only automated way to sync lookup tables is through the iFormBuilder API. To date, a number of wrappers have been created around the iFormBuilder API, such as:

	- [ifb-wrapper](https://github.com/jhsu98/ifb-wrapper) by Jonathan Hsu of Zerion Software provides a Python interface. This wrapper is used by this program.
	- [iformr](https://github.com/bdevoe/iformr) by Are Strom and Bill DeVoe provides an R interface, including functions for syncing forms and option lists.

However, all of these options require some ability in a given program language and also have dependencies that must be installed. As such, this project aims to package form and option list syncing procedures as stand-alone binaries for ease of use.

`ifb_syncer` is written in Python 3.7 and complied with PyInstaller.

## License

This program is distributed freely under an MIT license by Bill DeVoe. 

## Directory contents

- [form_syncer](./form_syncer) - Directory containing `form_syncer` source code, executable, and examples.
- [option_list_syncer](./option_list_syncer) - Directory containing `option_list_syncer` source code, executable, and examples.

## Usage

See:
- [form_syncer README](./form_syncer/README.md) for form_syncer usage.
- [option_list_syncer README](./option_list_syncer/README.md) for option_list_syncer usage.