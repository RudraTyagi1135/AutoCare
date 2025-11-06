# ================================
# 📦 Basic setup.py for Packaging
# ================================

# Importing the basic logging configuration (not used in this file, but often used in setup scripts for debugging)
from logging import basicConfig  

# Importing utilities from setuptools
# - setup: used to configure the package metadata and installation
# - find_packages: automatically finds all Python packages in your project directory
from setuptools import setup, find_packages  

# Importing typing support for type hints
from typing import List  



# ================================
# 🔧 Utility function to parse requirements
# ================================
def get_requirements() -> List[str]:
    """
    This function reads the `requirements.txt` file 
    and returns a clean list of dependencies (packages to install).
    Why?
    - Keeps setup.py clean.
    - Avoids hardcoding dependencies directly inside setup.py.
    - Ensures consistency between local development and production installs.
    """
    requirement_lst: List[str] = []   # empty list to collect dependencies

    try:
        # Open requirements.txt in read mode
        with open('requirements.txt', 'r') as file:    
            
            # Read all lines from requirements.txt
            lines = file.readlines()

            # Process each line
            for line in lines:
                requirement = line.strip()  # remove whitespace/newlines

                # Ignore empty lines and "-e ." (used for editable installs in development mode)
                if requirement and requirement != '-e .':
                    requirement_lst.append(requirement)  # add valid dependency to list

    # If requirements.txt is missing, just warn instead of crashing
    except FileNotFoundError:
        print("⚠️ requirements.txt not found")  

    # Return the final list of requirements
    return requirement_lst    



# ================================
# 📦 Setup Configuration
# ================================
# This tells pip/setuptools how to install your project as a package.
setup(
     # Metadata
     name = "ETL_project",                         # package/project name
     version = "1.0.0",                            # project version
     author = "Rudra Tyagi",                       # author name
     author_email = "rudratyagi777@gmail.com",     # author contact

     # Automatically find all Python packages inside the project
     # Example: if you have folders like `network_security/`, `utils/`, they get packaged
     packages = find_packages(),                   

     # Dependencies for installation
     # (will read directly from requirements.txt via our helper function)
     install_requires = get_requirements()          # <-- fixed typo: `install_reqirements` → `install_requires`
)

