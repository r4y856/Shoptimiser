from playwright.sync_api import sync_playwright
from seleniumbase import sb_cdp
from bs4 import BeautifulSoup
from datetime import datetime
import random
import os
import sys

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

#functions and procedures
def reject_cookies(sb, shop_name):
    match shop_name:
        case "Asda":
            sb.click("#onetrust-reject-all-handler")
        case "Tesco":
            pass #the cookies is not a pop-up, so you're not foreced to reject it
        case "Aldi":
            sb.click("#onetrust-reject-all-handler")
        case "Morrisons":
            sb.click("#onetrust-reject-all-handler")
        case "Sainsburys":
            sb.click(".ot-pc-refuse-all-handler")

def get_product_info(soup, shop_name):
    match shop_name:
        case "Asda":
            name = soup.find('h1')
            price = soup.find('div', {'data-testid': 'txt-pdp-product-price'})
            return name, price
        case "Tesco":
            name = soup.find('h1', {'data-auto': 'pdp-product-title'})
            price = soup.select_one("p[class*='priceText']")
            return name, price
        case "Aldi":
            name = soup.select_one("h1[class='product-details__title']")
            price = soup.find("span", class_="base-price__regular")
            return name, price
        case "Morrisons":
            name = soup.select_one('div[class*="_box_"] h1')
            price = soup.select_one('div[data-test="price-container"]')
            return name, price
        case "Sainsburys":
            name = soup.select_one('h1[data-testid="pd-product-title"]')
            price = soup.select_one('[data-testid="pd-retail-price"]')
            return name, price
        
    return None, None

def append_file(full_path, product_ref, shop_name, product_name=None, product_price=None):
    with open(full_path, "a", encoding="utf-8") as f:
        f.write(f"{product_ref}, {shop_name}, {product_name}, {product_price}\n")
        f.close()

#seleniumbase boilerplate code
sb = sb_cdp.Chrome(locale="en", ad_block=True)
endpoint_url = sb.get_endpoint_url()

#create file to store product info
todays_date = datetime.now().strftime("%d-%m-%Y")
folder = os.path.join(APP_DIR, "product_info_files")
filename = f"product_info_{todays_date}.csv"
full_path = os.path.join(folder, filename)
with open(full_path, "w", encoding="utf-8") as f:
    f.write("reference_id, store, product_title, product_price\n")
    f.close()

#list of all products to scrape prices for
website_urls = {
    "Asda":[
        "https://www.asda.com/groceries/product/melon-pineapple/asda-refreshingly-juicy-watermelon/915130",
        "https://www.asda.com/groceries/product/berries-cherries/exceptional-by-asda-exceptional-by-asda-hand-picked-raspberries-150g/9300569",
        "https://www.asda.com/groceries/product/berries-cherries/asda-sweet-juicy-blackberries/2717897",
        "https://www.asda.com/groceries/product/melon-pineapple/asda-giant-pineapple/151745",
        "https://www.asda.com/groceries/product/apples/asda-royal-gala-apples/5648295",
        "https://www.asda.com/groceries/product/oranges-easy-peelers/just-essentials-by-asda-oranges/5797447",
        "https://www.asda.com/groceries/product/mango-kiwi-exotic-fruit/asda-delicate-smooth-papaya/866041",
        "https://www.asda.com/groceries/product/broccoli-cauliflower/asda-tender-crunchy-broccoli/5561471",
        "https://www.asda.com/groceries/product/broccoli-cauliflower/asda-light-nutty-cauliflower/153881",
        "https://www.asda.com/groceries/product/beans-asparagus-sweetcorn/just-essentials-by-asda-green-beans-240g/7132612"
        "https://www.asda.com/groceries/product/cabbage-sprouts/asda-mild-sweet-spring-greens/150460",
        "https://www.asda.com/groceries/product/white-potatoes/asda-fluffy-golden-baking-potatoes-2kg/9100617",
        "https://www.asda.com/groceries/product/sweet-red-potatoes/asda-creamy-flavoursome-sweet-potatoes-1kg/2076628",
        "https://www.asda.com/groceries/product/carrots-root-vegetables/asda-crunchy-sweet-carrots-1kg/150208",
        "https://www.asda.com/groceries/product/carrots-root-vegetables/asda-sweet-earthy-parsnips-500g/4419168",
        "https://www.asda.com/groceries/product/courgettes-aubergines-squash/asda-aubergine/5795232",
        "https://www.asda.com/groceries/product/courgettes-aubergines-squash/asda-courgettes-typically-0-35kg-/150567",
        "https://www.asda.com/groceries/product/onions-leeks/asda-brown-onions-1kg/2110666",
        "https://www.asda.com/groceries/product/tomatoes-peppers/asda-loose-red-pepper/1857059",
        "https://www.asda.com/groceries/product/lettuce-cucumber/asda-iceberg-lettuce/410006",
        "https://www.asda.com/groceries/product/lettuce-cucumber/asda-whole-cucumber/152446",
        "https://www.asda.com/groceries/product/natural-greek-yogurts/exceptional-by-asda-authentic-fat-free-greek-yogurt-500g/9123240",
        "https://www.asda.com/groceries/product/natural-greek-yogurts/plant-based-by-asda-plant-based-by-plain-soya-yogurt-alternative-500g/6019150",
        None, #I only want corn flakes from tesco
        "https://www.asda.com/groceries/product/bran-flakes-fruit-n-fibre/free-from-by-asda-bran-flakes-300g/9273080",
        "https://www.asda.com/groceries/product/tinned-pulses-lentils/asda-chickpeas-in-water-400g/5016063",
        "https://www.asda.com/groceries/product/honey/exceptional-by-asda-exceptional-by-spanish-forest-honey-340g/9295455",
        "https://www.asda.com/groceries/product/organic-eggs/asda-organic-organic-6-free-range-mixed-eggs-328g/3015762",
        "https://www.asda.com/groceries/product/sharing-chocolate-bars/lindt-excellence-intense-dark-90-cocoa-chocolate-bar-100g/5028239",
        "https://www.asda.com/groceries/product/semi-skimmed-milk/asda-organic-fresh-semi-skimmed-british-milk-1-litre/9222708",
        "https://www.asda.com/groceries/product/raw-nuts-seeds/asda-cashews-200g/7359199",
        "https://www.asda.com/groceries/product/raw-nuts-seeds/asda-pistachios-in-shell-200g/7359201",
        "https://www.asda.com/groceries/product/raw-nuts-seeds/asda-walnuts-200g/7359203",
        "https://www.asda.com/groceries/product/pasta-tubes-shells-spirals/asda-free-from-free-from-by-penne-500g/2513574",
        "https://www.asda.com/groceries/product/spaghetti-tagliatelle/asda-free-from-free-from-spaghetti-500g/2513572",
        "https://www.asda.com/groceries/product/smoked-salmon/asda-2-flavoursome-salmon-fillets-260g/9311950",
        "https://www.asda.com/groceries/product/cod-haddock-white-fish/asda-2-sea-bass-fillets-180g/4016132"
        "https://www.asda.com/groceries/product/grated-sliced-cheese/asda-grated-mozzarella-250g/4642115"
    ],

    "Tesco":[
        "https://www.tesco.com/shop/en-GB/products/254638605",
        "https://www.tesco.com/shop/en-GB/products/287377667",
        "https://www.tesco.com/shop/en-GB/products/287377189",
        "https://www.tesco.com/shop/en-GB/products/255230763",
        "https://www.tesco.com/shop/en-GB/products/284475550",
        "https://www.tesco.com/shop/en-GB/products/292225110",
        "https://www.tesco.com/shop/en-GB/products/255547786",
        "https://www.tesco.com/shop/en-GB/products/307344549.",
        "https://www.tesco.com/shop/en-GB/products/253558119?_gl=1*1wvgdtq*_up*MQ..*_ga*MTI3NjAwNTA4LjE3NzgyMzU5MzM.*_ga_H653QXESTP*czE3NzgyMzU5MzIkbzEkZzAkdDE3NzgyMzU5MzIkajYwJGwwJGgxMDE1ODU0NDQ3*_ga_33B19D36CY*czE3NzgyMzU5MzIkbzEkZzEkdDE3NzgyMzYxMDEkajYwJGwwJGg4MTI2MDA4NTM.",
        "https://www.tesco.com/shop/en-GB/products/313168567?_gl=1*5z78qe*_up*MQ..*_ga*MTI3NjAwNTA4LjE3NzgyMzU5MzM.*_ga_H653QXESTP*czE3NzgyMzU5MzIkbzEkZzAkdDE3NzgyMzU5MzIkajYwJGwwJGgxMDE1ODU0NDQ3*_ga_33B19D36CY*czE3NzgyMzU5MzIkbzEkZzEkdDE3NzgyMzYxMjMkajM4JGwwJGg4MTI2MDA4NTM.",
        "https://www.tesco.com/shop/en-GB/products/255838396?_gl=1*1tyk563*_up*MQ..*_ga*MTI3NjAwNTA4LjE3NzgyMzU5MzM.*_ga_H653QXESTP*czE3NzgyMzU5MzIkbzEkZzAkdDE3NzgyMzU5MzIkajYwJGwwJGgxMDE1ODU0NDQ3*_ga_33B19D36CY*czE3NzgyMzU5MzIkbzEkZzEkdDE3NzgyMzYxNjQkajYwJGwwJGg4MTI2MDA4NTM.",
        "https://www.tesco.com/shop/en-GB/products/302290700?_gl=1*i41dqz*_up*MQ..*_ga*MTk3ODUwNzYxMy4xNzc4MjQ4ODI4*_ga_H653QXESTP*czE3NzgyNDg4MjckbzEkZzAkdDE3NzgyNDg4MjckajYwJGwwJGg4NTA0MzU3NzA.*_ga_33B19D36CY*czE3NzgyNDg4MjckbzEkZzAkdDE3NzgyNDg4MzEkajU2JGwwJGgxMDQxODQxMTY4",
        "https://www.tesco.com/shop/en-GB/products/310190037?_gl=1*1jybcsq*_up*MQ..*_ga*MTI3NjAwNTA4LjE3NzgyMzU5MzM.*_ga_H653QXESTP*czE3NzgyMzU5MzIkbzEkZzAkdDE3NzgyMzU5MzIkajYwJGwwJGgxMDE1ODU0NDQ3*_ga_33B19D36CY*czE3NzgyMzU5MzIkbzEkZzEkdDE3NzgyMzYyNjMkajYwJGwwJGg4MTI2MDA4NTM.",
        "https://www.tesco.com/shop/en-GB/products/305953125?_gl=1*hi5sq*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY0MzUkajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/292310843?_gl=1*170gvev*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY0NjYkajI5JGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/293610620?_gl=1*13sjirw*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY0OTckajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/302292312?_gl=1*gff0gr*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY1NTAkajckbDAkaDE2MTQyMjgxNjk.",
        "https://www.tesco.com/shop/en-GB/products/255736044?_gl=1*1okcqi6*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY1NjkkajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/295673143?_gl=1*anpqs8*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY1ODckajQyJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/253560041?_gl=1*1ypmgc8*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY2MjIkajckbDAkaDE2MTQyMjgxNjk.",
        "https://www.tesco.com/shop/en-GB/products/253558972?_gl=1*1jsemg1*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY2NTgkajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/256381115?_gl=1*1byt48v*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY2ODEkajM3JGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/311442721?_gl=1*8b1tfx*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY3MjEkajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/313855241?_gl=1*1ae8fdd*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY3NDMkajM4JGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/321678473?_gl=1*1pbk68*_up*MQ..*_ga*NTY4NTcwMzg2LjE3NzgyNDkyODc.*_ga_H653QXESTP*czE3NzgyNDkyODckbzEkZzAkdDE3NzgyNDkyODckajYwJGwwJGg3MjU2MTUwODc.*_ga_33B19D36CY*czE3NzgyNDkyODckbzEkZzEkdDE3NzgyNDkzNTUkajYwJGwwJGgyMTI0Njk2NzQx",
        "https://www.tesco.com/shop/en-GB/products/262490576?_gl=1*1k2xtz6*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY4NzQkajkkbDAkaDE2MTQyMjgxNjk.",
        "https://www.tesco.com/shop/en-GB/products/313523951?_gl=1*14j0aij*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY4ODckajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/268263786?_gl=1*73nqic*_up*MQ..*_ga*MTA4MTUzNTY5Mi4xNzc4MjM4MDYy*_ga_H653QXESTP*czE3NzgyMzgwNjIkbzEkZzAkdDE3NzgyMzgwNjIkajYwJGwwJGgxMjM4MzU0OTc.*_ga_33B19D36CY*czE3NzgyMzgwNjIkbzEkZzAkdDE3NzgyMzgwNjkkajUzJGwwJGgxNzcxMzA2MDcx",
        "https://www.tesco.com/shop/en-GB/products/315377302?_gl=1*snl3di*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY5MjckajIwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/251499710?_gl=1*1dr5gm5*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzY5NjgkajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/266376222?_gl=1*6jsyqp*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzcwNTckajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/266375344?_gl=1*1hn7ypb*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzcwODYkajMxJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/296546961?_gl=1*1uuu32w*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzcxNDEkajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/256876734?_gl=1*1u4wtom*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzcxNjYkajM1JGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/256876728?_gl=1*1u4wtom*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzcxNjYkajM1JGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/296920881?_gl=1*8adq6c*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzcxOTEkajEwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/310154741?_gl=1*7jntqd*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzcyMTAkajYwJGwwJGgxNjE0MjI4MTY5",
        "https://www.tesco.com/shop/en-GB/products/257480267?_gl=1*199tfr2*_up*MQ..*_ga*MTMzODAxMDgwLjE3NzgyMzYzMDM.*_ga_H653QXESTP*czE3NzgyMzYzMDMkbzEkZzAkdDE3NzgyMzYzMDMkajYwJGwwJGgxNjUwNzAwMTYy*_ga_33B19D36CY*czE3NzgyMzYzMDMkbzEkZzEkdDE3NzgyMzcyMzIkajM4JGwwJGgxNjE0MjI4MTY5"
    ],

    "Aldi":[
        "https://www.aldi.co.uk/product/nature-s-pick-watermelon-000000000000265497",
        "https://www.aldi.co.uk/product/nature-s-pick-british-raspberries-000000000000339909",
        "https://www.aldi.co.uk/product/nature-s-pick-british-blackberries-000000000000339765",
        None, #Aldi does not sell whole pineapples,
        "https://www.aldi.co.uk/product/everyday-essentials-wonky-apples-000000000000491850",
        "https://www.aldi.co.uk/product/nature-s-pick-oranges-000000000000266773",
        None, #Aldi does not sell papaya,
        "https://www.aldi.co.uk/product/nature-s-pick-british-broccoli-000000000000339776",
        "https://www.aldi.co.uk/product/nature-s-pick-british-cauliflower-000000000000334794",
        "https://www.aldi.co.uk/product/nature-s-pick-green-beans-000000000000339847",
        "https://www.aldi.co.uk/product/nature-s-pick-savoy-cabbage-000000000000339970",
        None, #aldi does not have desired mass of potatoes
        "https://www.aldi.co.uk/product/nature-s-pick-sweet-potatoes-000000000000272328",
        "https://www.aldi.co.uk/product/nature-s-pick-carrots-000000000000339791",
        "https://www.aldi.co.uk/product/nature-s-pick-british-parsnips-000000000000339898",
        "https://www.aldi.co.uk/product/nature-s-pick-aubergine-000000000000334444",
        "https://www.aldi.co.uk/product/nature-s-pick-courgettes-000000000000339808",
        "https://www.aldi.co.uk/product/nature-s-pick-brown-onions-000000000000339777",
        "https://www.aldi.co.uk/product/nature-s-pick-mixed-peppers-000000000000275392",
        "https://www.aldi.co.uk/product/nature-s-pick-british-little-gem-lettuce-2-pack-000000000000339865",
        "https://www.aldi.co.uk/product/nature-s-pick-cucumber-000000000000273659",
        "https://www.aldi.co.uk/product/lyttos-greek-yoghurt-10-fat-000000000000268881",
        None, #aldi does not have dairy free yoghurt
        None, #aldi does not have gluten free corn flakes 
        None, #aldi does not have gluten free bran flakes
        "https://www.aldi.co.uk/product/four-seasons-chickpeas-000000000000625258",
        "https://www.aldi.co.uk/product/specially-selected-manuka-honey-000000000000629340",
        "https://www.aldi.co.uk/product/merevale-british-organic-eggs-6-pack-000000000000417565",
        "https://www.aldi.co.uk/product/moser-roth-dark-85-cocoa-chocolate-000000000297252032",
        None, #aldi does not have organic milk
        "https://www.aldi.co.uk/product/the-foodie-market-cashew-nuts-000000000000384094",
        "https://www.aldi.co.uk/product/the-foodie-market-californian-roasted-pistachios-000000000000304635",
        "https://www.aldi.co.uk/product/the-foodie-market-walnut-halves-000000000000384093",
        None, #aldi does not have gluten free pasta
        None, #aldi does not have gluten free spaghetti
        "https://www.aldi.co.uk/product/the-fishmonger-boneless-salmon-fillets-2-pack-000000000000381995",
        "https://www.aldi.co.uk/product/the-fishmonger-boneless-mediterranean-sea-bass-fillets-2-pack-000000000000388008",
        "https://www.aldi.co.uk/product/emporium-grated-mozzarella-000000000000280873"
    ],

    "Morrisons":[
        "https://groceries.morrisons.com/products/morrisons-watermelon/108448923",
        "https://groceries.morrisons.com/products/morrisons-raspberries-150g-punnet/108472798",
        "https://groceries.morrisons.com/products/morrisons-blackberries-150g-punnet/108473192",
        "https://groceries.morrisons.com/products/fyffes-ready-to-eat-pineapple/113016965",
        "https://groceries.morrisons.com/products/morrisons-royal-gala-apples-6-pack/108682621",
        "https://groceries.morrisons.com/products/morrisons-oranges-5-pack/109541521",
        "https://groceries.morrisons.com/products/morrisons-formosa-papaya-fruit/113822537",
        "https://groceries.morrisons.com/products/morrisons-broccoli-375g/109148703",
        "https://groceries.morrisons.com/products/morrisons-medium-cauliflower/108303071",
        "https://groceries.morrisons.com/products/morrisons-savers-green-beans/112941382",
        "https://groceries.morrisons.com/products/morrisons-spring-greens-500g/108302422",
        "https://groceries.morrisons.com/products/morrisons-british-maris-piper-potatoes-2kg/113405101",
        "https://groceries.morrisons.com/products/morrisons-sweet-potatoes-1kg/108572051",
        "https://groceries.morrisons.com/products/morrisons-british-carrots-1kg/108305527",
        "https://groceries.morrisons.com/products/morrisons-parsnips-500g/108304575",
        "https://groceries.morrisons.com/products/morrisons-purple-aubergine/108392641",
        "https://groceries.morrisons.com/products/morrisons-courgettes/115508998",
        "https://groceries.morrisons.com/products/morrisons-british-brown-onions-1kg/108504753",
        "https://groceries.morrisons.com/products/morrisons-greengrocer-sweet-peppers-3-pack-colours-may-vary/112915504",
        "https://groceries.morrisons.com/products/morrisons-little-gem-lettuce-2-pack/108285343",
        "https://groceries.morrisons.com/products/morrisons-whole-cucumber/108413093",
        "https://groceries.morrisons.com/products/morrisons-the-best-greek-yogurt-10-fat-500g/109815035",
        "https://groceries.morrisons.com/products/arla-lactofree-natural-yogurt/114110734",
        "https://groceries.morrisons.com/products/nestle-go-free-gluten-free-cornflakes-cereal-375g/113140667",
        None, #morrisons does not sell gluten free bran flakes
        "https://groceries.morrisons.com/products/morrisons-chickpeas-in-water-400g/110434045",
        "https://groceries.morrisons.com/products/morrisons-the-best-spanish-forest-honey/109434785",
        "https://groceries.morrisons.com/products/purely-organic-10-mixed-size-eggs/110389336",
        "https://groceries.morrisons.com/products/lindt-excellence-dark-85-cocoa-chocolate-bar-100g/108622354",
        "https://groceries.morrisons.com/products/morrisons-organic-semi-skimmed-milk-1l/114038656",
        "https://groceries.morrisons.com/products/morrisons-the-best-roasted-jumbo-cashews-150g/112441417",
        None, #morrisons does not have desired weight of pistachios
        "https://groceries.morrisons.com/products/morrisons-walnut-pieces-150g/105626384",
        "https://groceries.morrisons.com/products/rummo-gluten-free-mezzi-rigatoni-no-51-pasta/115384198",
        "https://groceries.morrisons.com/products/morrisons-free-from-spaghetti-500g/105473681",
        "https://groceries.morrisons.com/products/morrisons-2-salmon-fillets-220g/111595107",
        "https://groceries.morrisons.com/products/morrisons-2-sea-bass-fillets-180g/109804336",
        "https://groceries.morrisons.com/products/morrisons-grated-mozzarella-240g/112608547"
    ]
}

with sync_playwright() as p:
    
    #browser creaton boilerplate code
    browser = p.chromium.connect_over_cdp(endpoint_url)
    context = browser.contexts[0]
    page = context.pages[0]

    #website navigation and extracting all html
    for shop_name, urls in website_urls.items():
        #if shop_name == "Asda": continue
        cookies_rejected = False #each new shop brings about new cookies to reject
        for product_ref, url in enumerate(urls): #product_ref is eg, watermelon = 1, raspberries = 2, regardless of shop. Not a unique field.

            sb.sleep(random.uniform(4, 15))

            try:
                page.goto(url, wait_until="domcontentloaded", referer="https://google.com")
            except:
                append_file(full_path, product_ref+1, shop_name)
                continue

            sb.sleep(random.uniform(2, 5))

            if not cookies_rejected:
                sb.sleep(2.7)
                reject_cookies(sb, shop_name)
                cookies_rejected = True

            sb.sleep(random.uniform(2, 5))

            #fetching the html will be the main source of errors
            try:
                page.wait_for_load_state("domcontentloaded") 
                sb.sleep(random.uniform(3.5, 7.2))
                page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                html_content = page.content()

                if not html_content:
                    raise ValueError("HTML content is empty")
                
            except ValueError:
                    #the page will be a 404, or may have been caught by bot detection
                    append_file(full_path, product_ref, shop_name)
                    continue
            
            except Exception:
                    #this will be a runtime issue.
                    append_file(full_path, product_ref, shop_name)
                    continue
            
            #---the following will run if no errors are found---

            #parsing html code
            soup = BeautifulSoup(html_content, 'lxml')
            product_name_container, product_price_container = get_product_info(soup, shop_name)

            #in case None errors were not caught, assign "None" to achieve same effect
            if product_name_container:
                product_name = f'"{product_name_container.text.strip()}"' #wrapped in quotes so commas in the name aren't treated as new columns in the csv.
            else:
                product_name = "None"

            if product_price_container:
                product_price = product_price_container.text.strip().replace("actual price", "")
            else:
                product_price = "None"

            #writing to text file in csv format
            append_file(full_path, product_ref+1, shop_name, product_name, product_price)
            sb.sleep(random.uniform(2, 5))

    browser.close()

        

        
        


