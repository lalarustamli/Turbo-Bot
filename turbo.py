from flask import Flask
import sys
print(sys.path)
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from flask import send_file
app = Flask(__name__)

@app.route('/')
def hello_world():
    url = 'https://www.turbo.az'
    prods = []
    for i in range(1, 3):
        turbo_az = requests.get('https://turbo.az/autos?page=' + str(i))
        turbo_az_html = turbo_az.content
        soup = BeautifulSoup(turbo_az_html, "html.parser")
        product_links = soup.find_all("a", {"class": "products-i-link", "href": re.compile(r'autos')})
        for link in product_links:
            car_pages_request = requests.get(url + link["href"])
            soup2 = BeautifulSoup(car_pages_request.content, "html.parser")
            product_name = soup2.find("h1", {"class": "product-name"})
            product_name_list = product_name.text.split(',')
            product_properties_list = soup2.find_all("li", {"class": "product-properties-i"})
            car_names_dict = {}
            for pr in product_properties_list:
                values = pr.find("div", {"class": "product-properties-value"})
                if pr.find("label"):
                    car_names_dict[pr.find("label").text] = values.text
            if soup2.find("div", {"class": "seller-name"}):
                car_names_dict["Satıcı"] = soup2.find("div", {"class": "seller-name"}).text
                car_names_dict["Avtosalon"] = ''
                car_names_dict["Əlaqə"] = soup2.find("a", {"class": "phone"}).text
            elif soup2.find("a", {"class": "shop-contact--shop-name"}):
                car_names_dict["Satıcı"] = ''
                car_names_dict["Avtosalon"] = soup2.find("a", {"class": "shop-contact--shop-name"}).text
                car_names_dict["Əlaqə"] = soup2.find("a", {"class": "shop-contact--phones-number"}).text
            else:
                car_names_dict["Diler"] = soup2.find("a", {"class": "shop-contact--shop-name"}).text
                car_names_dict["Əlaqə"] = soup2.find("a", {"class": "shop-contact--phones-number"}).text

            car_names_dict["Link"] = url + link["href"]
            prods.append(car_names_dict)
    df = pd.DataFrame(prods)
    if os.path.exists('turbo.csv'):
        csv = df.to_csv('turbo.csv', mode='a', header=False, index=False, encoding='utf-8-sig')
    else:
        csv = df.to_csv('turbo.csv', index=False, encoding='utf-8-sig')
    return send_file('turbo.csv',attachment_filename='data.csv')