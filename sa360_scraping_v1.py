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

# New XPath pattern for keywords
keyword_xpath_pattern = "/html/body/div[1]/root/div/div[1]/div[2]/div/div[3]/div/div/awsm-child-content/content-main/div/div/entitybuilder-root/base-root/div/div[2]/div[1]/view-loader/keyword-template-construction-host/guided-flow-wrapper/div/main-flow-stepper/ess-stepper/material-stepper/div[2]/div/step-loader/keyword-template-construction/template-attributes-construction/guided-flow-step/div[1]/construction-layout/construction-layout-engine/div/div/div[2]/div[1]/lazy-plugin/div/dynamic-component/keyword-template-text/overridable-plugin-panel/construction-panel/div/construction-plugin-panel/material-expansionpanel/div/div[2]/div/div[1]/div/div/div[2]/div/plugin-content/div/keyword-template-text-editor/div/div[{}]/div/template-custom-column-inline-input/div/formula-editor/div/div[2]"

# store progress in a .txt file to resume from last template
progress_file = "sa360_progress.txt"


def get_last_processed_template():
    """ Reads the last processed template index from the progress file. """
    if os.path.exists(progress_file):
        with open(progress_file, "r") as f:
            last_line = f.readlines()[-1].strip()
            return int(last_line) if last_line.isdigit() else 1
    return 2  # default to row 2 if no progress is recorded


def save_progress(template_index):
    """ Saves the current template index to the progress file. """
    with open(progress_file, "w") as f:
        f.write(str(template_index))


# Check for existing progress and ask user for start row
start_row = 2
if os.path.exists(progress_file):
    last_processed = get_last_processed_template()
    use_progress = input(
        f"Found a previous session at row {last_processed}. Do you want to continue from there? (y/n): ").lower()
    if use_progress == 'y':
        start_row = last_processed
    else:
        start_row = int(input("Enter the row number to start from (table starts at row 2): "))
else:
    start_row = int(input("Enter the row number to start from (table starts at row 2): "))

# Ask user for number of rows to scrape
end_row = int(input("Enter the number of rows to scrape: ")) + start_row

# open .txt file for logging results. if file exists appends rows to bottom.
results_file = "test_sa360_results.txt"
with open(results_file, "a") as file:
    file.write("Template Name | Final URL | Keywords\n")
    print("\n Starting SA360 Scraping...\n")
    print(f"🔄 Starting from row {start_row} and scraping {end_row - start_row} rows...\n")

    # loop through templates based on user input
    for i in range(start_row, end_row):
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

            # Simple solution: Click twice for the first row
            if i == start_row:
                print("⚙️ First row - clicking settings cog twice...")
                settings_cog.click()
                time.sleep(0.5)  # Short delay between clicks

                # Try to find and click it again
                try:
                    settings_cog = driver.find_element(By.CSS_SELECTOR, settings_cog_css)
                    settings_cog.click()
                    print("⚙️ Second click on settings cog.")
                except:
                    # If second click fails, that might mean first click worked
                    print("⚙️ Second click not needed (first click likely worked).")
            else:
                settings_cog.click()
                print("⚙️ Clicked settings cog.")

            # **Wait until the 'Status' field is visible before clicking 'Continue'**
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, status_xpath))
                )
                print("✅ Status field is visible. now clicking 'Continue'.")
            except:
                # If we can't find the status field, maybe we need manual intervention
                if i == start_row:
                    print("⚠️ Status field not found after clicking settings cog")
                    input("❗ Please click the settings cog manually if needed, then press Enter to continue...")

            # **Click 'Continue'**
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, continue_button_class)))
            driver.find_element(By.CLASS_NAME, continue_button_class).click()
            print("➡️ Clicked 'Continue'.")

            # **Scrape all keywords**
            keywords = []
            keyword_index = 1
            max_attempts = 30  # Maximum number of keywords to check

            print("🔍 Scraping keywords...")
            for keyword_index in range(1, max_attempts + 1):
                try:
                    keyword_xpath = keyword_xpath_pattern.format(keyword_index)
                    # Short timeout for checking if keyword exists
                    keyword_element = WebDriverWait(driver, 2).until(
                        EC.presence_of_element_located((By.XPATH, keyword_xpath))
                    )
                    keyword_text = keyword_element.text
                    keywords.append(keyword_text)
                    print(f"✅ Keyword {keyword_index}: {keyword_text}")
                except:
                    # If we can't find any more keywords, break the loop
                    print(f"🔍 No more keywords found after {keyword_index - 1} keywords.")
                    break

            # Join all keywords with a separator
            keywords_text = " | ".join(keywords)
            print(f"📝 Found {len(keywords)} keywords.")

            # **Ensure the Final URL field is visible before proceeding**
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, final_url_xpath)))
            final_url = driver.find_element(By.XPATH, final_url_xpath).text
            print(f"🔗 Final URL: {final_url}")

            # Save to file
            file.write(f"{template_name} | {final_url} | {keywords_text}\n")

            # Save progress
            save_progress(i)

            # Click Back button
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, back_button_xpath)))
            driver.find_element(By.XPATH, back_button_xpath).click()
            print("⬅️ clicked 'Back' button. returning to main list...")

            # Add a slight delay after returning to the list, especially for the first iteration
            if i == start_row:
                time.sleep(1)

        except Exception as e:
            print(f"❌ Error processing template {i}: {e}")

            # Ask user if they want to retry this row or continue to next
            retry = input(f"❓ Error on row {i}. Retry this row? (y/n): ").lower()
            if retry == 'y':
                i -= 1  # Adjust index to retry the same row
                continue

# Close driver after completion
print("\n✅ Scraping completed! Results saved to 'sa360_results.txt'.")
# Ask user if they want to delete the progress file
delete_progress = input("\n🗑️ Do you want to delete the progress file for a fresh start next time? (y/n): ").lower()
if delete_progress == 'y' and os.path.exists(progress_file):
    os.remove(progress_file)
    print(f"\n🗑️ Progress file '{progress_file}' deleted. Ready for a fresh start next time.")
else:
    print(f"\n💾 Progress file '{progress_file}' preserved for next session.")

driver.quit()