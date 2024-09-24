# simple-llm-exporter
a tool to export entire scripts to a text file with a file tree and description, for exporting to llm's 

quick intro: use this command to export all files (determined by config in code)  that have been modified in the last 90 minutes, with a tree of the app, no description

``` python export.py --export-options 2,1,1,all --recent 90```

Or this to export all functions in a tree. 
```python export.py --export-options 0,1,0 --map-functions```

## Overview
The export.py script allows users to export selected files from a Flask project based on certain criteria like file types, modification time, and structure mapping. It can also map Python and JavaScript functions, classes, and methods for easier navigation. The output is stored in a text file, organized into sections like a project description, file tree, and content from specific file types.

    Include Description (choices[0])
        '1': Include the application's description in the output file.
        '0': Exclude the description.
    Include Project Structure Tree (choices[1])
        '1': Include a tree-like structure of the project's directories and files.
        '0': Exclude the project structure.
    Include All File Types (choices[2])
        '1': Include all default file types (all, py, js, md, txt, css, html, json, other).
        '0': Specify specific file types to include in choices[3].
    Specific File Types (choices[3])
        A comma-separated list of file types to include (e.g., 'py,js,md').
        Only used if choices[2] is '0'.

Default Export Options

The default value for --export-options is '1,1,1,all', which means:

    Include the description.
    Include the project structure tree.
    Include all default file types.

How the Code Parses Export Options

In the FileExporter class, the _parse_export_options method processes the export_options string:

    Split the Options: The string is split by commas into a list called choices.
    Validate Length: If the length of choices is less than 4, it defaults to '1,1,1,all'.
    Initialize file_types: A set that will contain the types of files to export.
    Process Each Choice:
        Choice 0: If '1', add 'description' to file_types.
        Choice 1: If '1', add 'tree' to file_types.
        Choice 2:
            If '1', add all default file types to file_types.
            If '0', use choices[3] to add specific file types to file_types.

Selecting Options for a Readme File

To customize what gets included in the readme file, you adjust the values in --export-options:

    Include Only Description and Tree:

    bash

--export-options '1,1,0,'

Include Only Python and JavaScript Files Without Description and Tree:

bash

--export-options '0,0,0,py,js'

Include Everything Except Other File Types:

bash

--export-options '1,1,1,all'

(Note: Since choices[2] is '1', choices[3] is ignored.)

## Requirements
- Python 3.6+
- Flask project with directories such as app and static

## Command Line Usage
The script supports several command line arguments to control what gets exported:

### Basic Usage
Export with default options:
```
python export.py
```

This will:

Export the project description
Include the file tree
Export all file types (.py, .js, .md, .html, .css, .json, .txt, and other files)

Output is stored in ./backups/exported_files_<timestamp>.txt.


### Export Options 
The --export-options flag allows you to control what gets exported.
Syntax:
```Copy--export-options <description>,<tree>,<file-types>,<specific-files>```
Each value is either 0 (disable) or 1 (enable). For example:

1,1,1,all: Export description, file tree, and all file types.
0,1,0: Skip description, export tree, and no file content.

Example 1: Export specific file types
Export project structure and only Python and JSON files:
```Copypython export.py --export-options 0,1,0,py,json```
Example 2: Full export with all file types
```Copypython export.py --export-options 1,1,1,all```
This exports:

Project description
File tree
All file types

###  Filtering by Recent Files
The --recent flag restricts the export to files modified in the last N minutes.
Example: Export files modified in the last 90 minutes
```Copypython export.py --recent 90```
Mapping Functions, Classes, and Methods
The --map-functions flag maps Python and JavaScript functions, classes, and methods in the export.
Example: Export with function and method mapping
```Copypython export.py --map-functions```
This will include a hierarchical view of functions, classes, and methods in Python and JavaScript files in the exported tree.
Output
The exported output file will include:

### Project Description (if enabled)
File Tree (if enabled)
File Content (if enabled), with sections for each file type or all files based on your options.

### Sub Folders 
You can export only specific subfolders / extensions using specific-path: 

 ``` python export.py --specific-path "app/models/*.py" --export-options 2,1,1,all ```

### Logs
The script will attempt to include the most recent log file from the logs/ directory if it exists. The log file must follow the naming pattern log_<timestamp>.txt.
Example Commands

Export the entire project tree with a description and all file types:

```Copypython export.py --export-options 1,1,1,all```

Export only Python and Markdown files from the last 60 minutes with function mapping:

```Copypython export.py --export-options 0,1,0,py,md --recent 60 --map-functions```

Export project description and structure without file content:

```Copypython export.py --export-options 1,1,0```
Conclusion
Use this script to easily export and map project files based on your needs. Customize the export options to filter by file type, time of last modification, or include a structured view of functions and methods in Python and JavaScript files.
