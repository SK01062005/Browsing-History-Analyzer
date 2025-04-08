import os
import sqlite3
import time
import requests
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
import webbrowser
import asyncio
import aiohttp
import csv
from PIL import Image, ImageTk
import winsound

# Set VirusTotal API Key
VIRUSTOTAL_API_KEY = "c4b16b3dee648fdb2572985710cd04b18db62f717bef6bbf93ac8c9e2786d303"

# Browser History Paths
BROWSER_PATHS = {
    "Edge": os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History"),
    "Opera": os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera Stable\\History"),
    "Opera GX": os.path.expanduser("~\\AppData\\Roaming\\Opera Software\\Opera GX Stable\\History"),
}

def get_browser_history(browser):
    history_data = []
    path = BROWSER_PATHS.get(browser)
    if not path or not os.path.exists(path):
        messagebox.showerror("Error", f"{browser} history not found!")
        return []
    try:
        temp_path = path + "_copy"
        shutil.copyfile(path, temp_path)
        with sqlite3.connect(temp_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 30")
            rows = cursor.fetchall()
        for row in rows:
            history_data.append([row[0], row[1] if row[1] else "No Title", row[2], "🔍 Scanning..."])
    except sqlite3.Error:
        messagebox.showerror("Database Error", f"Could not access {browser} history!")
    return history_data

async def check_url_safety(session, url):
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    params = {"url": url}
    try:
        async with session.post("https://www.virustotal.com/api/v3/urls", headers=headers, data=params) as response:
            if response.status == 200:
                scan_id = (await response.json()).get("data", {}).get("id", None)
                if scan_id:
                    await asyncio.sleep(3)
                    async with session.get(f"https://www.virustotal.com/api/v3/analyses/{scan_id}", headers=headers) as result:
                        data = await result.json()
                        malicious_count = data.get("data", {}).get("attributes", {}).get("stats", {}).get("malicious", 0)
                        if malicious_count > 0:
                            winsound.Beep(1000, 500)
                            return "⚠️ Unsafe"
                        return "✅ Safe"
            return "❓ No Data"
    except Exception:
        return "❌ API Error"

async def analyze_history():
    browser = browser_var.get()
    history_list = get_browser_history(browser)
    for i in tree.get_children():
        tree.delete(i)
    for row in history_list:
        tree.insert("", "end", values=row)
    progress["value"] = 10
    status_label.config(text="🔄 Scanning URLs...")
    root.update_idletasks()
    async with aiohttp.ClientSession() as session:
        results = await asyncio.gather(*(check_url_safety(session, row[0]) for row in history_list))
    for i, safety_status in enumerate(results):
        item_id = tree.get_children()[i]
        tree.item(item_id, values=[history_list[i][0], history_list[i][1], history_list[i][2], safety_status])
        if safety_status == "⚠️ Unsafe":
            tree.tag_configure("unsafe", foreground="red", font=("Helvetica", 10, "bold"))
            tree.item(item_id, tags=("unsafe",))
    progress["value"] = 100
    status_label.config(text="✅ Scan Complete")
    messagebox.showinfo("Analysis Complete", "Browser history analysis is completed!")

def open_url(event):
    item = tree.selection()
    if item:
        url = tree.item(item, "values")[0]
        webbrowser.open(url)

def export_results():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if file_path:
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["URL", "Title", "Last Visit", "Safety"])
            for row in tree.get_children():
                writer.writerow(tree.item(row, "values"))
        messagebox.showinfo("Export Complete", "Results exported successfully!")

def set_background():
    global bg_image
    img = Image.open("image.png")
    img = img.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.Resampling.LANCZOS)
    bg_image = ImageTk.PhotoImage(img)
    canvas.create_image(0, 0, image=bg_image, anchor="nw")
    canvas.lower("all")

root = tb.Window(themename="cyborg")
root.title("🚀 Browser History Analyzer")
root.geometry("1300x750")

canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
canvas.pack(fill="both", expand=True)
set_background()

title_label = tb.Label(root, text="🔎 Browser History Analyzer", font=("Arial", 24, "bold"), foreground="cyan")
title_label.place(relx=0.5, y=30, anchor="center")

output_frame = tb.Frame(root, bootstyle="dark")
output_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.7)

browser_var = tk.StringVar(value="Edge")
browser_menu = tb.Combobox(output_frame, textvariable=browser_var, values=["Edge", "Opera", "Opera GX"], state="readonly", font=("Helvetica", 14))
browser_menu.pack(pady=10)

analyze_btn = tb.Button(output_frame, text="🚀 Analyze History", bootstyle="success-outline", command=lambda: asyncio.run(analyze_history()))
analyze_btn.pack(pady=5)

export_btn = tb.Button(output_frame, text="📁 Export Results", bootstyle="info-outline", command=export_results)
export_btn.pack(pady=5)

tree = ttk.Treeview(output_frame, columns=("URL", "Title", "Last Visit", "Safety"), show="headings", height=12)
tree.pack(fill="both", expand=True)
tree.bind("<Double-1>", open_url)

progress = tb.Progressbar(root, length=450, mode="determinate", bootstyle="success")
progress.place(relx=0.5, rely=0.9, anchor="center")

status_label = tb.Label(root, text="", font=("Arial", 12), foreground="yellow")
status_label.place(relx=0.5, rely=0.95, anchor="center")

root.mainloop()
