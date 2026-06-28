import os
import time
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USERNAME = os.getenv("USERNAME") or os.getenv("NAUKRI_USERNAME")
PASSWORD = os.getenv("PASSWORD") or os.getenv("NAUKRI_PASSWORD")

if not USERNAME or not PASSWORD:
    raise RuntimeError("USERNAME/PASSWORD not found.")

# ---------------- Chrome ----------------

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-notifications")

print("Launching Chrome...")

driver = webdriver.Chrome(options=options)

try:

    print("Opening login page...")
    driver.set_page_load_timeout(60)
    driver.get("https://www.naukri.com/nlogin/login")
    
    print(driver.current_url)
    print(driver.title)
    
    time.sleep(5)
    
    print(driver.page_source[:1000])

    print("Waiting for username field...")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.ID, "usernameField"))
    )

    print("Entering credentials...")

    driver.find_element(By.ID, "usernameField").send_keys(USERNAME)
    driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)

    print("Clicking Login...")

    driver.find_element(
        By.XPATH,
        "//button[@type='submit' and contains(.,'Login')]"
    ).click()

    print("Waiting for homepage...")

    WebDriverWait(driver, 30).until(
        EC.url_contains("/mnjuser/homepage")
    )

    print("✓ Logged in")

    # Close popup
    try:
        print("Checking popup...")

        close = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//*[contains(@class,'cross-icon') or contains(@class,'crossIcon')]"
                )
            )
        )

        close.click()

    except:
        print("No popup")

    print("Opening profile...")

    profile = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//*[contains(@class,'view-profile')]//a"
            )
        )
    )

    driver.execute_script("arguments[0].click();", profile)

    print("✓ Profile opened")

    print("Waiting for Resume Headline...")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "lazyResumeHead"))
    )

    print("Opening Resume Headline editor...")

    edit_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//div[@id='lazyResumeHead']//span[contains(@class,'edit')]"
            )
        )
    )

    driver.execute_script("arguments[0].click();", edit_btn)

    print("Waiting for textarea...")

    textarea = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located(
            (By.ID, "resumeHeadlineTxt")
        )
    )

    current = textarea.get_attribute("value")

    print("Current Headline:")
    print(repr(current))

    if current.endswith(" "):
        updated = current.rstrip()
        print("Removing trailing space")
    else:
        updated = current + " "
        print("Adding trailing space")

    textarea.clear()
    textarea.send_keys(updated)

    print("Saving...")

    save_btn = WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//button[@type='submit' and normalize-space()='Save']"
            )
        )
    )

    driver.execute_script("arguments[0].click();", save_btn)

    print("✓ Resume headline updated")

    time.sleep(5)

except Exception:

    print("\n========== ERROR ==========\n")

    traceback.print_exc()

    try:
        driver.save_screenshot("error.png")
        print("Saved error.png")
    except:
        pass

    try:
        with open("page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved page.html")
    except:
        pass

    raise

finally:
    driver.quit()
