import os
import argparse
from datetime import datetime
import glob
import ast
import re

class FileExporter:
    def __init__(self, output_path, export_options, recent=None, map_functions=False, specific_path=None):
        self.output_path = output_path
        self.export_options = export_options
        self.recent = recent
        self.map_functions = map_functions
        self.specific_path = specific_path
        self.file_types = self._parse_export_options()

    def _parse_export_options(self):
        choices = self.export_options.split(',')
        file_types = set()
        if len(choices) < 4:
            print("Invalid export options. Using default: 1,1,1,all")
            choices = ['1', '1', '1', 'all']

        if choices[0] == '1':
            file_types.add('description')
        if choices[1] == '1':
            file_types.add('tree')

        file_type_options = ['all', 'py', 'js', 'md', 'txt', 'css', 'html', 'json', 'other']
        if choices[2] == '1':
            file_types.update(file_type_options)
        else:
            file_types.update(choices[3].split(','))

        return file_types

    def create_tree(self):
        tree = {'root': []}
        current_time = datetime.now()

        if self.specific_path:
            for file_path in glob.glob(self.specific_path, recursive=True):
                self._process_file(file_path, tree, current_time)
        else:
            included_dirs = ['app', 'static']
            included_files = ['config.py', 'main.py']
            excluded_dirs = ['__pycache__', 'migrations', '.upm', '.pythonlibs']
            excluded_files = ['.gitignore', 'poetry.lock', '.png', '.jpg', '.jpeg']

            for item in os.listdir():
                if os.path.isfile(item) and item in included_files:
                    self._process_file(item, tree, current_time)
                elif os.path.isdir(item) and item in included_dirs:
                    for root, dirs, files in os.walk(item):
                        dirs[:] = [d for d in dirs if d not in excluded_dirs]
                        files = [f for f in files if f not in excluded_files and not f.endswith(('.png', '.jpg', '.jpeg'))]
                        for file in files:
                            file_path = os.path.join(root, file)
                            self._process_file(file_path, tree, current_time)

        if self.map_functions:
            tree = self._map_functions_to_tree(tree)

        return tree

    def _process_file(self, file_path, tree, current_time):
        if os.path.isfile(file_path):
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if self.recent is None or (current_time - file_mtime).total_seconds() <= self.recent * 60:
                dir_path = os.path.dirname(file_path)
                if dir_path not in tree:
                    tree[dir_path] = []
                tree[dir_path].append(os.path.basename(file_path))

    def _map_functions_to_tree(self, tree):
        for directory, files in tree.items():
            mapped_files = []
            for file in files:
                file_path = os.path.join(directory, file) if directory != 'root' else file
                if file.endswith('.py'):
                    mapped_files.append({file: self._extract_python_elements(file_path)})
                elif file.endswith('.js'):
                    mapped_files.append({file: self._extract_js_elements(file_path)})
                else:
                    mapped_files.append(file)
            tree[directory] = mapped_files
        return tree

    def _extract_python_elements(self, file_path):
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

    def _extract_js_elements(self, file_path):
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
        elements.extend([f"  method: {method}" for method in methods if method not in functions])
        return elements

    def generate_tree_string(self, tree):
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
                            element_connector = "    └── " if k == len(elements) - 1 else "    ├── "
                            tree_str += f"{prefix}{extension}    {element_connector}{element}\n"
                    else:
                        tree_str += f"{prefix}{extension}{item_connector}{item}\n"
            return tree_str
        return _generate_tree(tree)

    def export_files(self, tree):
        with open(self.output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(f"--- Export timestamp: {datetime.now()} ---\n\n")

            if 'description' in self.file_types:
                outfile.write(self._get_app_description())
                outfile.write("\n\n")

            if 'tree' in self.file_types:
                outfile.write("Project Structure:\n")
                outfile.write(self.generate_tree_string(tree))
                outfile.write("\n\n")

            file_order = ['.py', '.html', '.json', '.js', '.css', '.md']

            for ext in file_order + ['other']:
                if ext == 'other':
                    if 'all' not in self.file_types and 'other' not in self.file_types:
                        continue
                elif ext[1:] not in self.file_types and 'all' not in self.file_types:
                    continue

                for directory, files in tree.items():
                    for file in files:
                        file_name = list(file.keys())[0] if isinstance(file, dict) else file
                        file_path = os.path.join(directory, file_name) if directory != 'root' else file_name

                        if os.path.isfile(file_path):
                            if ext == 'other' and os.path.splitext(file_name)[1] in file_order:
                                continue
                            if ext != 'other' and not file_name.endswith(ext):
                                continue
                            try:
                                with open(file_path, 'r', encoding='utf-8') as infile:
                                    outfile.write(f"--- Start of {file_path} ---\n")
                                    outfile.write(infile.read())
                                    outfile.write(f"\n--- End of {file_path} ---\n\n")
                            except UnicodeDecodeError:
                                outfile.write(f"--- Unable to read {file_path} (possibly a binary file) ---\n\n")

    def _get_app_description(self):
        return """
        # 
        This is a two-sided marketplace application built with Flask, hosted on Replit. It connects Users with Founders who work with Vendors to provide various events and services. The app uses only Auth0 for all authentication and authorization, and Stripe for payment processing, subscriptions, and payouts. The application is structured around Communities, Events, Products, Subscriptions, Loops, and Stacks.
        """

def main():
    parser = argparse.ArgumentParser(description='Export selected files to an output file.')
    parser.add_argument('-o', '--output', default='./backups/exported_files.txt',
                        help='Output filepath (default: ./backups/exported_files.txt)')
    parser.add_argument('--export-options', default='1,1,1,all',
                        help='Export options (default: 1,1,1,all)')
    parser.add_argument('--recent', type=int, default=None,
                        help='Include only files modified in the last N minutes')
    parser.add_argument('--map-functions', action='store_true',
                        help='Map functions, classes, and methods in Python and JS files')
    parser.add_argument('--specific-path', type=str, default=None,
                        help='Specific folder or subfolder to export, e.g., "app/models/*.py"')
    args = parser.parse_args()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_output = os.path.splitext(args.output)[0]
    output_file = f"{base_output}_{timestamp}.txt"

    os.makedirs('./backups', exist_ok=True)

    exporter = FileExporter(
        output_file,
        args.export_options,
        recent=args.recent,
        map_functions=args.map_functions,
        specific_path=args.specific_path
    )

    tree = exporter.create_tree()
    exporter.export_files(tree)

    print(f"\nFiles were exported successfully to {output_file}")

if __name__ == '__main__':
    main()
