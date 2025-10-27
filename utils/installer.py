# utils/installer.py
import os, glob, subprocess, requests, threading
from urllib.parse import urlsplit
from werkzeug.utils import secure_filename

DOWNLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'downloads'))
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def path_exists_windows(path):
    if not path:
        return False
    if '*' in path:
        return len(glob.glob(path)) > 0
    return os.path.exists(path)

def run_cmd_ok(cmd, timeout=5):
    try:
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
        out = (p.stdout or b'').decode(errors='ignore') + (p.stderr or b'').decode(errors='ignore')
        return p.returncode == 0 or bool(out.strip())
    except Exception:
        return False

def detect_installed(item):
    t = item.get('type')
    if t in ('exe','dir','file'):
        return path_exists_windows(item.get('path_windows'))
    elif t == 'cmd':
        return run_cmd_ok(item.get('cmd'))
    else:
        return False

def download_to_file(url, filename, progress_callback=None, chunk_size=1024*64):
    # downloads to downloads/filename (returns full path)
    local_path = os.path.join(DOWNLOAD_DIR, filename)
    with requests.get(url, stream=True, allow_redirects=True, timeout=30) as r:
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))
        downloaded = 0
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if not chunk:
                    continue
                f.write(chunk)
                downloaded += len(chunk)
                if progress_callback and total:
                    progress_callback(downloaded, total)
    return local_path
