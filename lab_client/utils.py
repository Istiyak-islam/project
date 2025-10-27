# lab_client/utils.py
import os, subprocess, glob, webbrowser, sys, requests

def is_installed(path=None, cmd=None, package=None):
    try:
        if path:
            if '*' in path:
                return bool(glob.glob(path))
            return os.path.exists(path)
    except:
        pass
    if cmd:
        try:
            cp = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return cp.returncode == 0
        except:
            return False
    if package:
        try:
            __import__(package)
            return True
        except:
            return False
    return False

def download_with_progress(url, dest_path, progress_callback=None):
    headers = {"User-Agent":"Mozilla/5.0"}
    with requests.get(url, stream=True, headers=headers, allow_redirects=True, timeout=30) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        downloaded = 0
        chunk_size = 1024*128
        with open(dest_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if not chunk: continue
                f.write(chunk)
                downloaded += len(chunk)
                if total and progress_callback:
                    progress_callback(int(downloaded/total*100))
    return dest_path
