import csv
import json
import asyncio
from pprint import pprint
from dataclasses import dataclass, fields, asdict
from aiohttp import ClientSession, ClientResponseError
from bs4 import BeautifulSoup

@dataclass
class AdditionalInfo:
    label: str | list[str]
    values: str | list[str]


@dataclass
class Product:
    title: str
    image: str
    price: str
    sku: str
    short_description: str
    description: str
    cateogory: str
    additional: list[AdditionalInfo] | None


def append_to_json(data: Product):
    with open("products.json", "r+", encoding="utf-8") as file:
        try:
            file.seek(0) # Go to the start of the file
            json_data = json.load(file)  # Load existing data
            json_data.append(asdict(data))  # Append new data

            file.seek(0)  # Go back to the start of the file
            file.truncate()  # Truncate the file to overwrite
            json.dump(json_data, file, indent=4, ensure_ascii=False)

        except json.JSONDecodeError:
            # If the file is empty or the JSON is invalid, overwrite with new data
            file.seek(0)
            file.truncate()  # Clear the file before writing
            json.dump([asdict(data)], file, indent=4, ensure_ascii=False)
            


def append_to_csv(product: Product):
    with open("products.csv", "a", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=csv_headers)
        writer.writerow(asdict(product))
            


async def get_html(client: ClientSession, url: str, **kwargs) -> BeautifulSoup:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    }
    async with client.get(url, headers=headers, params=kwargs) as request:
        response = await request.text()
        return BeautifulSoup(response, "html.parser")
        

async def scrape_page(client: ClientSession, url: str, **kwargs):
    html = await get_html(client, url, **kwargs)
    tasks = []
    product_info = html.select("a.woocommerce-loop-product__link")
    product_links = [product.get("href") for product in product_info]
        
    for product_link in product_links:
        tasks.append(asyncio.ensure_future(get_html(client, product_link)))
    
    for task in asyncio.as_completed(tasks):
        product_page = await task
        product = Product(
            title = product_page.select_one("h1.product_title").text,
            image = product_page.select_one("div.woocommerce-product-gallery__image > a").get("href"),
            price = product_page.select_one("span.amount > bdi").text,
            short_description  = product_page.select_one("div.woocommerce-product-details__short-description > p").text.strip(),
            description = product_page.select_one("div#tab-description").text.replace("Description", "").strip(),
            sku = product_page.select_one("span.sku").text,
            cateogory=product_page.select_one("span.posted_in").text.replace("Category: ", ""),
            additional=[]
        )
        
        tr_tags = product_page.select("table.variations > tbody > tr")
        for tr in tr_tags:
            product.additional.append(AdditionalInfo(
                label = tr.select_one("th > label").text,
                # Excluding the first option "Choose an option"
                values = [value.text for value in tr.select("td > select > option") if value.text != "Choose an option"]
            ))
        
        yield product


async def main():
    url = "https://gopher1.extrkt.com/"
    page = 1
    products = []
    
    async with ClientSession(raise_for_status=True) as client:
        while True:
            try:
                async for product in scrape_page(client, url, paged=page):
                    products.append(product)
                    pprint(product)
                    append_to_json(product)
                    append_to_csv([product])
                    
                page += 1
                
            except ClientResponseError as e:
                print("Page limit reached")
                break

if __name__ == "__main__":
    csv_headers = [header.name for header in fields(Product)]
    csv_headers.pop(-1) # Removing the additional field
    for header in fields(AdditionalInfo):
        csv_headers.append("additional_" + header.name)
    
    with open("products.csv", "w", encoding="utf-8") as file:
        csv_writer = csv.DictWriter(file, csv_headers)
        csv_writer.writeheader()
    
    asyncio.run(main())
