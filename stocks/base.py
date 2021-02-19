import os
import csv
import datetime
from decimal import Decimal


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = os.path.join(BASE_DIR, 'input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
FILES_TO_EXCLUDE = ['.gitignore']
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'export_%s_%s.csv')


class StockStatBase:

    currency = None

    def __init__(self, *args, **kwargs):
        self.dirname = os.path.join(INPUT_DIR, self.stock_name)
        if not os.path.exists(self.dirname):
            os.mkdir(self.dirname)
        self.files_list = [
            filename for filename in os.listdir(self.dirname) if filename not in FILES_TO_EXCLUDE
        ]

    def read_files(self, output_dict):
        for file in self.files_list:
            with open(os.path.join(self.dirname, file), 'r', encoding='utf-8') as input_file:
                filereader = csv.reader(input_file, delimiter=self.delimiter)
                self.process_rows(filereader, output_dict)

    def preproc_date(self, date):
        return date


class StockStatUniqDate(StockStatBase):

    def process_rows(self, rows, output_dict):
        for row in rows:
            if row:
                try:
                    date = datetime.datetime.strptime(
                        self.preproc_date(row[self.date_col]),
                        self.date_format
                    ).date().strftime('%Y-%m-%d')
                    date_data = output_dict.get(date, {})
                    count = int(row[self.total_col])
                    if not count:
                        continue
                    earning = Decimal(row[self.total_money_col].replace('$', ''))
                    date_data[self.stock_name] = (count, earning, self.currency)
                    output_dict[date] = date_data
                except ValueError:
                    continue


class StockStatNotUniqDate(StockStatBase):

    def process_rows(self, rows, output_dict):
        for row in rows:
            if row:
                try:
                    date = datetime.datetime.strptime(
                        self.preproc_date(row[self.date_col]),
                        self.date_format
                    ).date().strftime('%Y-%m-%d')
                except (ValueError, IndexError):
                    continue
                date_data = output_dict.get(date, {})
                total_count, total_money, currency = date_data.get(
                    self.stock_name, (0, Decimal(0), self.currency))
                new_total_count = total_count + 1
                new_total_money = total_money + Decimal(row[self.money_col].replace('$', ''))
                date_data[self.stock_name] = (new_total_count, new_total_money, currency)
                output_dict[date] = date_data
