# Shoptimiser
Raw source code files for my personal project Shoptimiser - a supermarket scraper and shopping list optimisation program

This project is currently intended for my own use in optimising my own shopping habits. I have added the project to GitHub as a testament to several new data analytics skils I have learned, such as:

- web scraping
- advanced file handling
- data cleaning and aggregation using pandas and numpy
- UI creation using Pyside6

As a novice, I mistakenly pushed the whole project as one commit. For future projects I will incrementally push my project updates.
For now, I have added a seperate readme called _dev-retrospective_ which highlights some notable insights and challenging situations from prpject development.

# How to run the software (from the command line):

1. Install the dependencies:
   _pip install -r requirements.txt_

If unsuccessful, try _python -m pip install -r requirements.txt_  
   
If still unsuccessful, please try installing each module manually by looking at the module names at the top of each script (data_collection.py, data_transformation.py, shoptimiser_controller.py)

2. Install the web-scraping browsers (Required for Playwright):
   _playwright install_
   
If unsuccessful, try _python -m playwright install_ 

5. Launch the application:
   python main.py

# Guide on how to use the software:

1. Search for the Latest Prices for Your Groceries

Click the Refresh Product Prices button to create a new file detailing the current prices of your products.This will be openly accessible in the /product_info_files folder.

As more shopping lists are generated, this product history can be used in data analysis software to analyze variations like product price per store or product price trends over time.

2. Configure Your Search Constraints

Select how often you buy groceries (e.g., weekly, biweekly). This alters the pricing scale models behind the scenes.
Check at least one location from the options list. The algorithm will filter items exclusive to these companies.

3. Process and View Optimization Results

Clicking the 'Create Shopping List' button will generate several shopping lists based on subsets of your shopping list selection.
A popup will appear listing all these lists alongside their total cost. You are free to choose a list which balances cost with the number of stores to visit. 

4. Export Shopping List

Click the Export Button to save your shopping list as a PNG
You can find your list in the /shopping_list_exports folder.

# Current Prototype Limitations

This project is currently a prototype, so it experiences a few limitations: 

- The shopping list and the shopping period (weekly, monthly, etc.) are currently hard-coded.
- Out of the stores you select, if all supermarkets have one or more products unavailable, then no list will be generated. This will not be an issue if you choose at least three of the four possible supermarkets.





