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

# New XPath pattern for keyword dropdown values
keyword_dropdown_xpath_pattern = "/html/body/div[1]/root/div/div[1]/div[2]/div/div[3]/div/div/awsm-child-content/content-main/div/div[2]/entitybuilder-root/base-root/div/div[2]/div[1]/view-loader/keyword-template-construction-host/guided-flow-wrapper/div/main-flow-stepper/ess-stepper/material-stepper/div[2]/div/step-loader/keyword-template-construction/template-attributes-construction/guided-flow-step/div[1]/construction-layout/construction-layout-engine/div/div/div[2]/div[1]/lazy-plugin/div/dynamic-component/keyword-template-text/overridable-plugin-panel/construction-panel/div/construction-plugin-panel/material-expansionpanel/div/div[2]/div/div[1]/div/div/div[2]/div/plugin-content/div/keyword-template-text-editor/div/div[{}]/div/div/match-type-select/material-dropdown-select/dropdown-button/div/span"

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

# Ask user for custom output txt file path
results_file = str(input("Enter the name of your export file. Don't forget the .txt extension!: "))

# Perform a test write to verify file access
try:
    with open(results_file, "a") as test_file:
        test_file.write("# Test line - Script started\n")
        print(f"✅ Test write successful to {results_file}")
except Exception as e:
    print(f"❌ Error during test write to {results_file}: {e}")
    alt_filename = f"sa360_export_{int(time.time())}.txt"
    print(f"⚠️ Will attempt to use alternative filename: {alt_filename}")
    results_file = alt_filename

# open .txt file for logging results. if file exists appends rows to bottom.
with open(results_file, "a") as file:
    # Updated header with paired columns for keywords and match types
    file.write("Template Name | Final URL")
    # Create headers for up to 30 keyword pairs (adjust as needed)
    for j in range(1, 31):
        file.write(f" | Keyword {j} | Match Type {j}")
    file.write("\n")
    file.flush()  # Force write to disk after headers

    print("\n Starting SA360 Scraping...\n")
    print(f"🔄 Starting from row {start_row} and scraping {end_row - start_row} rows...\n")

    # loop through templates based on user input
    for i in range(start_row, end_row):
        try:
            print(f"\n🔄 Processing template {i - 1}...")
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

            # Check if template_name is empty or blank, retry up to 3 times
            max_retries = 3
            retry_count = 0
            while (not template_name or template_name.strip() == "") and retry_count < max_retries:
                retry_count += 1
                print(f"⚠️ Empty template name detected. Retry attempt {retry_count}/{max_retries}...")
                time.sleep(2)  # Wait a bit before retrying
                template_name = driver.find_element(By.XPATH, template_xpath).text
                print(f"✅ Retry {retry_count} - Template Name: {template_name}")

            # If template name is still empty after retries, ask user what to do
            if not template_name or template_name.strip() == "":
                print("❌ Failed to get template name after multiple attempts")
                user_choice = input(
                    "Template name is empty. (s)kip this row, (c)ontinue anyway, or (m)anually enter name? (s/c/m): ").lower()
                if user_choice == 's':
                    print(f"⏭️ Skipping row {i}")
                    continue  # Skip to the next iteration
                elif user_choice == 'm':
                    template_name = input("Enter the template name manually: ")
                    if not template_name:
                        print(f"⏭️ No name entered. Skipping row {i}")
                        continue  # Skip if user didn't enter anything
                else:
                    template_name = f"Unknown_Template_{i}"
                    print(f"⚠️ Continuing with placeholder name: {template_name}")

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

            # **Improved Keyword Scraping**
            print("🔍 Scraping keywords and match types...")
            keywords = []
            keyword_match_types = []
            max_attempts = 100
            wait = WebDriverWait(driver, 15)  # Increased timeout for better reliability

            # Try multiple approaches to find keywords
            keyword_found = False

            # Approach 1: Try to find all keyword containers at once
            try:
                # Look for keyword containers using a more general CSS selector
                keyword_containers = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR,
                                                         "keyword-template-text-editor > div > div"))
                )

                print(f"✅ Found {len(keyword_containers)} potential keyword containers")

                # Process each container up to max_attempts
                for idx, container in enumerate(keyword_containers[:max_attempts], 1):
                    try:
                        # Method 1: Try to find using the expected structure
                        try:
                            keyword_element = container.find_element(By.CSS_SELECTOR,
                                                                     "template-custom-column-inline-input > div > formula-editor > div > div:nth-child(2)")
                            keyword_text = keyword_element.text
                        except:
                            # Method 2: If structure doesn't match, try to get direct text
                            keyword_text = container.text
                            if not keyword_text or keyword_text.strip() == "":
                                # Try another approach to extract text
                                try:
                                    keyword_text = container.find_element(By.CSS_SELECTOR, "div").text
                                except:
                                    keyword_text = "Unknown"

                        # Try to find match type within same container
                        try:
                            match_type_element = container.find_element(By.CSS_SELECTOR,
                                                                        "div > match-type-select > material-dropdown-select > dropdown-button > div > span")
                            match_type = match_type_element.text
                        except:
                            # Default match type if not found
                            match_type = "Unknown"

                        # Only add valid keywords
                        if keyword_text and keyword_text.strip() != "":
                            keywords.append(keyword_text)
                            keyword_match_types.append(match_type)
                            print(f"✅ Keyword {idx}: {keyword_text} (Match Type: {match_type})")
                            keyword_found = True
                    except Exception as e:
                        print(f"⚠️ Error processing keyword container {idx}: {str(e)}")
                        # If container has any text at all, try to capture it
                        try:
                            if container.text and container.text.strip() != "":
                                keywords.append(container.text)
                                keyword_match_types.append("Unknown")
                                print(f"✅ Salvaged Keyword {idx}: {container.text} (Match Type: Unknown)")
                                keyword_found = True
                        except:
                            pass

                print(f"📝 Found {len(keywords)} keywords with match types using container method.")
            except Exception as e:
                print(f"⚠️ Container method failed: {str(e)}")

            # Approach 2: Fall back to original XPath method if no keywords found
            if not keyword_found:
                print("Falling back to original keyword scraping method...")
                for keyword_index in range(1, max_attempts + 1):
                    try:
                        keyword_xpath = keyword_xpath_pattern.format(keyword_index)
                        # Shorter timeout with exponential backoff
                        for attempt in range(3):  # Try up to 3 times with increasing waits
                            try:
                                wait_time = 1 * (2 ** attempt)  # 1, 2, 4 seconds
                                keyword_element = WebDriverWait(driver, wait_time).until(
                                    EC.presence_of_element_located((By.XPATH, keyword_xpath))
                                )
                                break
                            except:
                                if attempt == 2:  # Last attempt failed
                                    raise

                        keyword_text = keyword_element.text
                        keywords.append(keyword_text)

                        # Get the match type dropdown value for this keyword
                        try:
                            dropdown_xpath = keyword_dropdown_xpath_pattern.format(keyword_index)
                            dropdown_value = WebDriverWait(driver, 1).until(
                                EC.presence_of_element_located((By.XPATH, dropdown_xpath))
                            ).text
                            keyword_match_types.append(dropdown_value)
                            print(f"✅ Keyword {keyword_index}: {keyword_text} (Match Type: {dropdown_value})")
                        except:
                            keyword_match_types.append("Unknown")
                            print(f"✅ Keyword {keyword_index}: {keyword_text} (Match Type: Unknown)")
                    except:
                        # If we can't find any more keywords, break the loop
                        print(f"🔍 No more keywords found after {keyword_index - 1} keywords.")
                        break

            # Optimize Final URL scraping
            print("🔍 Looking for Final URL...")
            final_url = ""

            # Try different strategies to find the final URL with exponential backoff
            final_url_css = "formula-editor > div > div:nth-child(2)"  # Simplified CSS selector
            final_url_selectors = [
                (By.XPATH, final_url_xpath),  # Original XPath as fallback
                (By.CSS_SELECTOR, final_url_css)  # Try CSS first
            ]

            for selector_type, selector in final_url_selectors:
                for attempt in range(3):  # Try up to 3 times with increasing waits
                    try:
                        wait_time = 2 * (2 ** attempt)  # 2, 4, 8 seconds
                        url_element = WebDriverWait(driver, wait_time).until(
                            EC.presence_of_element_located((selector_type, selector))
                        )
                        final_url = url_element.text
                        print(f"🔗 Found Final URL using {selector_type}: {final_url}")
                        break  # Break out of attempt loop
                    except:
                        if attempt == 2:  # Last attempt for this selector
                            continue  # Try next selector
                        continue

                if final_url:  # If URL was found
                    break  # Break out of selector loop

            if not final_url:
                print("⚠️ Final URL not found using standard methods")
                final_url = input("Please enter the Final URL manually or press Enter to skip: ")
                if not final_url:
                    final_url = "URL_NOT_FOUND"

            # Enhanced data logging
            print(f"Debug - Keywords found: {len(keywords)}")
            print(f"Debug - Match types found: {len(keyword_match_types)}")

            # Save to file with paired keyword and match type columns - WITH ENHANCED ERROR HANDLING
            try:
                row_data = f"{template_name} | {final_url}"

                # Add each keyword and its match type as adjacent columns
                for j in range(len(keywords)):
                    kw = keywords[j] if j < len(keywords) else ""
                    mt = keyword_match_types[j] if j < len(keyword_match_types) else ""
                    # Escape any pipe characters in the keyword or match type to prevent column misalignment
                    kw = kw.replace("|", "\\|") if kw else ""
                    mt = mt.replace("|", "\\|") if mt else ""
                    row_data += f" | {kw} | {mt}"

                # Fill empty cells for any remaining columns
                for j in range(len(keywords), 30):
                    row_data += f" |  | "

                print(f"Debug - Writing row data with length: {len(row_data)}")
                file.write(row_data + "\n")
                file.flush()  # Force write to disk
                print(f"✅ Successfully wrote data for template: {template_name}")
            except Exception as e:
                print(f"❌ Error writing to file: {e}")
                # Attempt emergency save of the data
                try:
                    emergency_file_name = f"emergency_{results_file}"
                    with open(emergency_file_name, "a") as emergency_file:
                        emergency_file.write(f"{template_name} | {final_url} | {', '.join(keywords)}\n")
                        print(f"✅ Data saved to emergency file: {emergency_file_name}")
                except Exception as e2:
                    print(f"❌ Critical error: Could not save data even to emergency file: {e2}")
                    # Last resort - print to console so at least it's visible
                    print("EMERGENCY DATA DUMP:")
                    print(f"Template: {template_name}")
                    print(f"URL: {final_url}")
                    print(f"Keywords: {keywords}")
                    print(f"Match Types: {keyword_match_types}")

            # Save progress
            save_progress(i)

            # Click Back button
            try:
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, back_button_xpath)))
                driver.find_element(By.XPATH, back_button_xpath).click()
                print("⬅️ clicked 'Back' button. returning to main list...")
            except Exception as e:
                print(f"⚠️ Error clicking back button: {e}")
                input("❗ Please click the 'Back' button manually, then press Enter to continue...")

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

            # Even if we skip, try to save current progress
            save_progress(i)

# Close driver after completion
print(f"\n✅ Scraping completed! Results saved to '{results_file}'")
# Ask user if they want to delete the progress file
delete_progress = input("\n🗑️ Do you want to delete the progress file for a fresh start next time? (y/n): ").lower()
if delete_progress == 'y' and os.path.exists(progress_file):
    os.remove(progress_file)
    print(f"\n🗑️ Progress file '{progress_file}' deleted. Ready for a fresh start next time.")
else:
    print(f"\n💾 Progress file '{progress_file}' preserved for next session.")

driver.quit()