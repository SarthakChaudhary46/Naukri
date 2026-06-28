from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

USERNAME = os.getenv("USERNAME") or os.getenv("NAUKRI_USERNAME")
PASSWORD = os.getenv("PASSWORD") or os.getenv("NAUKRI_PASSWORD")

if not USERNAME or not PASSWORD:
    raise RuntimeError("USERNAME and PASSWORD must be provided via environment variables")

# ---------------- Chrome ----------------
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-notifications")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # ---------------- Login ----------------
    driver.get("https://www.naukri.com/nlogin/login")

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "usernameField"))
    )

    driver.find_element(By.ID, "usernameField").send_keys(USERNAME)
    driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)

    driver.find_element(
        By.XPATH,
        "//button[@type='submit' and contains(.,'Login')]"
    ).click()

    WebDriverWait(driver, 30).until(
        EC.url_contains("/mnjuser/homepage")
    )

    print("✓ Logged in successfully")

    # ---------------- Close popup if present ----------------
    try:
        close = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH,
                 "//*[contains(@class,'cross-icon') or contains(@class,'crossIcon')]")
            )
        )
        close.click()
    except:
        pass

    # ---------------- Open Profile ----------------
    profile = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH,
             "//*[contains(@class,'view-profile')]//a")
        )
    )

    driver.execute_script("arguments[0].click();", profile)

    print("✓ Profile opened")

    # Wait for profile page
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "lazyResumeHead"))
    )

    # ---------------- Click Resume Headline Edit ----------------
    edit_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[@id='lazyResumeHead']//span[contains(@class,'edit')]"
            )
        )
    )

    driver.execute_script("arguments[0].click();", edit_btn)

    print("✓ Resume headline editor opened")

    # ---------------- Wait for textarea ----------------
    textarea = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(
            (By.ID, "resumeHeadlineTxt")
        )
    )

    current = textarea.get_attribute("value")

    print("Current Headline:")
    print(repr(current))

    # ---------------- Toggle trailing space ----------------
    if current.endswith(" "):
        updated = current.rstrip()
        print("Removing trailing space")
    else:
        updated = current + " "
        print("Adding trailing space")

    # Clear existing text
    textarea.clear()

    # Type updated headline
    textarea.send_keys(updated)

    time.sleep(1)

    # ---------------- Save ----------------
    save_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[@type='submit' and normalize-space()='Save']"
            )
        )
    )

    driver.execute_script("arguments[0].click();", save_btn)

    print("✓ Resume headline updated successfully")

    time.sleep(5)

except Exception as e:
    print("\nERROR:")
    print(e)

finally:
    driver.quit()