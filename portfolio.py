import requests 
from bs4 import BeautifulSoup
from dataclasses import dataclass
import tabulate  

@dataclass
class Stock:
    ticker: str
    exchange: str
    price_USD: float = 0.0
    currency: str = 'USD'

    def __post_init__(self):
        price_info = self.fetch_price_information()

        if price_info['ticker'] != self.ticker or price_info['exchange'] != self.exchange:
            raise ValueError(f'Could not find {self.ticker} on {self.exchange}')
        
        self.currency = price_info['currency']
        self.price_USD = round(price_info['price_USD'], 2)

    def fetch_price_information(self):
        url = f'https://www.google.com/finance/quote/{self.ticker}:{self.exchange}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        price_div = soup.find('div', attrs={'data-last-price': True})
        price = float(price_div['data-last-price'])
        currency = price_div['data-currency-code']

        if currency != 'USD':
            price *= self.get_fx_to_usd(currency)

        return {
            'ticker': self.ticker,
            'exchange': self.exchange,
            'price_USD': price,
            'currency': currency
        }

    @staticmethod
    def get_fx_to_usd(currency):
        url = f'https://www.google.com/finance/quote/{currency}-USD'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')    

        fx_rate = soup.find('div', attrs={'data-last-price': True})
        return float(fx_rate['data-last-price'])

@dataclass
class Position:
    stock: Stock
    quantity: int

@dataclass
class Portfolio:
    positions: list[Position]

    def get_total_value(self):
        return sum(position.stock.price_USD * position.quantity for position in self.positions)

def print_portfolio(portfolio):
    if not isinstance(portfolio, Portfolio):
        raise ValueError('Input must be a Portfolio object')

    portfolio_positions = [
        [position.stock.ticker, position.stock.exchange, position.quantity, position.stock.price_USD, position.stock.currency]
        for position in portfolio.positions
    ]

    print(tabulate.tabulate(portfolio_positions, headers=['Ticker', 'Exchange', 'Quantity', 'Price', 'Currency'], tablefmt='pretty'))

if __name__ == '__main__':
    shop = Stock('SHOP', 'NYSE')
    msft = Stock('MSFT', 'NASDAQ')
    aapl = Stock('AAPL', 'NASDAQ')

    portfolio = Portfolio([Position(shop, 10), Position(msft, 5), Position(aapl, 3)])
    print_portfolio(portfolio)
    print('Total portfolio value:', portfolio.get_total_value())


