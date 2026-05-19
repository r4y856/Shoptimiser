# Shoptimiser
Raw source code files for my personal project Shoptimiser - a supermarket scraper and shopping list optimisation program

This project is currently intended for my own use in optimising my own shopping habits. I have added the project to GitHub as a testament to several new skils I have learned, such as:

- web scraping
- advanced file handling
- data cleaning and aggregation using pandas and numpy
- UI creation using Pyside6

# How to run the software (from the command line):

1. Install the dependencies:
   pip install -r requirements.txt

2. Install the web-scraping browsers (Required for Playwright):
   playwright install

3. Launch the application:
   python main.py

# Guide on how to use the software:

1. Search for the Latest Prices for Your Groceries

Click the Refresh Product Prices button to create a new file detailing the current prices of your products.This will be openly accessible in the /product_info_files folder.

As more shopping lists are generated, this product history can be used in data analysis software to analyze variations like product price per store or product price trends over time.

2. Configure Your Search Constraints

Shopping Frequency: Select how often you buy groceries (e.g., weekly, biweekly). This alters the pricing scale models behind the scenes.Superstores: Check at least one location from the options list. The algorithm will filter items exclusive to these companies.

3. Process and View Optimization Results

Click the Create Button to execute calculations. If settings are missing, a system safety warning popup will appear.
Review your filtered choices in the data grid table on the right side of the interface shell. Rows are sorted automatically by Shop, then by Price.

4. Export Shopping List

Click the Export Button to save your shopping list in PNG format.
You can find your list in the /shopping_list_exports folder.


# Current Prototype Limitations

This project is currently a prototype, so it experiences a few limitations: 

- The shopping list and the shopping period (weekly, monthly, etc.) are currently hard-coded.
- Out of the stores you select, if all supermarkets have one or more products unavailable, then no list will be generated. This will not be an issue if you choose at least three of the four possible supermarkets.





