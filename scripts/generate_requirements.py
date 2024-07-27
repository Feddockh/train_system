import os
import ast
import subprocess

def is_local_import(import_name, local_packages):
    return any(import_name.startswith(pkg) for pkg in local_packages)

def get_imports_from_file(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read(), filename=file_path)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports

def get_all_imports(project_path, local_packages):
    all_imports = set()
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                imports = get_imports_from_file(file_path)
                for imp in imports:
                    if imp and not is_local_import(imp, local_packages):
                        all_imports.add(imp)
    return all_imports

def get_installed_packages():
    result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    installed_packages = {}
    for line in result.stdout.splitlines():
        if '==' in line:
            package, version = line.split('==')
            installed_packages[package] = version
    return installed_packages

def map_import_to_package(import_name, mapping, installed_packages):
    if import_name in mapping:
        package_name = mapping[import_name]
        if package_name in installed_packages:
            return f"{package_name}=={installed_packages[package_name]}"
    else:
        try:
            # Attempt to find the package using pip show
            result = subprocess.run(['pip', 'show', import_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return import_name
            else:
                print(f"Warning: Import '{import_name}' not found in mapping and no package found via pip.")
        except Exception as e:
            print(f"Error searching for package {import_name}: {e}")
    return None

def create_requirements_file(imports, mapping, installed_packages):
    requirements = set()
    for imp in imports:
        package_name_with_version = map_import_to_package(imp, mapping, installed_packages)
        if package_name_with_version:  # Exclude standard library imports and unresolved imports
            requirements.add(package_name_with_version)
    
    with open("requirements.txt", "w") as file:
        for req in sorted(requirements):
            file.write(f"{req}\n")
    print("requirements.txt file created successfully.")

def main():
    project_path = input("Enter the path to your project directory: ")
    local_packages = input("Enter a comma-separated list of local package names: ").split(',')

    imports = get_all_imports(project_path, local_packages)
    print("External imports found in the project:")
    for imp in imports:
        print(imp)
    
    mapping = {
        'PyQt6': 'PyQt6',
        'PyQt6.QtCore': 'PyQt6',
        'PyQt6.QtWidgets': 'PyQt6',
        'PyQt6.QtGui': 'PyQt6',
        'PyQt6.sip': 'PyQt6',
        'PyQt5': 'PyQt5',
        'PyQt5.QtCore': 'PyQt5',
        'PyQt5.QtWidgets': 'PyQt5',
        'matplotlib': 'matplotlib',
        'matplotlib.pyplot': 'matplotlib',
        'matplotlib.backends.backend_qtagg': 'matplotlib',
        'matplotlib.figure': 'matplotlib',
        'pandas': 'pandas',
        'networkx': 'networkx',
        'anytree': 'anytree',
        'paramiko': 'paramiko',
        'cryptography.fernet': 'cryptography',
        'setuptools': 'setuptools',
        'typing': '',  # Part of standard library
        'abc': '',  # Part of standard library
        'time': '',  # Part of standard library
        'random': '',  # Part of standard library
        'copy': '',  # Part of standard library
        'collections': '',  # Part of standard library
        'csv': '',  # Part of standard library
        'os': '',  # Part of standard library
        'heapq': '',  # Part of standard library
        'enum': '',  # Part of standard library
        'sys': '',  # Part of standard library
        'ast': '',  # Part of standard library
        'dataclasses': '',  # Part of standard library (Python 3.7+)
        'math': '',  # Part of standard library
        'json': '',  # Part of standard library
        'datetime': '',  # Part of standard library
        'subprocess': '',  # Part of standard library
    }

    installed_packages = get_installed_packages()
    create_requirements_file(imports, mapping, installed_packages)

if __name__ == "__main__":
    main()
