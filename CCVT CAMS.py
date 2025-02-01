#!/usr/bin/env python3
# -- coding: utf-8 --

import requests
import re
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from requests.structures import CaseInsensitiveDict

headers = CaseInsensitiveDict()
headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

languages = {
    "en": {
        "title": "Camera IP Fetcher",
        "select_country": "Select a country",
        "fetch_ips": "Fetch IP Addresses",
        "save_ips": "Save IP Addresses",
        "no_ips": "No IP addresses found.",
        "error": "Error",
        "warning": "Warning",
        "save_as": "Save As",
        "saved": "IP addresses saved to",
        "lang_select": "Select Language",
    },
    "tr": {
        "title": "Kamera IP Adresi Getirici",
        "select_country": "Bir ülke seçin",
        "fetch_ips": "IP Adreslerini Getir",
        "save_ips": "IP Adreslerini Kaydet",
        "no_ips": "IP adresi bulunamadı.",
        "error": "Hata",
        "warning": "Uyarı",
        "save_as": "Farklı Kaydet",
        "saved": "IP adresleri kaydedildi",
        "lang_select": "Dil Seç",
    },
}

current_lang = "en"

def fetch_countries():
    try:
        url = "http://www.insecam.org/en/jsoncountries/"
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            return data['countries']
        else:
            raise Exception(f"Failed to fetch countries: HTTP {resp.status_code}")
    except Exception as e:
        messagebox.showerror(languages[current_lang]["error"], str(e))
        return {}

def fetch_cameras(country_code):
    try:
        res = requests.get(f"http://www.insecam.org/en/bycountry/{country_code}", headers=headers)
        last_page = re.findall(r'pagenavigator\("\?page=", (\d+)', res.text)
        if not last_page:
            return []

        last_page = int(last_page[0])
        ip_addresses = []

        for page in range(last_page):
            res = requests.get(f"http://www.insecam.org/en/bycountry/{country_code}/?page={page}", headers=headers)
            find_ip = re.findall(r"http://\d+\.\d+\.\d+\.\d+:\d+", res.text)
            ip_addresses.extend(find_ip)

        return ip_addresses
    except Exception as e:
        messagebox.showerror(languages[current_lang]["error"], str(e))
        return []

def display_ips():
    country_code = country_var.get().split('(')[-1].strip(')')
    ip_addresses = fetch_cameras(country_code)

    ip_display.delete(1.0, tk.END)
    if ip_addresses:
        for ip in ip_addresses:
            ip_display.insert(tk.END, f"{ip}\n")
        animate_text()
    else:
        ip_display.insert(tk.END, languages[current_lang]["no_ips"])

def animate_text():
    text_content = ip_display.get(1.0, tk.END)
    ip_display.delete(1.0, tk.END)

    def reveal_text(index=0):
        if index < len(text_content):
            ip_display.insert(tk.END, text_content[index], "ip")
            ip_display.after(10, reveal_text, index + 1)

    reveal_text()

def save_to_file(ip_addresses):
    if not ip_addresses:
        messagebox.showwarning(languages[current_lang]["warning"], languages[current_lang]["no_ips"])
        return

    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if filepath:
        with open(filepath, 'w') as f:
            for ip in ip_addresses:
                f.write(f'{ip}\n')
        messagebox.showinfo(languages[current_lang]["saved"], f"{languages[current_lang]['saved']} {filepath}")

def on_enter(event):
    event.widget['background'] = 'lightblue'

def on_leave(event):
    event.widget['background'] = 'SystemButtonFace'

def change_language(lang):
    global current_lang
    current_lang = lang
    root.title(languages[lang]["title"])
    country_menu_label.config(text=languages[lang]["select_country"])
    fetch_button.config(text=languages[lang]["fetch_ips"])
    save_button.config(text=languages[lang]["save_ips"])
    lang_label.config(text=languages[lang]["lang_select"])

def main():
    global root, country_var, country_menu_label, ip_display, fetch_button, save_button, lang_label

    countries = fetch_countries()
    if not countries:
        return  # Eğer ülkeler yüklenmezse uygulama çalışmasın

    root = tk.Tk()
    root.title(languages[current_lang]["title"])
    root.geometry("600x400")

    cctv_label = tk.Label(root, text="CCTV OKYA", font=("Helvetica", 14, "bold"), fg="red")
    cctv_label.place(x=10, y=10)

    lang_label = tk.Label(root, text=languages[current_lang]["lang_select"])
    lang_label.pack(pady=5)

    lang_menu = tk.OptionMenu(root, tk.StringVar(), *["English (en)", "Türkçe (tr)"], command=lambda x: change_language(x.split('(')[-1].strip(')')))
    lang_menu.pack(pady=5)

    country_var = tk.StringVar(root)
    country_var.set(languages[current_lang]["select_country"])
    country_menu_label = tk.Label(root, text=languages[current_lang]["select_country"])
    country_menu_label.pack(pady=5)

    country_menu = tk.OptionMenu(root, country_var, *[f'{value["country"]} ({key})' for key, value in countries.items()])
    country_menu.pack(pady=10)

    ip_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
    ip_display.pack(pady=10)
    ip_display.tag_configure("ip", foreground="blue", font=("Helvetica", 12, "bold"))

    fetch_button = tk.Button(root, text=languages[current_lang]["fetch_ips"], command=display_ips)
    fetch_button.pack(pady=10)
    fetch_button.bind("<Enter>", on_enter)
    fetch_button.bind("<Leave>", on_leave)

    save_button = tk.Button(root, text=languages[current_lang]["save_ips"], command=lambda: save_to_file(ip_display.get(1.0, tk.END).strip().split('\n')))
    save_button.pack(pady=10)
    save_button.bind("<Enter>", on_enter)
    save_button.bind("<Leave>", on_leave)

    def open_in_browser(event):
        try:
            selected_ip = ip_display.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if selected_ip.startswith("http://"):
                import webbrowser
                webbrowser.open(selected_ip)
        except tk.TclError:
            pass

    ip_display.bind("<Double-1>", open_in_browser)

    def title_animation():
        original_title = languages[current_lang]["title"]
        anim_title = original_title + "  "
        def animate():
            if root.winfo_exists():
                nonlocal anim_title
                anim_title = anim_title[1:] + anim_title[0]
                root.title(anim_title)
                root.after(200, animate)
            else:
                return

        animate()

    root.after(0, title_animation)

    root.mainloop()

if __name__ == "__main__":
    main()
