# %%
import numpy as np
import pandas as pd
import duckdb
import glob 
import sys
import os

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))




# %%
#retrieve file
glob_pattern = os.path.join(APP_DIR, 'product_info_files', 'product_info*.csv')
list_of_files = glob.glob(glob_pattern)
latest_file = max(list_of_files, key=os.path.getctime)

#retrieve shopping frequency (user input) to use in filtering
freq = int(sys.argv[1])

# %%
#read in files
product_info = pd.read_csv(latest_file)
references_path = os.path.join(APP_DIR, 'product_info_files', 'product_references.csv')
product_references = pd.read_csv(references_path)


# %%
#strip whitespace from headers
product_info.columns = [col.strip() for col in product_info.columns]
#cleaning the price column by removing pre-sale prices, removing £ sign and converting to float
prices = product_info['product_price'].str.findall(r'£(\d+\.\d{2})')
product_info['product_price'] = prices.apply(lambda x: min(map(float, x)) if x else None)
product_info['product_price'] = product_info['product_price'].apply(lambda x: f"£{x:.2f}" if x is not None else "None")

# %%
#remainder of data cleaning and casting
product_info['reference_id'] = product_info['reference_id'].astype("int8") #smallest int dtype
product_info['store'] = product_info['store'].str.strip()
product_info['product_title'] = product_info['product_title'].str.strip().replace("None", np.nan) #clean nulls
product_info['product_price'] = pd.to_numeric(product_info['product_price'].str.replace("£",'', regex=False), errors='coerce').round(2) #clean nulls and convert to float16


# %%
#shopping lists will be made for every combination of stores (for 4 stores, that is 10 lists total)
unique_shops = product_info['store'].unique().tolist()
store_sublists = []
for i in range(len(unique_shops)):
    for j in range(i+1, len(unique_shops) + 1):
        store_sublists.append(unique_shops[i:j])

# %%
#for each subset of stores, select the product with the lowest price and add to the shopping list
#record how much each shopping list costs in total_cost
date = latest_file[:-4].split('_')[-1]
total_cost = {}
total_cost_file_path = os.path.join(APP_DIR, 'total_cost_files', f'total_cost_{date}.csv')

for store_sublist in store_sublists:
    shopping_list = duckdb.sql(
    """
    SELECT
        product_name,
        reference_id AS product_ref,
        product_title,
        product_price,
        store,
        shopping_frequency
        FROM(
            SELECT
                pi.*,
                pr.name AS product_name,
                pr.shopping_frequency,
                ROW_NUMBER() OVER(PARTITION BY pi.reference_id ORDER BY product_price ASC) AS rn
            FROM product_info pi RIGHT JOIN product_references pr ON pi.reference_id = pr.reference_id
            WHERE list_contains(?, store)
            AND pr.shopping_frequency <= ?
        )
        WHERE rn=1
    """, params=[store_sublist, freq]
    ).df()

    #if a store sublist has one or more products NOT available, do not include that shopping list
    if not shopping_list['product_price'].isnull().any():
        shopping_list_file_path = os.path.join(APP_DIR, 'intermediary_shopping_lists', f'shopping_list_{"-".join(store_sublist)}.csv')
        shopping_list.to_csv(shopping_list_file_path, index=False)
        total_cost["-".join(store_sublist)] = shopping_list['product_price'].sum()

# %%
total_cost = pd.DataFrame(list(total_cost.items()), columns=["stores","total_cost"]).sort_values(by="total_cost", ascending=True)
total_cost['total_cost'] = total_cost['total_cost'].round(2)
total_cost.to_csv(total_cost_file_path, index=False)

