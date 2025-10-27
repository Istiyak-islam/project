# file_helpers.py
import os
import json
import subprocess
import platform
import logging

# --------------------------------------------------
# Logging Configuration
# --------------------------------------------------
logging.basicConfig(
    filename='logs/file_helpers.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --------------------------------------------------
# File/Directory Utilities
# --------------------------------------------------
def ensure_directory(path):
    """
    Ensure that a directory exists. If not, create it.
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            logging.info(f"Directory created: {path}")
        return True
    except Exception as e:
        logging.error(f"Error creating directory {path}: {str(e)}")
        return False


def save_json_file(path, data):
    """
    Save Python dict/list to JSON file.
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logging.info(f"JSON saved successfully: {path}")
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {path}: {str(e)}")
        return False


def load_json_file(path):
    """
    Load JSON file and return as Python dict/list.
    """
    try:
        if not os.path.exists(path):
            logging.warning(f"JSON file not found: {path}")
            return None
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"JSON loaded successfully: {path}")
        return data
    except Exception as e:
        logging.error(f"Error loading JSON from {path}: {str(e)}")
        return None

# --------------------------------------------------
# Software Check / Installation Utilities
# --------------------------------------------------
def is_software_installed(software_name, search_paths=None):
    """
    Check if a software is installed on the system.
    Optionally provide paths to search for the executable.
    Returns (installed: bool, path: str or None)
    """
    try:
        # First check PATH environment
        path = shutil.which(software_name)
        if path:
            logging.info(f"{software_name} found in PATH: {path}")
            return True, path

        # Check custom search paths
        if search_paths:
            for sp in search_paths:
                exe_path = os.path.join(sp, software_name)
                if os.path.exists(exe_path):
                    logging.info(f"{software_name} found at {exe_path}")
                    return True, exe_path

        logging.info(f"{software_name} is not installed")
        return False, None
    except Exception as e:
        logging.error(f"Error checking software {software_name}: {str(e)}")
        return False, None


def install_software(software_info):
    """
    Auto-install software.
    software_info is a dict: {
        'name': 'CodeBlocks',
        'installer_path': 'path/to/installer.exe' or None,
        'download_url': 'https://...'
    }
    """
    try:
        installer_path = software_info.get('installer_path')
        download_url = software_info.get('download_url')
        name = software_info.get('name')

        if installer_path and os.path.exists(installer_path):
            logging.info(f"Installing {name} using installer {installer_path}")
            if platform.system() == "Windows":
                subprocess.run([installer_path, "/S"], check=True)
            elif platform.system() == "Linux":
                subprocess.run(['bash', installer_path], check=True)
            else:
                logging.warning(f"Auto-install not supported for {platform.system()}")
                return False
            logging.info(f"{name} installed successfully")
            return True
        else:
            # Open official download page
            logging.info(f"{name} requires manual download. Redirecting to: {download_url}")
            if platform.system() == "Windows":
                os.startfile(download_url)
            elif platform.system() == "Linux":
                subprocess.run(['xdg-open', download_url])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', download_url])
            return False
    except Exception as e:
        logging.error(f"Error installing {name}: {str(e)}")
        return False

# --------------------------------------------------
# Example: Save student submission
# --------------------------------------------------
def save_student_submission(student_id, exam_id, code, base_dir='submissions'):
    """
    Save a student's submission in a structured folder: submissions/{exam_id}/{student_id}.txt
    """
    try:
        exam_dir = os.path.join(base_dir, str(exam_id))
        ensure_directory(exam_dir)
        file_path = os.path.join(exam_dir, f"{student_id}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)
        logging.info(f"Saved submission: {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"Error saving submission for student {student_id}: {str(e)}")
        return None

