import os
import csv
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, 'input')


class StockStatBase:
    def __init__(self, *args, **kwargs):
        self.filename = os.path.join(INPUT_DIR, self.filename)

    def read_files(self, output_dict):
        with open(self.filename, 'r') as input_file:
            filereader = csv.reader(input_file, delimiter=',')
            for row in filereader:
                date = row[self.date_col]
                try:
                    datetime.date.fromisoformat(date)
                    date_data = output_dict.get(date, {})
                    date_data[self.stock_name] = (
                        row[self.total_col], row[self.total_money_col])
                    output_dict[date] = date_data
                except:
                    continue


class ShutterStat(StockStatBase):
    stock_name = 'Shutterstock'
    filename = 'earnings.csv'
    date_col = 0
    date_format = ''
    total_col = 1
    total_money_col = 11


if __name__ == "__main__":
    stock_classes = [
        ShutterStat,
    ]
    result = {}
    for stock_class in stock_classes:
        stock = stock_class()
        stock.read_files(result)
    from pprint import pprint
    pprint(result)
