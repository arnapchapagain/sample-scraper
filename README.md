# Sample Scraping Project

This is a sample project to demonstrate how to scrape data from a website using Python, AioHTTP, Beautiful Soup and Asyncio.

The website is an [example ecommerce website](https://gopher1.extrkt.com/) and the data is about the products.

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py
```

## Output
The output is a JSON file named `products.json` in the root directory of the project which contains every data in a structured way.

The output is also printed saved to a CSV file named `products.csv` in the root directory of the project. However, due to complex data structures, the CSV file does not contain all the data.

Likewise the output is also pretty-printed to console. 

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## TODO
- [ ] Make sure CSV file contains all the data
- [ ] Pretty print the output to console
- [ ] Save the data to a SQLite database

## License
This project is licensed under the terms of the [MIT license](LICENSE).

 This project is developed for educational purposes only, and is not affiliated with the website in any way.