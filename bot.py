#!/usr/bin/env python3
"""
Termux Automation Bot - Works inside proot Ubuntu
Instagram | Facebook | New FB | Reset FB
"""

import os
import sys
import time
import random
import threading
from queue import Queue, Empty
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ---------- Fixed Mobile User Agents ----------
USER_AGENTS = [
    "Mozilla/5.0 (Windows Mobile 10; Android 10.0; Microsoft; Lumia 950XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36 Edge/40.15254.603 VirusTotalBot",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_2 like Mac OS X) AppleWebKit/603.2.4 (KHTML, like Gecko) FxiOS/7.5b3349 Mobile/14F89 Safari/603.2.4",
    "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-S931B Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/127.0.6533.103 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-S931U Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/132.0.6834.163 Mobile Safari/537.36",
    "Mozila/5.0 (Linux; Android 14; SM-S928B/DS) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Mozila/5.0 (Linux; Android 14; SM-S928W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6099.230 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; RM-1152) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15254",
    "Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro Build/AD1A.240418.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.54 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 9 Build/AD1A.240411.003.A5; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.54 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; moto g power 5G - 2024 Build/U1UD34.16-62; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/123.0.6312.99 Mobile Safari/537.36"
]

def parse_proxy(proxy_str):
    if not proxy_str or proxy_str.lower() == "none":
        return None
    parts = proxy_str.split(':')
    if len(parts) < 2:
        return None
    server = f"http://{parts[0]}:{parts[1]}"
    config = {"server": server}
    if len(parts) >= 4:
        config["username"] = parts[2]
        config["password"] = parts[3]
    return config

# ---------- Automation Classes ----------
class InstagramAutomation:
    def __init__(self, phone, headless=True, proxy=None, user_agent=None, resend_attempts=0, viewport=None):
        self.phone = phone
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent or random.choice(USER_AGENTS)
        self.resend_attempts = resend_attempts
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.success = False
        self.resend_count = 0

    def run(self):
        playwright = None
        browser = None
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=self.headless, proxy=self.proxy)
            context = browser.new_context(user_agent=self.user_agent, viewport=self.viewport)
            page = context.new_page()
            page.goto("https://www.instagram.com/accounts/signup/phone/", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)

            phone_input = page.locator('input[aria-label="Mobile Number"]')
            phone_input.wait_for(state="visible", timeout=10000)
            phone_input.fill(self.phone)
            time.sleep(random.uniform(0.5, 1.2))

            next_btn = page.locator('div[role="button"][aria-label="Next"]')
            next_btn.wait_for(state="visible", timeout=10000)
            next_btn.click()
            time.sleep(2)
            page.wait_for_load_state("networkidle", timeout=20000)

            continue_btn = page.locator('div[role="button"]:has-text("Continue")')
            try:
                continue_btn.wait_for(state="visible", timeout=20000)
                continue_btn.click()
                time.sleep(1)
                page.wait_for_load_state("networkidle", timeout=10000)
            except PlaywrightTimeout:
                pass

            for _ in range(self.resend_attempts):
                try:
                    didnt_get_code = page.locator('div[role="button"][aria-label="I didn\'t get the code"]')
                    if didnt_get_code.count() == 0: break
                    didnt_get_code.click()
                    time.sleep(1)
                    resend_btn = page.locator('div[role="button"][aria-label="Resend confirmation code"]')
                    resend_btn.wait_for(state="visible", timeout=5000)
                    resend_btn.click()
                    self.resend_count += 1
                    time.sleep(2)
                except:
                    break
            self.success = True
        except:
            self.success = False
        finally:
            if browser: browser.close()
            if playwright: playwright.stop()
        return self.success


class FacebookAutomation:
    def __init__(self, phone, headless=True, proxy=None, user_agent=None, viewport=None):
        self.phone = phone
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent or random.choice(USER_AGENTS)
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.success = False

    def run(self):
        playwright = None
        browser = None
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=self.headless, proxy=self.proxy)
            context = browser.new_context(user_agent=self.user_agent, viewport=self.viewport)
            page = context.new_page()
            page.goto("https://m.facebook.com/login/identify/?ctx=recover&from_login_screen=0", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)

            phone_input = page.locator('input[aria-label="Mobile number"]')
            phone_input.wait_for(state="visible", timeout=15000)
            phone_input.fill(self.phone)
            time.sleep(random.uniform(0.5, 1.0))

            continue_btn = page.locator('div[role="button"][aria-label="Continue"]').first
            continue_btn.wait_for(state="visible", timeout=10000)
            continue_btn.click()
            time.sleep(3)

            if page.locator('div[role="radio"][aria-label*="sms" i]').count() > 0:
                page.locator('div[role="radio"][aria-label*="sms" i]').first.click()
                time.sleep(0.5)
                page.locator('div[role="button"][aria-label="Continue"]').last.click()

            self.success = True
        except:
            self.success = False
        finally:
            if browser: browser.close()
            if playwright: playwright.stop()
        return self.success


class NewFacebookAutomation:
    def __init__(self, phone, headless=True, proxy=None, user_agent=None, resend_attempts=0, viewport=None):
        self.phone = phone
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent or random.choice(USER_AGENTS)
        self.resend_attempts = resend_attempts
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.success = False
        self.resend_count = 0

    def run(self):
        playwright = None
        browser = None
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=self.headless, proxy=self.proxy)
            context = browser.new_context(user_agent=self.user_agent, viewport=self.viewport)
            page = context.new_page()
            page.goto("https://limited.facebook.com/", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)

            page.locator('a#signup-button').click()
            page.wait_for_selector('input[name="firstname"]', timeout=15000)
            page.locator('input[name="firstname"]').fill("John")
            page.locator('input[name="lastname"]').fill("Doe")
            
            for _ in range(3):
                page.locator('button[data-sigil="touchable multi_step_next"]').click()
                time.sleep(1)
            
            page.locator('input[name="age_step_input"]').fill("25")
            page.locator('button[data-sigil="touchable multi_step_next"]').click()
            page.locator('a[data-sigil="default_birthday_popup_yes"]').click()
            page.locator('input[name="reg_email__"]').fill(self.phone)
            page.locator('button[data-sigil="touchable multi_step_next"]').click()
            page.locator('input[name="sex"][value="1"]').click()
            page.locator('button[data-sigil="touchable multi_step_next"]').click()
            page.locator('input[name="reg_passwd__"]').fill("Password123!")
            page.locator('button[name="submit"]').click()
            page.locator('button[type="submit"][value="OK"]').click()
            
            sms_option = page.locator('div[role="radio"][aria-label*="SMS" i]')
            if sms_option.get_attribute("aria-checked") == "false":
                sms_option.click()
            page.locator('div[role="button"][aria-label="Continue"]').click()
            
            for _ in range(self.resend_attempts):
                try:
                    page.locator('div[role="button"][aria-label="I didn\'t receive the code"]').click()
                    time.sleep(1)
                    page.locator('div[role="button"][aria-label="Resend code to SMS"]').click()
                    self.resend_count += 1
                    time.sleep(2)
                except: break
            
            self.success = True
        except:
            self.success = False
        finally:
            if browser: browser.close()
            if playwright: playwright.stop()
        return self.success


class ResetFBAutomation:
    def __init__(self, phone, headless=True, proxy=None, user_agent=None, resend_attempts=0, viewport=None):
        self.phone = phone
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent or random.choice(USER_AGENTS)
        self.resend_attempts = resend_attempts
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.success = False
        self.resend_count = 0

    def run(self):
        playwright = None
        browser = None
        try:
            playwright = sync_playwright().start()
            browser = playwright.chromium.launch(headless=self.headless, proxy=self.proxy)
            context = browser.new_context(user_agent=self.user_agent, viewport=self.viewport)
            page = context.new_page()
            page.goto("https://limited.facebook.com/login/identify/?ctx=recover", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            page.locator('#identify_search_text_input').fill(self.phone)
            page.locator('#did_submit').click()
            time.sleep(3)
            
            page.locator('a[href*="/recover/initiate/"]:has-text("Try another way")').click()
            time.sleep(2)
            
            last_two = self.phone[-2:]
            sections = page.locator('section._7br1')
            for i in range(sections.count()):
                section = sections.nth(i)
                radio = section.locator('input[type="radio"][name="recover_method"]')
                if radio.get_attribute("value", "").startswith("send_sms:"):
                    if section.locator('label div._52jc._52j9').text_content().strip().endswith(last_two):
                        radio.click()
                        break
            
            page.locator('button[type="submit"][name="reset_action"]:has-text("Continue")').click()
            
            for _ in range(self.resend_attempts):
                try:
                    page.locator('a[href*="/recover/initiate/"]:has-text("Try another way")').click()
                    time.sleep(1)
                    self.resend_count += 1
                except: break
            
            self.success = True
        except:
            self.success = False
        finally:
            if browser: browser.close()
            if playwright: playwright.stop()
        return self.success


# ---------- Main ----------
def main():
    print("=" * 60)
    print("  TERMUX AUTOMATION BOT (Playwright)")
    print("  Instagram | Facebook | New FB | Reset FB")
    print("=" * 60)

    while True:
        file_path = input("\n📁 Enter path to numbers.txt: ").strip()
        if not os.path.isfile(file_path):
            print("❌ File not found.")
            continue
        with open(file_path, "r") as f:
            numbers = [line.strip() for line in f if line.strip()]
        if not numbers:
            print("❌ Empty file.")
            return
        numbers = list(dict.fromkeys(numbers))
        print(f"✅ Loaded {len(numbers)} numbers.")
        break

    platform_map = {
        "1": ("Instagram", InstagramAutomation),
        "2": ("Facebook", FacebookAutomation),
        "3": ("New FB", NewFacebookAutomation),
        "4": ("Reset FB", ResetFBAutomation)
    }
    print("\nSelect platforms (comma separated):")
    for k, (name, _) in platform_map.items():
        print(f"  {k}) {name}")
    
    choice = input("Your choice(s): ").strip()
    selected = [x.strip() for x in choice.split(",") if x.strip() in platform_map]
    platforms = [(platform_map[k][0], platform_map[k][1]) for k in selected]

    proxy_input = input("\n🔌 Proxy (IP:Port:User:Pass) or Enter to skip: ").strip()
    proxy_config = parse_proxy(proxy_input) if proxy_input else None

    workers = int(input("\n👥 Workers (1-5): ").strip())
    resend = int(input("\n🔄 Resend attempts (0-10): ").strip())

    if input("\nStart automation? (y/n): ").strip().lower() != 'y':
        return

    queue = Queue()
    for num in numbers:
        queue.put(num)

    total_tasks = len(numbers) * len(platforms)
    stop_event = threading.Event()
    lock = threading.Lock()
    processed = 0
    success_count = 0
    results = []

    def progress_monitor():
        while not stop_event.is_set():
            with lock:
                sys.stdout.write(f"\r📊 Progress: {processed}/{total_tasks}")
                sys.stdout.flush()
            time.sleep(1)

    threading.Thread(target=progress_monitor, daemon=True).start()

    def worker():
        nonlocal processed, success_count
        while not stop_event.is_set():
            try:
                phone = queue.get(timeout=2)
            except Empty:
                break
            for name, cls in platforms:
                if name in ("Instagram", "New FB", "Reset FB"):
                    automator = cls(phone, headless=True, proxy=proxy_config,
                                   user_agent=random.choice(USER_AGENTS),
                                   resend_attempts=resend)
                else:
                    automator = cls(phone, headless=True, proxy=proxy_config,
                                   user_agent=random.choice(USER_AGENTS))
                
                success = automator.run()
                resend_cnt = getattr(automator, 'resend_count', 0)
                
                with lock:
                    if success:
                        extra = f" [{resend_cnt}]" if resend_cnt > 0 else ""
                        msg = f"[{phone}] {name} ==> ✅ Send Successfully{extra}"
                        success_count += 1
                    else:
                        msg = f"[{phone}] {name} ==> ❌ Failed"
                    print(msg)
                    processed += 1
                    results.append((phone, name, success))
            queue.task_done()
            time.sleep(2)

    threads = []
    for _ in range(min(workers, total_tasks)):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted...")
        stop_event.set()
        sys.exit(0)

    print(f"\n✅ Done! Success: {success_count}/{len(results)}")

if __name__ == "__main__":
    main()