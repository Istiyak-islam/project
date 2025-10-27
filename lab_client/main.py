# lab_client/main.py
import tkinter as tk
from tkinter import ttk, messagebox
import json, os, threading, socket, subprocess, webbrowser
from utils import is_installed, download_with_progress

SERVER_URL = "http://<SERVER_IP>:5000"  # change to your server IP or localhost for testing

BASE_DIR = os.path.dirname(__file__)
with open(os.path.join(BASE_DIR, "config.json"), "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

DOWNLOADS = os.path.join(BASE_DIR, "downloads")
os.makedirs(DOWNLOADS, exist_ok=True)

def report_check(hostname, software, status, path=""):
    try:
        import requests
        requests.post(f"{SERVER_URL}/api/report_check", json={
            "hostname": hostname, "software": software, "status": status, "path": path
        }, timeout=6)
    except Exception as e:
        print("Report failed:", e)

def do_check_all(progress_var=None):
    hostname = socket.gethostname()
    results = []
    for s in CONFIG.get("softwares", []):
        name = s.get("name")
        path = s.get("path_windows")
        cmd = s.get("cmd")
        installed = is_installed(path, cmd)
        status = "Installed" if installed else "Not Installed"
        results.append((name, status, path if installed else ""))
        # report each to server (non-blocking)
        threading.Thread(target=report_check, args=(hostname, name, status, path if installed else ""), daemon=True).start()
    return results

# GUI
root = tk.Tk()
root.title("Lab Assistant - Software Checker")
root.geometry("900x600")

ttk.Label(root, text="Lab Assistant — Software Checker", font=("Helvetica", 16)).pack(pady=10)

frame = ttk.Frame(root)
frame.pack(fill="both", padx=10, pady=10, expand=True)

cols = ("Software", "Status", "Action")
tree = ttk.Treeview(frame, columns=cols, show="headings", height=20)
for c in cols:
    tree.heading(c, text=c)
tree.column("Software", width=450)
tree.column("Status", width=150, anchor="center")
tree.column("Action", width=150, anchor="center")
tree.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scrollbar.set)
scrollbar.pack(side="right", fill="y")

progress_var = tk.IntVar()
progress = ttk.Progressbar(root, orient="horizontal", length=800, mode="determinate", variable=progress_var)
progress.pack(pady=8)

def refresh_table():
    for i in tree.get_children(): tree.delete(i)
    rows = do_check_all()
    for r in rows:
        name, status, path = r
        tree.insert("", "end", values=(name, status, "Install" if status=="Not Installed" else "Open"))

def on_tree_click(event):
    item = tree.identify_row(event.y)
    col = tree.identify_column(event.x)
    if not item: return
    values = tree.item(item, "values")
    name = values[0]
    status = values[1]
    software = next((s for s in CONFIG["softwares"] if s["name"]==name), None)
    if not software: return
    url = software.get("url")

    # If installed -> open path if possible
    if status == "Installed":
        p = software.get("path_windows")
        if p and os.path.exists(p):
            try:
                os.startfile(p)
            except Exception as e:
                messagebox.showinfo("Open", f"Cannot open: {e}")
        else:
            messagebox.showinfo("Info", "Installed but path not found.")
        return

    # Not installed -> try auto download if direct link
    if any(url.lower().endswith(ext) for ext in (".exe", ".msi", ".zip")):
        dest = os.path.join(DOWNLOADS, url.split("/")[-1].split("?")[0])
        confirm = messagebox.askyesno("Download", f"Download and install {name}?")
        if not confirm: return
        progress_var.set(0)
        def progress_cb(pct):
            progress_var.set(pct)
        def worker():
            try:
                download_with_progress(url, dest, progress_cb)
                messagebox.showinfo("Downloaded", f"Saved to {dest}")
                # auto-launch if exe/msi
                if dest.lower().endswith((".exe",".msi")):
                    try:
                        subprocess.Popen([dest], shell=True)
                    except Exception as e:
                        messagebox.showwarning("Launch", f"Could not launch installer: {e}")
                refresh_table()
            except Exception as e:
                messagebox.showerror("Error", f"Download failed: {e}")
        threading.Thread(target=worker, daemon=True).start()
    else:
        # Not direct -> open official site and show message
        messagebox.showinfo("Manual Download", f"{name} requires manual download. Opening official site.")
        webbrowser.open(url)

# click binding (install/open actions)
tree.bind("<Button-1>", on_tree_click)

# top buttons
top_frame = ttk.Frame(root)
top_frame.pack(pady=6)
ttk.Button(top_frame, text="Refresh", command=refresh_table).pack(side="left", padx=6)
ttk.Button(top_frame, text="Logout", command=root.quit).pack(side="left", padx=6)

# initial load
refresh_table()
root.mainloop()
