from PySide6.QtWidgets import(
    QMessageBox, QRadioButton, QCheckBox, QTableWidget,
    QAbstractItemView, QTableWidgetItem, QDialog, QTextBrowser, 
    QVBoxLayout, QDialogButtonBox, QHeaderView, QLabel)
from PySide6.QtCore import QFile, QProcess
from PySide6.QtUiTools import QUiLoader
import subprocess
import glob
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import textwrap
from datetime import datetime


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

class Shoptimiser:

    def __init__(self):
        #initialise loader
        self.loader = QUiLoader()
        self.file = QFile(resource_path('shopping_ui.ui'))

        self.file.open(QFile.ReadOnly)
        self.window = self.loader.load(self.file)
        self.file.close()

        self.setup()

    def setup(self): #initialise attributes and button actions    
        self.freq = None
        self.selected_stores = []
        self.final_shopping_list = None
        self.window.guideButton.clicked.connect(self.open_guide)
        self.window.scrapeButton.clicked.connect(self.run_scraper)
        self.window.creationButton.clicked.connect(self.create_shopping_list)
        self.window.downloadButton.clicked.connect(self.export_shopping_list)

    def open_guide(self): #open popup that explains how to use the program

        #initiliase dialog box popup
        popup = QDialog(self.window)
        popup.setWindowTitle("Shoptimiser User Guide")
        popup.resize(700, 550)

        #create layout
        layout = QVBoxLayout(popup)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        

        #create text window that lets you use HTML to structure the text
        text = QTextBrowser(popup)
        text.setOpenExternalLinks(True) #allows user to open up the folder containing the shopping lists
        #TO-DO: create hyperlinks to the png folder - both in the guide, and next to the export button

        html = """<h2 style='color: #FFFFFF; margin-bottom: 5px;'> Shoptimiser User Guide</h2>

        <hr style='border: none; border-top: 1px solid #BDC3C7;'>
        
        <h3 style='color: #2980B9;'>1. Search for the latest prices for your groceries</h3>
        <ul>
            <li>Click the <b>Refresh Product Prices</b> button to create a new file detailing the current prices of your product</li>
            <li>This will be openly accessible in the <b><code>/product_info_files</code> folder</b></li>
            <li>As more shopping lists are generated, this product history can be used in data analysis software,
            <li>to analyse eg. product price per store, or product price over time</li>
        </ul>

        <h3 style='color: #2980B9;'>2. Configure Your Search Constraints</h3>
        <ul>
            <li><b>Shopping Frequency:</b> Select how often you buy groceries (e.g., weekly, biweekly). This alters the pricing scale models behind the scenes.</li>
            <li><b>Superstores:</b> Check at least one location from the options list. The algorithm will filter items exclusive to these companies.</li>
        </ul>
        
        <h3 style='color: #2980B9;'>3. Process and View Optimization Results</h3>
        <ul>
            <li>Click the <b>Create Button</b> to execute calculations. If settings are missing, a system safety warning popup will appear.</li>
            <li>Review your filtered choices in the data grid table on the right side of the interface shell. Rows are sorted automatically by <i>Shop</i>, then by <i>Price</i>.</li>
        </ul>
        
        <h3 style='color: #2980B9;'>4. Export Shopping List</h3>
        <ul>
            <li>Click the <b>Export Button</b> to save your shopping list in png format.</li>
            <li>You can find your list in the <code>/shopping_list_exports</code> folder.</li>
        </ul>
        <br>
        <br>
        <h3 style='color: #F39C12;'>Current Prototype Limitations</h3>
        <p style='color: #BDC3C7; margin-bottom: 5px;'>This project is currently a prototype, so it experiences a few limitations:</p>
        <ol style='color: #ECEFF1; padding-left: 20px; line-height: 1.5;'>
            <li style='margin-bottom: 8px;'>The shopping list and the shopping period (weekly, monthly, etc.) are currently hard-coded.</li>
            <li>If any product is not available, no list will be generated. This will not be an issue if you choose at least three of the four possible supermarkets.</li>
        </ol>
        """
        
        text.setHtml(html)
        layout.addWidget(text)
        popup.exec()

    def run_scraper(self):

        #run the data_collection script as an asynchronous process. 
        self.scraper_process = QProcess()
        script_path = os.path.join(APP_DIR, "data_collection.py")
        #use signals to indicate to user that scraping is complete
        #self.scraper_process.finished.connect(lambda: self.popup("Product refresh complete."))
        self.scraper_process.start(sys.executable, [script_path])

       
    def create_shopping_list(self): #collect user input and run the data transformation script

        #check shopping frequency (radio buttons)
        radios = self.window.freqGroup.findChildren(QRadioButton)
        radio_selected = False
        for radio in radios:
            if radio.isChecked() and radio_selected == False:
                match radio.text():
                    case "twice a week":
                        self.freq = 1
                    case "every week":
                        self.freq = 2
                    case "every two weeks":
                        self.freq = 3
                    case "every month":
                        self.freq = 4
                radio_selected = True
        

        #check valid shop locations
        checkboxes = self.window.shopGroup.findChildren(QCheckBox)
        for checkbox in checkboxes:
            if checkbox. isChecked():
                self.selected_stores.append(checkbox.text())

        #check that user has selected a radio and at least one checkbox
        if self.freq == None or self.selected_stores == []:
            self.popup("Please select a <b>shopping frequency</b>" \
            " AND at least one <b>superstore</b>.")
            return
        
        #run the data transformation script and call to display its output
        self.transform_process = QProcess()
        script_path = os.path.join(APP_DIR, "data_transformation.py")
        args = [script_path, str(self.freq) ]
        self.transform_process.start(sys.executable, args)

        #use signals to populate the shopping table once data transformation script has run
        self.transform_process.finished.connect(self.populate_shopping_table)
    
    def populate_shopping_table(self):

        #grab cost file and filter to match the selected stores
        cost_folder = os.path.join(APP_DIR, "total_cost_files", "*")
        cost_files  = glob.glob(cost_folder)
        latest_cost_file = max(cost_files, key=os.path.getctime)

        shops, cost = self.choose_list_popup(latest_cost_file)
        self.clear_selections()
        if shops == None or cost == None:
            return 
        
        intermediary_shopping_folder = os.path.join(APP_DIR, "intermediary_shopping_lists", "*")
        intermediary_shopping_lists = glob.glob(intermediary_shopping_folder)
        for lst in intermediary_shopping_lists:
            l = os.path.basename(lst)
            if l.split('_')[2] == f"{shops}.csv":
                self.final_shopping_list = lst

        
        tbl_values = pd.read_csv(self.final_shopping_list).to_numpy()

        #create the table to display the shopping list in the table widget
        table = self.window.shoppingTable
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setRowCount(len(tbl_values))

        #fill table with the shopping list
        index = 0
        for row in tbl_values:

            table.setItem(index, 2, QTableWidgetItem(str(row[3]))) #shop name
            table.setItem(index, 1, QTableWidgetItem(str(row[0]))) #product name
            table.setItem(index, 0, QTableWidgetItem(str(row[4]))) #product cost
            index += 1
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        #add the total cost to the cost label
        self.window.costLabel.setText(f"TOTAL COST: £{cost}")

    def choose_list_popup(self, cost_file): #popup where user chooses final list before table is populated

        #boilerplate
        popup = QDialog(self.window)
        layout = QVBoxLayout(popup) 

        #instruction label
        label = QLabel("please select the superstores and corresponding total cost that suits you")
    
        #turn csv into a 2D array by converting to a dataframe and extracting its values.
        df = pd.read_csv(cost_file)
        df.columns = df.columns.str.strip()
        df = self.filter_by_shop(df)
        tbl_values = df.to_numpy()

        #create the table to display the intermediary table's total cost per shop subset
        table = QTableWidget(len(tbl_values), 2, popup)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        #iterate over tbl_values to fill in the table
        index = 0
        for row in tbl_values:
            table.setItem(index, 1, QTableWidgetItem(str(row[1]))) #total cost
            table.setItem(index, 0, QTableWidgetItem(str(row[0]))) #shop subset
            index += 1
        #make the table stretch to the size of the whole window...
        #...so that no text in the table is truncated
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        #submit button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(popup.accept)

        #add widgets and execute
        layout.addWidget(label)
        layout.addWidget(table)
        layout.addWidget(button_box)
        eval_code = popup.exec()
        selected_items = table.selectedItems()
        
        if eval_code == QDialog.Accepted and selected_items:
            #retrieve and return the selected shops and corresponding cost, that the user chooses
            selected_row = selected_items[0].row()
            selected_shops = table.item(selected_row, 0).text()
            selected_cost = table.item(selected_row, 1).text()
            return selected_shops, selected_cost 
        else:
            return None, None

    def filter_by_shop(self, df): #here the total_cost file is filtered
            #only return the rows where the shops are a subset of the user selection
            stores = df['stores'].str.split('-').apply(set)
            mask = stores.apply(lambda s: s.issubset(set(self.selected_stores)))
            df = df[mask]

            return df
 
    def popup(self, message):
        popup = QMessageBox(self.window)
        popup.setText(message)
        popup.setWindowTitle("  ")
        popup.setStandardButtons(QMessageBox.StandardButton.Ok)
        popup.exec()

    def clear_selections(self):
        radios = self.window.freqGroup.findChildren(QRadioButton)
        for radio in radios:
            radio.setAutoExclusive(False)
            radio.setChecked(False)
            radio.setAutoExclusive(True)

        checkboxes = self.window.shopGroup.findChildren(QCheckBox)
        for checkbox in checkboxes:
            checkbox.setChecked(False)

        self.selected_stores = []
        self.freq = None

    def export_shopping_list(self): #save to 'shopping_lisr_exports' folder as a png
        if self.final_shopping_list == None:
            self.popup('You need to <b>create a shopping list</b> before you can export it')
            return
        
        #convert the final shopping list to a dataframe and remove uneeded columns
        df = pd.read_csv(self.final_shopping_list)
        df = df.sort_values(by=['store', 'product_ref'], ascending=[True, True])
        df = df.drop(columns=['product_name', 'product_ref', 'shopping_frequency'])

        #the product title is long, so have it wrap to a new line at some point
        df['product_title'] = df['product_title'].astype(str).apply(lambda x: '\n'.join(textwrap.wrap(x, width=35)))

        #dynamic height to prevent rows being 'squashed'. Width is A4
        height = (len(df) * 0.4) + 1.0
        width = 8.27

        #render table and save
        figure, axes = plt.subplots(figsize=(width, height))
        axes.axis('off')
        table = axes.table(cellText=df.values, colLabels=df.columns, loc='center')
        table.scale(1.0, 2.0)
        
        #export table as png
        todays_date = datetime.now().strftime("%d-%m-%Y")
        filename = f"shopping_list_exports/shopping_list_{todays_date}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        self.popup(f'shopping list saved as {filename}')




        









#widget names:
# MainWindow
    # centralWidget
    # baseLayout
    # inputFrame
        # freqGroup
            # freqLabel
            # freqLayout
                # radio1,2,3,4
        # shopGroup
            # shopLabel
            # shopLayout
                # checkbox1,2,3,4
        # guideButton  
        # prototypeLabel
        # creationButton
    # outputFrame
        # downloadButton
        # label
        # shoppingTable

    






