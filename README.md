# simple-llm-exporter
a tool to export entire scripts to a text file with a file tree and description, for exporting to llm's 

quick intro: use this command to export all files (determined by config in code)  that have been modified in the last 90 minutes, with a tree of the app, no description

``` python export.py --export-options 2,1,1,all --recent 90```

Or this to export all functions in a tree. 
```python export.py --export-options 0,1,0 --map-functions```

## Overview
The export.py script allows users to export selected files from a Flask project based on certain criteria like file types, modification time, and structure mapping. It can also map Python and JavaScript functions, classes, and methods for easier navigation. The output is stored in a text file, organized into sections like a project description, file tree, and content from specific file types.

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
