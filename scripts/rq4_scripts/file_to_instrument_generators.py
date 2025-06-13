import glob
import os
import argparse

# Set up argument parser
parser = argparse.ArgumentParser(description='Generate list of files to instrument')
parser.add_argument('directory', help='Directory to search for Python files')
parser.add_argument('venv_name', help='Name of virtual environment directory')

# Parse arguments
args = parser.parse_args()

# Use the provided paths
search_dir = os.path.abspath(args.directory)
venv_path = os.path.join(search_dir, args.venv_name)

# Change to the search directory
os.chdir(search_dir)

# Get all .py files recursively
all_files = glob.glob('**/*.py', recursive=True)

def is_in_venv_site_packages(file):
    return os.path.commonpath([file, venv_path]) == venv_path and 'site-packages' in file

def is_project_file(file):
    return not file.startswith(venv_path)

def should_ignore_file(file):
    # Ignore pip, setuptools, pytest, and distutils related files
    ignore_patterns = ['pip', 'setuptools', 'pytest', 'distutils']
    return any(pattern in file.lower() for pattern in ignore_patterns)

# Filter: include site-packages + your code, exclude internal venv scripts, pip, setuptools, pytest, and distutils
filtered_files = [
    f for f in all_files
    if (is_project_file(f) or is_in_venv_site_packages(f)) and not should_ignore_file(f)
]

# Change back to parent directory
os.chdir('..')


# Save to file
with open('files_to_instrument.txt', 'w') as f:
    for file in filtered_files:
        f.write(file + '\n')