import os
import re
import json
import importlib.metadata
import subprocess
import sys


def install_package(package_name, version=None):
    """Install a package using pip."""
    try:
        if version:
            package_name = f"{package_name}=={version}"
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"Successfully installed {package_name}.")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}.")


def check_and_install_dependencies_with_version(notebook_path, default_versions=None):
    """
    Check and optionally install missing dependencies with version prompts.
    
    Parameters:
        notebook_path (str): Path to the Jupyter notebook file.
        default_versions (dict): Dictionary of modules and specific versions to install.
    """
    if default_versions is None:
        default_versions = {}

    # Read the notebook file
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    # Extract code cells
    code_cells = [
        cell['source']
        for cell in notebook['cells']
        if cell['cell_type'] == 'code'
    ]

    # Extract all imports
    import_pattern = re.compile(r'^\s*(?:import|from)\s+([\w\d_\.]+)')
    imports = set()

    for cell in code_cells:
        for line in cell:
            match = import_pattern.match(line)
            if match:
                imports.add(match.group(1).split('.')[0])  # Capture the top-level module

    # Check and optionally install each import
    report = []
    for module in imports:
        try:
            version = importlib.metadata.version(module)
            report.append({'Module': module, 'Installed': True, 'Version': version})
        except importlib.metadata.PackageNotFoundError:
            report.append({'Module': module, 'Installed': False, 'Version': None})
            # Determine the version to install
            target_version = default_versions.get(module)
            prompt = f"Module '{module}' is missing. "
            if target_version:
                prompt += f"Do you want to install {module} v. {target_version}? (yes/no): "
            else:
                prompt += f"Do you want to install the latest version of {module}? (yes/no): "
            # Prompt user for installation
            while True:
                user_input = input(prompt).strip().lower()
                if user_input in ['yes', 'y']:
                    install_package(module, target_version)
                    break
                elif user_input in ['no', 'n']:
                    print(f"Skipping installation of {module}.")
                    break
                else:
                    print("Invalid input. Please enter 'yes' or 'no'.")

    return report


# Example usage
notebook_path = 'ironkaggle.ipynb'  # Replace with your notebook's path

# Specify default versions if desired
default_versions = {
    'seaborn': '0.12.1',
    'sklearn': '1.2.0',
    'xgboost': '1.7.2'
}

report = check_and_install_dependencies_with_version(notebook_path, default_versions)

# Print the report
import pandas as pd
df = pd.DataFrame(report)
print(df)

# # Optionally, save the report to a file
# df.to_csv('dependency_report.csv', index=False)
