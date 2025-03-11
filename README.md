# sa_360_scraping
 Testing selenium to scrape multiple templates in Search Ads 360

To prevent issues with having to open new window each time wanting to run script, manually start Chrome in debugging mode & connect to existing session. You'll have to login to this chrome instance, but as long as the window remains open you won't have to login again. Login data is preserved in /tmp/ChromeProfile.

Run this in Terminal:

	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/ChromeProfile"


Keep this Terminal window open while running Selenium.


When run, the script opens up Google Search Ads 360, and prompts the user to navigate to the templates section. 
Then, the user should manually add any filters that are required to show all desired templates on a single page.

The script will wait for user input before starting any scraping. When the enter key is pressed within the python instance, the script will look for the first row in the table shown, copy the title of the template to a predefined .txt file path, then click on the settings cog.

When the first page of the settings loads, the script will automatically go to the second page, and copy the final URL path to the same .txt file, separated by the "|" symbol.

Then, the script will click on the back button and go to the second row to follow the same process. Progress (as to what row the script is on) is saved in a sa360_progress.txt file, only when the data is scraped for that row.

For deeper rows within the table, the script will scroll a few rows at a time to get to the needed row. 
It may take a few seconds to scroll to rows 100+, but the script can reliably scroll. Each scroll is 0.3 seconds apart, to allow for lazy loading content, particularly on slower connections. this value can be updated to be faster or slower deoending on requirements.

If the script crashes (usually when the chrome tab crashes, error handling is not added properly yet), you can just re-run the script - progress is saved so the script will start where you left off. You will have to apply filters again and get the desired templates to show up. Data is just appended to the end of your file rather than re-writing (including header row so there will be some duplicate rows)


Recently Added:
- Deleting progress file on completion (and prompting user if they want it deleted)
- Better scroll detection so scrolls more reliably, and retries if issue presents
- Taking user input on number of rows to scrape
- Taking user input on whether to use the progress file (if detected)
- Taking user input on a manual override for progress file if desired
- Some crash handling & retry logic
- Settings button double click on first instance to handle bug of not working on first row click

Need to add:
- proper crash handling
- handling pagination
- inputting filters automatically
- running headlessly
- checking for already running chrome, if not, launching new instance & navigating to correct location

bugs / issues
- settings click not working on first instance (fixed)
- not working on non-kw templates - add detail on when & where is appropriate to use, add error checking to ensure is used in right places
- need to get it to cancel / quit when getting to end of displayed results if internal number does not match row count (to prevent attempting endless scrape). 
