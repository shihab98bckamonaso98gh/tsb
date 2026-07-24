#!/usr/bin/env python3
"""
Termux Mobile Automation Bot
- Auto‑detects missing dependencies and installs them.
- Supports Instagram, Facebook, New FB, Reset FB.
- Silent mode: only final results and progress bar.
"""

import os
import sys
import time
import random
import threading
import subprocess
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
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/13.2b11866 Mobile/16A366 Safari/605.1.15",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A5370a Safari/604.1",
    "Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; RM-1152) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15254",
    "Mozilla/5.0 (Linux; Android 9; AFTWMST22 Build/PS7233; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.152 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 9 Pro Build/AD1A.240418.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.54 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 9 Build/AD1A.240411.003.A5; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/124.0.6367.54 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; moto g power 5G - 2024 Build/U1UD34.16-62; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/123.0.6312.99 Mobile Safari/537.36"
]

# ---------- Proxy Parsing ----------
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

# ---------- Automation Classes (unchanged) ----------

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

            try:
                didnt_get_code = page.locator('div[role="button"][aria-label="I didn’t get the code"]')
                didnt_get_code.wait_for(state="visible", timeout=15000)
            except PlaywrightTimeout:
                pass

            for _ in range(self.resend_attempts):
                try:
                    didnt_get_code = page.locator('div[role="button"][aria-label="I didn’t get the code"]')
                    if didnt_get_code.count() == 0:
                        break
                    didnt_get_code.click()
                    time.sleep(1)
                    page.wait_for_load_state("networkidle", timeout=5000)
                    resend_btn = page.locator('div[role="button"][aria-label="Resend confirmation code"]')
                    resend_btn.wait_for(state="visible", timeout=5000)
                    resend_btn.click()
                    self.resend_count += 1
                    time.sleep(2)
                except Exception:
                    break

            self.success = True
        except Exception:
            self.success = False
        finally:
            if browser:
                try: browser.close()
                except: pass
            if playwright:
                try: playwright.stop()
                except: pass
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
            page.wait_for_load_state("networkidle", timeout=20000)

            if self._handle_account_not_found(page):
                return False

            self._navigate_to_sms_option(page)

            self.success = self._is_code_entry_page(page)
        except Exception:
            self.success = False
        finally:
            if browser:
                try: browser.close()
                except: pass
            if playwright:
                try: playwright.stop()
                except: pass
        return self.success

    def _handle_account_not_found(self, page):
        try:
            dialog = page.locator('div[role="dialog"]')
            if dialog.count() > 0 and "couldn't find your account" in dialog.inner_text().lower():
                try_again_btn = dialog.locator('div[role="button"]:has-text("Try again")')
                if try_again_btn.count() > 0:
                    try_again_btn.click()
                    time.sleep(1)
                return True
        except:
            pass
        return False

    def _navigate_to_sms_option(self, page):
        for _ in range(6):
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(1)
            if page.locator('h3[aria-label="Choose your account"]').count() > 0:
                accounts = page.locator('div[role="button"][aria-label]:not([aria-label="Back"])')
                if accounts.count() > 0:
                    accounts.first.click()
                    time.sleep(2)
                    continue
            try_another = page.locator('div[role="button"][aria-label="Try another way"]')
            if try_another.count() > 0 and try_another.is_visible():
                try_another.click()
                time.sleep(2)
                continue
            sms_radio = page.locator('div[role="radio"][aria-label*="sms" i]')
            if sms_radio.count() > 0:
                sms_radio.first.click()
                time.sleep(0.5)
                continue_btns = page.locator('div[role="button"][aria-label="Continue"]')
                if continue_btns.count() > 0:
                    continue_btns.last.click()
                    time.sleep(2)
                    page.wait_for_load_state("networkidle", timeout=20000)
                break
            if self._is_code_entry_page(page):
                break
        if not self._is_code_entry_page(page):
            try:
                page.locator('text="Get code via SMS"').first.click()
                time.sleep(1)
                page.locator('div[role="button"][aria-label="Continue"]').last.click()
                time.sleep(2)
                page.wait_for_load_state("networkidle", timeout=10000)
            except:
                pass

    def _is_code_entry_page(self, page):
        return page.locator('input[aria-label="Enter code"]').count() > 0 or \
               page.locator('div[role="button"][aria-label="Didn\'t receive a code?"]').count() > 0


class NewFacebookAutomation:
    FIRST_NAMES = [
        "James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda",
        "William","Elizabeth","David","Barbara","Richard","Susan","Joseph","Jessica",
        "Thomas","Sarah","Charles","Karen","Christopher","Nancy","Daniel","Lisa",
        "Matthew","Betty","Anthony","Helen","Mark","Sandra","Donald","Donna",
        "Steven","Carol","Paul","Ruth","Andrew","Sharon","Joshua","Michelle",
        "Kenneth","Laura","Kevin","Sarah","Brian","Kimberly","George","Deborah",
        "Timothy","Amanda","Ronald","Melissa","Edward","Stephanie","Jason","Rebecca",
        "Jeffrey","Mary","Ryan","Shirley","Jacob","Amy","Gary","Angela",
        "Nicholas","Anna","Eric","Ruth","Jonathan","Brenda","Stephen","Pamela",
        "Larry","Nicole","Justin","Katherine","Scott","Samantha","Brandon","Christine",
        "Benjamin","Catherine","Samuel","Virginia","Gregory","Debra","Alexander","Rachel",
        "Patrick","Janet","Jack","Emma","Dennis","Carolyn","Jerry","Maria",
        "Tyler","Heather","Aaron","Diane","Jose","Julie","Nathan","Joyce",
        "Adam","Evelyn","Henry","Joan","Zachary","Kelly","Tiffany","Denise"
    ]
    LAST_NAMES = [
        "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
        "Rodriguez","Martinez","Hernandez","Lopez","Gonzalez","Wilson","Anderson",
        "Thomas","Taylor","Moore","Jackson","Martin","Lee","Perez","Thompson",
        "White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson","Walker",
        "Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill",
        "Flores","Green","Adams","Nelson","Baker","Hall","Rivera","Campbell",
        "Mitchell","Carter","Roberts","Turner","Phillips","Evans","Collins","Edwards",
        "Stewart","Morris","Murphy","Cook","Rogers","Morgan","Peterson","Cooper",
        "Reed","Bailey","Bell","Howard","Ward","Cox","Diaz","Richardson",
        "Wood","Watson","Brooks","Bennett","Gray","James","Reyes","Cruz",
        "Hughes","Price","Myers","Long","Foster","Sanders","Ross","Powell",
        "Sullivan","Russell","Ortiz","Jenkins","Perry","Butler","Barnes","Fisher"
    ]

    def __init__(self, phone, headless=True, proxy=None, user_agent=None, resend_attempts=0, viewport=None):
        self.phone = phone
        self.headless = headless
        self.proxy = proxy
        self.user_agent = user_agent or random.choice(USER_AGENTS)
        self.resend_attempts = resend_attempts
        self.viewport = viewport or {"width": 1280, "height": 720}
        self.success = False
        self.resend_count = 0
        self.first_name = random.choice(self.FIRST_NAMES)
        self.last_name = random.choice(self.LAST_NAMES)
        self.password = self._generate_password()

    def _generate_password(self):
        import string
        chars = string.ascii_letters + string.digits + "!@#$%^&*()"
        return ''.join(random.choice(chars) for _ in range(random.randint(10, 12)))

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

            create_btn = page.locator('a#signup-button, a[role="button"]#signup-button')
            create_btn.wait_for(state="visible", timeout=10000)
            create_btn.click()
            page.wait_for_selector('input[name="firstname"]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)

            page.locator('input[name="firstname"]').fill(self.first_name)
            time.sleep(0.5)
            page.locator('input[name="lastname"]').fill(self.last_name)
            time.sleep(0.5)
            next_btn = page.locator('button[data-sigil="touchable multi_step_next"]')
            next_btn.click()
            page.wait_for_selector('select[name="birthday_day"]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(0.5)
            next_btn = page.locator('button[data-sigil="touchable multi_step_next"]')
            next_btn.scroll_into_view_if_needed()
            next_btn.click()
            time.sleep(1)
            next_btn = page.locator('button[data-sigil="touchable multi_step_next"]')
            next_btn.scroll_into_view_if_needed()
            next_btn.click()
            page.wait_for_selector('input[name="age_step_input"]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(0.5)
            page.locator('input[name="age_step_input"]').fill(str(random.randint(22, 30)))
            time.sleep(0.5)
            next_btn = page.locator('button[data-sigil="touchable multi_step_next"]')
            next_btn.click()
            page.wait_for_selector('a[data-sigil="default_birthday_popup_yes"]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(0.5)
            page.locator('a[data-sigil="default_birthday_popup_yes"]').click()
            page.wait_for_selector('input[name="reg_email__"]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(0.5)
            page.locator('input[name="reg_email__"]').fill(self.phone)
            time.sleep(0.5)
            next_btn = page.locator('button[data-sigil="touchable multi_step_next"]')
            next_btn.click()
            page.wait_for_selector('input[name="sex"][value="1"]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(0.5)
            gender_val = random.choice(["1", "2"])
            page.locator(f'input[name="sex"][value="{gender_val}"]').click()
            time.sleep(0.5)
            next_btn = page.locator('button[data-sigil="touchable multi_step_next"]')
            next_btn.click()
            page.wait_for_selector('input[name="reg_passwd__"]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(0.5)
            page.locator('input[name="reg_passwd__"]').fill(self.password)
            time.sleep(0.5)
            page.locator('button[name="submit"]').click()
            page.wait_for_selector('button[type="submit"][value="OK"]', timeout=20000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(1)
            page.locator('button[type="submit"][value="OK"]').click()
            page.wait_for_selector('div[role="radio"][aria-label*="SMS" i]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(1)
            sms_option = page.locator('div[role="radio"][aria-label*="SMS" i]')
            if sms_option.get_attribute("aria-checked") == "false":
                sms_option.click()
                time.sleep(0.5)
            page.locator('div[role="button"][aria-label="Continue"]').click()
            page.wait_for_selector('input[inputmode="numeric"]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(1)

            for _ in range(self.resend_attempts):
                try:
                    didnt_receive = page.locator('div[role="button"][aria-label="I didn\'t receive the code"]')
                    if didnt_receive.count() == 0:
                        break
                    didnt_receive.click()
                    time.sleep(1)
                    page.wait_for_load_state("networkidle", timeout=5000)
                    resend_btn = page.locator('div[role="button"][aria-label="Resend code to SMS"]')
                    resend_btn.wait_for(state="visible", timeout=5000)
                    resend_btn.click()
                    self.resend_count += 1
                    time.sleep(2)
                except Exception:
                    break

            time.sleep(5)
            self.success = True
        except Exception:
            self.success = False
        finally:
            if browser:
                try: browser.close()
                except: pass
            if playwright:
                try: playwright.stop()
                except: pass
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
            page.goto(
                "https://limited.facebook.com/login/identify/?ctx=recover&c=https%3A%2F%2Flimited.facebook.com%2F&multiple_results=0&ars=facebook_login&from_login_screen=0&lwv=100&wtsid=rdr_03SBV2rCp90MeoDPA&_rdr",
                timeout=30000
            )
            page.wait_for_load_state("networkidle", timeout=10000)
            page.locator('#identify_search_text_input').fill(self.phone)
            time.sleep(0.5)
            page.locator('#did_submit').click()
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)

            try:
                page.locator('a[href*="/recover/initiate/"]:has-text("Try another way")').wait_for(state="visible", timeout=10000)
                page.locator('a[href*="/recover/initiate/"]:has-text("Try another way")').click()
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(1)
            except PlaywrightTimeout:
                return False

            page.wait_for_selector('input[name="recover_method"]', timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            time.sleep(0.5)

            def select_sms_option(page, phone):
                last_two = phone[-2:]
                sections = page.locator('section._7br1')
                for i in range(sections.count()):
                    section = sections.nth(i)
                    radio = section.locator('input[type="radio"][name="recover_method"]')
                    if radio.count() == 0:
                        continue
                    value = radio.get_attribute("value")
                    if value and value.startswith("send_sms:"):
                        label_div = section.locator('label div._52jc._52j9')
                        if label_div.count() > 0 and label_div.first.text_content().strip().endswith(last_two):
                            radio.click()
                            return True
                return False

            if not select_sms_option(page, self.phone):
                return False

            page.locator('button[type="submit"][name="reset_action"]:has-text("Continue")').click()
            page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(1)

            try:
                page.locator('a[href*="/recover/initiate/"]:has-text("Try another way")').wait_for(state="visible", timeout=10000)
            except PlaywrightTimeout:
                pass

            for _ in range(self.resend_attempts):
                try:
                    try_another = page.locator('a[href*="/recover/initiate/"]:has-text("Try another way")')
                    if try_another.count() == 0:
                        break
                    try_another.click()
                    page.wait_for_load_state("networkidle", timeout=10000)
                    time.sleep(1)
                except Exception:
                    break

                page.wait_for_selector('input[name="recover_method"]', timeout=15000)
                page.wait_for_load_state("networkidle", timeout=10000)
                time.sleep(0.5)

                if not select_sms_option(page, self.phone):
                    break

                page.locator('button[type="submit"][name="reset_action"]:has-text("Continue")').click()
                page.wait_for_load_state("networkidle", timeout=15000)
                time.sleep(1)

                try:
                    page.locator('a[href*="/recover/initiate/"]:has-text("Try another way")').wait_for(state="visible", timeout=10000)
                    self.resend_count += 1
                except PlaywrightTimeout:
                    pass

            time.sleep(5)
            self.success = True
        except Exception:
            self.success = False
        finally:
            if browser:
                try: browser.close()
                except: pass
            if playwright:
                try: playwright.stop()
                except: pass
        return self.success


# ---------- Dependency Checker (runs automatically) ----------
def run_cmd(cmd):
    """Run a shell command, print output, return True if successful."""
    print(f"  ➤ {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=False, text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(result.stdout.strip())
        return result.returncode == 0
    except Exception as e:
        print(f"  ✖ Error: {e}")
        return False

def check_and_install_dependencies():
    """Ensure Playwright and Chromium are available. Install if missing."""
    print("\n🔍 Checking dependencies...")

    # 1. Check if playwright module is importable
    try:
        import playwright
        print("  ✅ playwright Python module found.")
    except ImportError:
        print("  ⚠️ playwright not installed. Installing now...")
        mirrors = [
            "https://pypi.org/simple",
            "https://pypi.tuna.tsinghua.edu.cn/simple",
            "https://mirrors.aliyun.com/pypi/simple"
        ]
        installed = False
        for mirror in mirrors:
            if run_cmd(f"pip install -i {mirror} playwright"):
                installed = True
                break
        if not installed:
            print("❌ Failed to install playwright. Check internet connection.")
            sys.exit(1)

    # 2. Check if Chromium browser is usable
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        print("  ✅ Chromium browser works.")
        return
    except Exception as e:
        print(f"  ⚠️ Chromium not ready: {e}")
        print("  ⬇️ Attempting to install Chromium...")
        if run_cmd("playwright install chromium"):
            print("  ✅ Chromium installed successfully.")
        else:
            print("  ⚠️ Trying to install system dependencies...")
            if run_cmd("playwright install-deps chromium"):
                print("  ✅ Dependencies installed.")
            else:
                print("❌ Could not install Chromium. Please run manually:")
                print("   playwright install chromium")
                print("   or inside proot-distro: playwright install-deps chromium")
                sys.exit(1)


# ---------- Main Terminal Tool ----------
def main():
    # Run dependency checker first
    check_and_install_dependencies()

    print("=" * 60)
    print("  TERMUX MOBILE AUTOMATION (Silent Mode)")
    print("=" * 60)

    # 1. Numbers file
    while True:
        file_path = input("\n📁 Enter path to numbers.txt: ").strip()
        if not os.path.isfile(file_path):
            print("❌ File not found.")
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            numbers = [line.strip() for line in f if line.strip()]
        if not numbers:
            print("❌ Empty file.")
            return
        numbers = list(dict.fromkeys(numbers))
        print(f"✅ Loaded {len(numbers)} numbers.")
        break

    # 2. Platforms
    platform_map = {
        "1": ("Instagram", InstagramAutomation),
        "2": ("Facebook", FacebookAutomation),
        "3": ("New FB", NewFacebookAutomation),
        "4": ("Reset FB", ResetFBAutomation)
    }
    print("\nSelect platforms (comma separated, e.g. 1,2,4):")
    print("  1) Instagram")
    print("  2) Facebook")
    print("  3) New FB")
    print("  4) Reset FB")
    while True:
        choice = input("Your choice(s): ").strip()
        if not choice:
            print("❌ No selection.")
            return
        selected = [x.strip() for x in choice.split(",") if x.strip() in platform_map]
        if not selected:
            print("❌ Invalid. Use 1-4.")
            continue
        platforms = [(platform_map[k][0], platform_map[k][1]) for k in selected]
        print(f"✅ Using: {', '.join(p[0] for p in platforms)}")
        break

    # 3. Proxy (optional)
    proxy_input = input("\n🔌 Proxy (IP:Port:User:Pass) or Enter to skip: ").strip()
    proxy_config = parse_proxy(proxy_input) if proxy_input else None
    if proxy_config:
        print(f"✅ Proxy set: {proxy_input}")
    else:
        print("ℹ️ No proxy.")

    # 4. Workers
    while True:
        try:
            workers = int(input("\n👥 Workers (1-10): ").strip())
            if 1 <= workers <= 10:
                break
            print("❌ Between 1 and 10.")
        except ValueError:
            print("❌ Invalid number.")

    # 5. Resend attempts
    while True:
        try:
            resend = int(input("\n🔄 Resend attempts (0-10): ").strip())
            if 0 <= resend <= 10:
                break
            print("❌ Between 0 and 10.")
        except ValueError:
            print("❌ Invalid number.")

    # Summary
    print("\n" + "-" * 40)
    print(f"  Numbers: {len(numbers)}")
    print(f"  Platforms: {', '.join(p[0] for p in platforms)}")
    print(f"  Proxy: {'Yes' if proxy_config else 'No'}")
    print(f"  Workers: {workers}")
    print(f"  Resend attempts: {resend}")
    print("-" * 40)
    if input("\nStart automation? (y/n): ").strip().lower() != 'y':
        print("Aborted.")
        return

    # Prepare queue
    queue = Queue()
    for num in numbers:
        queue.put(num)

    total_tasks = len(numbers) * len(platforms)
    stop_event = threading.Event()
    lock = threading.Lock()
    processed = 0
    success_count = 0
    results = []

    # Progress monitor (updates bottom line every second)
    def progress_monitor():
        while not stop_event.is_set():
            with lock:
                sys.stdout.write(f"\r📊 Progress: {processed}/{total_tasks}")
                sys.stdout.flush()
            time.sleep(1)
        with lock:
            sys.stdout.write("\r" + " " * 40 + "\r")
            sys.stdout.flush()

    monitor_thread = threading.Thread(target=progress_monitor, daemon=True)
    monitor_thread.start()

    def worker():
        nonlocal processed, success_count
        while not stop_event.is_set():
            try:
                phone = queue.get(timeout=2)
            except Empty:
                break

            for name, AutomationClass in platforms:
                if stop_event.is_set():
                    break
                if name in ("Instagram", "New FB", "Reset FB"):
                    automator = AutomationClass(
                        phone=phone,
                        headless=True,
                        proxy=proxy_config,
                        user_agent=random.choice(USER_AGENTS),
                        resend_attempts=resend
                    )
                else:  # Facebook
                    automator = AutomationClass(
                        phone=phone,
                        headless=True,
                        proxy=proxy_config,
                        user_agent=random.choice(USER_AGENTS)
                    )

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
            time.sleep(1)

    # Launch workers
    threads = []
    for _ in range(min(workers, total_tasks)):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    try:
        for t in threads:
            t.join()
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted, stopping...")
        stop_event.set()
        for t in threads:
            t.join(timeout=3)
        sys.exit(0)

    stop_event.set()
    monitor_thread.join(timeout=1)

    # Final report
    print("\n" + "=" * 60)
    print("  AUTOMATION COMPLETED")
    print(f"  Total attempts: {len(results)}")
    print(f"  Success: {success_count}")
    print(f"  Failed: {len(results) - success_count}")
    print("=" * 60)

    # Save report
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = f"report_{timestamp}.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=== Automation Report ===\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Numbers file: {file_path}\n")
        f.write(f"Platforms: {', '.join(p[0] for p in platforms)}\n")
        f.write(f"Proxy: {proxy_input if proxy_config else 'None'}\n")
        f.write(f"Workers: {workers}  Resend attempts: {resend}\n\n")
        f.write(f"Total: {len(results)}  Success: {success_count}  Failed: {len(results)-success_count}\n\n")
        for phone, name, ok in results:
            status = "Success" if ok else "Failed"
            f.write(f"{phone} [{name}] -> {status}\n")
    print(f"📁 Report saved: {report_file}")

if __name__ == "__main__":
    main()