import os
import csv
import datetime
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, 'input')
FILES_TO_EXCLUDE = ['.gitignore']


class StockStatBase:
    def __init__(self, *args, **kwargs):
        self.dirname = os.path.join(INPUT_DIR, self.stock_name)
        if not os.path.exists(self.dirname):
            os.mkdir(self.dirname)
        self.files_list = [
            filename for filename in os.listdir(self.dirname) if filename not in FILES_TO_EXCLUDE
        ]

    def read_files(self, output_dict):
        for file in self.files_list:
            with open(os.path.join(self.dirname, file), 'r') as input_file:
                filereader = csv.reader(input_file, delimiter=self.delimiter)
                self.process_rows(filereader, output_dict)


class StockStatUniqDate(StockStatBase):

    def process_rows(self, rows, output_dict):
        for row in rows:
            if row:
                try:
                    date = datetime.datetime.strptime(
                        row[self.date_col], self.date_format).date().isoformat()
                except ValueError:
                    continue
                date_data = output_dict.get(date, {})
                str_total_col = row[self.total_col].replace('-', '')
                total_count = int(str_total_col) if str_total_col else 0
                date_data[self.stock_name] = (
                    total_count, Decimal(row[self.total_money_col].replace('$', '')))
                output_dict[date] = date_data


class StockStatNotUniqDate(StockStatBase):

    def process_rows(self, rows, output_dict):
        for row in rows:
            if row:
                try:
                    date = datetime.datetime.strptime(
                        row[self.date_col], self.date_format).date().isoformat()
                except ValueError:
                    print(row[self.date_col])
                    continue
                date_data = output_dict.get(date, {})
                stock_date_data = date_data.get(
                    self.stock_name, (0, Decimal(0)))
                total_count, total_money = stock_date_data
                stock_date_data = total_count + \
                    1, total_money + \
                    Decimal(row[self.money_col].replace('$', ''))
                date_data[self.stock_name] = stock_date_data
                output_dict[date] = date_data


class ShutterStat(StockStatUniqDate):
    stock_name = 'Shutterstock'
    date_col = 0
    date_format = '%Y-%d-%m'
    delimiter = ','
    total_col = 1
    total_money_col = 11


class IStockStat(StockStatNotUniqDate):
    stock_name = 'iStock'
    date_col = 6
    date_format = '%d-%b-%Y'
    delimiter = '\t'
    money_col = 28


class AdobeStockStat(StockStatNotUniqDate):
    stock_name = 'AdobeStock'
    date_col = 0
    date_format = '%Y-%m-%dT%H:%M:%S%z'
    delimiter = ','
    money_col = 4


class RF123Stat(StockStatNotUniqDate):
    stock_name = '123rf'
    date_col = 0
    date_format = '%Y-%m-%d %H:%M:%S'
    delimiter = ','
    money_col = 5


class BigstockStat(StockStatNotUniqDate):
    stock_name = 'Bigstock'
    date_col = 0
    date_format = '%Y-%m-%d %H:%M:%S'
    delimiter = ','
    money_col = 2


class DepositStat(StockStatUniqDate):
    stock_name = 'DepositPhotos'
    date_col = 0
    date_format = '%b.%d, %Y'
    delimiter = '\t'
    total_col = 2
    total_money_col = 6


if __name__ == "__main__":
    stock_classes = [
        ShutterStat,
        IStockStat,
        AdobeStockStat,
        RF123Stat,
        BigstockStat,
        DepositStat,
    ]
    result = {}
    for stock_class in stock_classes:
        stock = stock_class()
        stock.read_files(result)
    from pprint import pprint
    pprint(result)
