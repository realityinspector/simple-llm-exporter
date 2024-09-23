# export.py

import os
import argparse
from datetime import datetime
import subprocess
import logging
import delegator
import ast
import re


def create_tree(recent=None, map_functions=False):
    included_dirs = ['app', 'static']
    included_files = ['config.py', 'main.py']
    excluded_dirs = ['__pycache__', 'migrations', '.upm', '.pythonlibs']
    excluded_files = ['.gitignore', 'poetry.lock', '.png', '.jpg', '.jpeg']

    tree = {'root': []}
    current_time = datetime.now()

    for item in os.listdir():
        if os.path.isfile(item) and item in included_files:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(item))
            if recent is None or (current_time -
                                  file_mtime).total_seconds() <= recent * 60:
                tree['root'].append(item)
        elif os.path.isdir(item) and item in included_dirs:
            for root, dirs, files in os.walk(item):
                dirs[:] = [d for d in dirs if d not in excluded_dirs]
                files = [
                    f for f in files if f not in excluded_files
                    and not f.endswith(('.png', '.jpg', '.jpeg'))
                ]

                relative_dir = os.path.relpath(root, start='.')
                if relative_dir not in tree:
                    tree[relative_dir] = []

                for file in files:
                    file_path = os.path.join(root, file)
                    file_mtime = datetime.fromtimestamp(
                        os.path.getmtime(file_path))
                    if recent is None or (current_time - file_mtime
                                          ).total_seconds() <= recent * 60:
                        tree[relative_dir].append(file)

    log_dir = 'logs'
    if os.path.isdir(log_dir):
        log_files = [
            f for f in os.listdir(log_dir)
            if f.startswith('log_') and f.endswith('.txt')
        ]
        if recent is not None:
            log_files = [
                f for f in log_files if (current_time - datetime.fromtimestamp(
                    os.path.getmtime(os.path.join(log_dir, f)))
                                         ).total_seconds() <= recent * 60
            ]
        if log_files:
            most_recent_log = max(
                log_files,
                key=lambda f: os.path.getmtime(os.path.join(log_dir, f)))
            if 'logs' not in tree:
                tree['logs'] = []
            tree['logs'].append(most_recent_log)

    if map_functions:
        tree = map_functions_to_tree(tree)

    return tree


def map_functions_to_tree(tree):
    for directory, files in tree.items():
        mapped_files = []
        for file in files:
            file_path = os.path.join(directory,
                                     file) if directory != 'root' else file
            if file.endswith('.py'):
                mapped_files.append({file: extract_python_elements(file_path)})
            elif file.endswith('.js'):
                mapped_files.append({file: extract_js_elements(file_path)})
            else:
                mapped_files.append(file)
        tree[directory] = mapped_files
    return tree


def extract_python_elements(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    tree = ast.parse(content)
    elements = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            elements.append(f"function: {node.name}")
        elif isinstance(node, ast.ClassDef):
            elements.append(f"class: {node.name}")
            for child in node.body:
                if isinstance(child, ast.FunctionDef):
                    elements.append(f"  method: {child.name}")

    return elements


def extract_js_elements(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    function_pattern = r'function\s+(\w+)'
    class_pattern = r'class\s+(\w+)'
    method_pattern = r'(\w+)\s*\([^)]*\)\s*{'

    functions = re.findall(function_pattern, content)
    classes = re.findall(class_pattern, content)
    methods = re.findall(method_pattern, content)

    elements = []
    elements.extend([f"function: {func}" for func in functions])
    for cls in classes:
        elements.append(f"class: {cls}")
    elements.extend([
        f"  method: {method}" for method in methods if method not in functions
    ])

    return elements


def generate_tree_string(tree):

    def _generate_tree(tree, prefix=""):
        tree_str = ""
        items = list(tree.items())
        for i, (path, contents) in enumerate(items):
            if path == 'root':
                continue
            connector = "└── " if i == len(items) - 1 else "├── "
            tree_str += f"{prefix}{connector}{os.path.basename(path)}/\n"
            extension = "    " if i == len(items) - 1 else "│   "
            for j, item in enumerate(contents):
                item_connector = "└── " if j == len(contents) - 1 else "├── "
                if isinstance(item, dict):
                    file_name, elements = list(item.items())[0]
                    tree_str += f"{prefix}{extension}{item_connector}{file_name}\n"
                    for k, element in enumerate(elements):
                        element_connector = "    └── " if k == len(
                            elements) - 1 else "    ├── "
                        tree_str += f"{prefix}{extension}    {element_connector}{element}\n"
                else:
                    tree_str += f"{prefix}{extension}{item_connector}{item}\n"
        return tree_str

    return _generate_tree(tree)


def export_files(tree, output_path, file_types):
    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write(f"--- Export timestamp: {datetime.now()} ---\n\n")

        if 'description' in file_types:
            outfile.write(get_app_description())
            outfile.write("\n\n")

        if 'tree' in file_types:
            outfile.write("Project Structure:\n")
            outfile.write(generate_tree_string(tree))
            outfile.write("\n\n")

        file_order = ['.py', '.html', '.json', '.js', '.css', '.md']

        for ext in file_order + ['other']:
            if ext == 'other':
                if 'all' not in file_types and 'other' not in file_types:
                    continue
            elif ext[1:] not in file_types and 'all' not in file_types:
                continue

            for directory, files in tree.items():
                for file in files:
                    # Check if 'file' is a dict (from map_functions_to_tree)
                    if isinstance(file, dict):
                        file_name = list(file.keys())[0]
                    else:
                        file_name = file

                    file_path = os.path.join(
                        directory,
                        file_name) if directory != 'root' else file_name

                    if os.path.isfile(file_path):
                        if ext == 'other' and os.path.splitext(
                                file_name)[1] in file_order:
                            continue
                        if ext != 'other' and not file_name.endswith(ext):
                            continue
                        try:
                            with open(file_path, 'r',
                                      encoding='utf-8') as infile:
                                outfile.write(
                                    f"--- Start of {file_path} ---\n")
                                outfile.write(infile.read())
                                outfile.write(
                                    f"\n--- End of {file_path} ---\n\n")
                        except UnicodeDecodeError:
                            outfile.write(
                                f"--- Unable to read {file_path} (possibly a binary file) ---\n\n"
                            )


def get_app_description():
    return """
    # 
    This is the app description.. 
    """


def run_scrubber(options):
    c = delegator.run(f"bash scrubber.sh {options}")
    print(c.out)
    if c.return_code != 0:
        print(f"Scrubber failed: {c.err}")


def main():
    parser = argparse.ArgumentParser(
        description='Export selected files to an output file.')
    parser.add_argument(
        '-o',
        '--output',
        default='./backups/exported_files.txt',
        help='Output filepath (default: ./backups/exported_files.txt)')
    parser.add_argument('--export-options',
                        default='1,1,1,all',
                        help='Export options (default: 1,1,1,all)')
    parser.add_argument(
        '--recent',
        type=int,
        default=None,
        help='Include only files modified in the last N minutes')
    parser.add_argument(
        '--map-functions',
        action='store_true',
        help='Map functions, classes, and methods in Python and JS files')
    args = parser.parse_args()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_output = os.path.splitext(args.output)[0]
    output_file = f"{base_output}_{timestamp}.txt"

    file_types = set()
    export_choices = args.export_options.split(',')

    if len(export_choices) < 4:
        print("Invalid export options. Using default: 1,1,1,all")
        export_choices = ['1', '1', '1', 'all']

    if export_choices[0] == '1':
        file_types.add('description')

    if export_choices[1] == '1':
        file_types.add('tree')

    file_type_options = [
        'all', 'py', 'js', 'md', 'txt', 'css', 'html', 'json', 'other'
    ]
    if export_choices[2] == '1':
        file_types.update(file_type_options)
    else:
        selected_types = export_choices[3].split(',')
        file_types.update(selected_types)

    os.makedirs('./backups', exist_ok=True)
    tree = create_tree(recent=args.recent, map_functions=args.map_functions)
    export_files(tree, output_file, file_types)

    print(f"\nFiles were exported successfully to {output_file}")


if __name__ == '__main__':
    main()
