# sa_360_scraping
 Testing selenium to scrape multiple templates in Search Ads 360

Requires Selenium installed (pip install selenium)

To prevent issues with having to open new window each time wanting to run script, manually start Chrome in debugging mode & connect to existing session (preserves cookies etc):

Run this in Terminal:

	/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/ChromeProfile"


This starts Chrome with remote debugging enabled and preserves login data in /tmp/ChromeProfile.
Keep this Terminal window open while running Selenium.


Script opens up search ads 360, and prompts user to navigate to the templates section. 
Then, user should manually add any filters that are required to show all templates on a single page.

Press enter within python instance to get the script to start. It'll look for the first row, copy the title of the template to a predefined .txt file path, then click on the settings cog.

When the first page of the settings loads, the script will automatically go to the second page, and copy the final URL path to the same .txt file.

Then, the script will click on the back button and go to the second row to follow the same process. Progress is saved in a sa360_progress.txt file.

For deeper rows within the table, the script will scroll a few rows at a time to get to the needed row. It may take a few seconds to scroll to rows 100+, but script can reliably scroll.


If the script crashes (usually when the chrome tab crashes, error handling not added properly yet), you can just re-run from the start - progress is saved so the script will start where you left off. Data is just appended to the end of your file (including header row so there will be some duplicate rows)


Need to add:
- proper crash handling 
- deleting progress file on successful completion
- better scroll detection - sometimes when the table doesn't load fast enough it can skip rows
- handling pagination
- inputting filters
