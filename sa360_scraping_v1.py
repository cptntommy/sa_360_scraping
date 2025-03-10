import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up Chrome WebDriver to attach to an existing session
options = webdriver.ChromeOptions()
options.debugger_address = "127.0.0.1:9222"  # Connect to an existing Chrome session

driver = webdriver.Chrome(options=options)

# Navigate to SA360. if using existing session with previous scrape, just different filters, then can comment out
driver.get("https://searchads.google.com/")

# wait for user to log in & apply filters
input("log in, apply filters to show desired templates, then press Enter to continue...")

# Define XPath & Selectors
template_xpath_pattern = "/html/body/div[1]/root/div/div[1]/div[2]/div/div[3]/div/div/awsm-child-content/content-main/div/div[2]/entitybuilder-root/base-root/div/div[2]/div[1]/view-loader/entity-builder-template-view/tableview/div[6]/ess-table/ess-particle-table/div[1]/div/div[2]/div[{}]/div/div/ess-cell[1]/template-name-cell/div/div/span"
settings_cog_css_pattern = "div.ess-table-canvas > div:nth-child({}) > div > div > ess-cell:nth-child(1) > edit-icon-cell > material-button"
continue_button_class = "save-button"
final_url_xpath = "/html/body/div[1]/root/div/div[1]/div[2]/div/div[3]/div/div/awsm-child-content/content-main/div/div[2]/entitybuilder-root/base-root/div/div[2]/div[1]/view-loader/keyword-template-construction-host/guided-flow-wrapper/div/main-flow-stepper/ess-stepper/material-stepper/div[2]/div/step-loader/keyword-template-construction/template-attributes-construction/guided-flow-step/div[1]/construction-layout/construction-layout-engine/div/div/div[2]/div[3]/lazy-plugin/div/dynamic-component/formula/overridable-plugin-panel/construction-panel/div/construction-plugin-panel/material-expansionpanel/div/div[2]/div/div[1]/div/div/div[2]/div/plugin-content/div/formula-editor/formula-input/template-custom-column-inline-input/div/formula-editor/div/div[2]"
back_button_xpath = "/html/body/div[1]/root/div/div[1]/awsm-app-bar/div/div[2]/material-button"
status_xpath = "/html/body/div[1]/root/div/div[1]/div[2]/div/div[3]/div/div/awsm-child-content/content-main/div/div[2]/entitybuilder-root/base-root/div/div[2]/div[1]/view-loader/keyword-template-construction-host/guided-flow-wrapper/div/main-flow-stepper/ess-stepper/material-stepper/div[2]/div/step-loader/template-settings-construction/guided-flow-step/div[1]/construction-layout/construction-layout-engine/div/div/div[2]/div[1]/lazy-plugin/div/dynamic-component/template-name-plugin/construction-panel/div/construction-plugin-panel/material-expansionpanel/div/div[2]/div/div[1]/div/div/div[1]/div"

# store progress in a .txt file to resume from last template
progress_file = "sa360_progress.txt"  # if starting from scratch on new page, change value in file to 2

def get_last_processed_template():
    """ Reads the last processed template index from the progress file. """
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            last_line = f.readlines()[-1].strip()
            return int(last_line) if last_line.isdigit() else 1
    return 1  # default to row 2 if no progress is recorded

def save_progress(template_index):
    """ Saves the current template index to the progress file. """
    with open(progress_file, "w") as f:
        f.write(str(template_index))

# open .txt file for logging results. if file exists appends rows to bottom.
results_file = "test_sa360_results.txt"
with open(results_file, "a") as file:
    file.write("Template Name | Final URL\n")
    print("\n Starting SA360 Scraping...\n")

    # resume from last processed template
    last_processed = get_last_processed_template()
    print(f"🔄 Resuming from template {last_processed}...\n")

    # loop through first xxx templates on page 1 - table rows start from 2, so 100 rows will be 2,102
    for i in range(last_processed, 20):
        try:
            print(f"\n🔄 Processing template {i}...")
            time.sleep(1)
            template_xpath = template_xpath_pattern.format(i)

            # scroll in increments of 20 rows for large row numbers
            if i >= 20:
                scroll_steps = list(range(10, i + 1, 20))  # Generates 10, 30, 50, etc.
                for step in scroll_steps:
                    step_xpath = template_xpath_pattern.format(step)
                    try:
                        row_element = driver.find_element(By.XPATH, step_xpath)
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row_element)
                        time.sleep(0.3)  # allow lazy loading
                        print(f"✅ Scrolled to row {step}.")
                    except:
                        print(f"⚠️ Could not find row {step}, continuing to next step.")

            # wait for template name to be visible
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, template_xpath)))
            template_name = driver.find_element(By.XPATH, template_xpath).text
            print(f"✅ Template Name: {template_name}")

            # ensure settings cog is visible before clicking
            settings_cog_css = settings_cog_css_pattern.format(i)  # Build row-specific selector
            settings_cog = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, settings_cog_css)))
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", settings_cog)
            time.sleep(0.3)  # Short delay before clicking
            settings_cog.click()
            print("⚙️ Clicked settings cog.")

            # **Wait until the 'Status' field is visible before clicking 'Continue'**
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, status_xpath))
            )
            print("✅ field is visible. now clicking 'Continue'.")

            # **Click 'Continue'**
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, continue_button_class)))
            driver.find_element(By.CLASS_NAME, continue_button_class).click()
            print("➡️ Clicked 'Continue'.")

            # **Ensure the Final URL field is visible before proceeding**
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, final_url_xpath)))
            final_url = driver.find_element(By.XPATH, final_url_xpath).text
            print(f"🔗 Final URL: {final_url}")

            # Save to file
            file.write(f"{template_name} | {final_url}\n")

            # Save progress
            save_progress(i)

            # Click Back button
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, back_button_xpath)))
            driver.find_element(By.XPATH, back_button_xpath).click()
            print("⬅️ clicked 'Back' button. returning to main list...")

        except Exception as e:
            print(f"❌ Error processing template {i - 1}: {e}")

            # **Handle page crashes - refresh & continue** NOT WORKING
            if "chrome has stopped" in str(e).lower() or "tab crashed" in str(e).lower():
                print("⚠️ Tab crashed! Refreshing page...")
                driver.refresh()
                time.sleep(10)  # Allow time for the page to reload
                print("🔄 Page refreshed. Resuming...")
                continue  # Skip to the next loop iteration

# Close driver after completion
print("\n✅ Scraping completed! Results saved to 'sa360_results.txt'.")
# Delete the progress file after completion
if os.path.exists(progress_file):
    os.remove(progress_file)
    print(f"\n🗑️ Progress file '{progress_file}' deleted. Ready for a fresh start next time.")

driver.quit()
