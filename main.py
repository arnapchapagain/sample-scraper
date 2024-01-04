import csv
import json
import asyncio
from dataclasses import dataclass
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
    short_description: str
    additional: list[AdditionalInfo] | None


async def get_html(client: ClientSession, url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"
    }
    async with client.get(url, headers=headers) as request:
        response = await request.text()
        return BeautifulSoup(response, "html.parser")
        

async def main():
    url = "https://gopher1.extrkt.com/"
    async with ClientSession(raise_for_status=True) as client:
        html = await get_html(client, url)
        products = html.select("a.woocommerce-loop-product__link")
        product_links = [product.get("href") for product in products]
            
        
        for product_link in product_links:
            product_page = await get_html(client, product_link)
            product = Product(
                title = product_page.select_one("h1.product_title").text,
                image = product_page.select_one("div.woocommerce-product-gallery__image > a").get("href"),
                price = product_page.select_one("span.amount > bdi").text,
                short_description  = product_page.select_one("div.woocommerce-product-details__short-description > p").text,
                additional=[]
            )
            
            tr_tags = product_page.select("table.variations > tbody > tr")
            for tr in tr_tags:
                product.additional.append(AdditionalInfo(
                    label = tr.select_one("th > label").text,
                    # Excluding the first option "Choose an option"
                    values = [value.text for value in tr.select("td > select > option") if value.text != "Choose an option"]
                ))
            


if __name__ == "__main__":
    asyncio.run(main())
