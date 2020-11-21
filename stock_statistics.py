import os
import csv
import json
import datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, 'input')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
FILES_TO_EXCLUDE = ['.gitignore']
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'export_%s_%s.csv')


class JsonReaderMixin:

    def read_files(self, output_dict):
        for file in self.files_list:
            with open(os.path.join(self.dirname, file), 'r') as input_file:
                j = json.loads(input_file.read())
                reader = self.flatten_json(j)
                self.process_rows(reader, output_dict)


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
                    date_data[self.stock_name] = (
                        count, Decimal(row[self.total_money_col].replace('$', '')))
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
    date_format = '%Y-%m-%d'
    delimiter = ','
    total_col = 1
    total_money_col = 11


class DreamsTimeStat(StockStatUniqDate):
    stock_name = 'Dreamstime'
    date_col = 0
    date_format = '%B %d, %Y'
    delimiter = '\t'
    total_col = 2
    total_money_col = 1


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


class VectorStockStat(StockStatNotUniqDate):
    stock_name = 'VectorStock'
    date_col = 0
    date_format = '%d/%m/%Y, %H:%M:%S %p'
    delimiter = '\t'
    money_col = 4


class VectorStockStat(StockStatNotUniqDate):
    stock_name = 'VectorStock'
    date_col = 0
    date_format = '%d/%m/%Y, %H:%M:%S %p'
    delimiter = '\t'
    money_col = 4


class CanStockStat(StockStatNotUniqDate):
    stock_name = 'CanStock'
    date_col = 2
    date_format = '%Y-%m-%d'
    delimiter = ','
    money_col = 5


class PixtaStockStat(StockStatNotUniqDate):
    stock_name = 'PixtaStock'
    date_col = 2
    date_format = '%m/%d/%Y %H:%M:%S'
    delimiter = ','
    money_col = 4


class FreePikStat(StockStatUniqDate):

    stock_name = 'FreePik'
    date_col = 0
    date_format = '%Y-%m-%d'
    delimiter = ','
    total_col = 1
    total_money_col = 2

    def preproc_date(self, date):
        return datetime.datetime.fromtimestamp(int(date)/1000).strftime(self.date_format)


STOCK_CLASSES = [
    ShutterStat,
    FreePikStat,
    AdobeStockStat,
    IStockStat,
    DreamsTimeStat,
    RF123Stat,
    BigstockStat,
    DepositStat,
    CanStockStat,
    VectorStockStat,
    PixtaStockStat,
]


def process(stock_classes=STOCK_CLASSES):
    result = {}
    for stock_class in stock_classes:
        stock = stock_class()
        stock.read_files(result)
    return result


def generate_table(stats_dict, stock_classes=STOCK_CLASSES):
    total_table = []
    money_table = []
    first_row = ["Date"] + \
        [stock_class.stock_name for stock_class in stock_classes]
    total_table += [first_row]
    money_table += [first_row]
    for date, stock_data in sorted(stats_dict.items()):
        total_row = [date]
        money_row = [date]
        for stock_class in stock_classes:
            total, money = stock_data.get(
                stock_class.stock_name, (0, Decimal(0)))
            total_row += [total]
            money_row += [str(money).replace('.', ',')]
        total_table += [total_row]
        money_table += [money_row]
    return total_table, money_table


def export_to_csv(table, prefix):
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    now = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = OUTPUT_FILE % (now, prefix)
    with open(filename, 'w', newline='') as output:
        writer = csv.writer(output, delimiter='\t')
        for row in table:
            writer.writerow(row)


def count_milestones(stats_dict):
    result = {}
    old_total = old_money = new_total = new_money = 0
    for date, data in sorted(stats_dict.items()):
        old_total = new_total
        old_money = new_money
        new_total += sum([stock_data[0] for _, stock_data in data.items()])
        new_money += sum([stock_data[1] for _, stock_data in data.items()])
        if old_total // 100 < new_total // 100:
            milestone = result.get(date, [None, None])
            milestone[1] = (new_total // 100) * 100
            result[date] = milestone
        if old_money // 100 < new_money // 100:
            milestone = result.get(date, [None, None])
            milestone[0] = (new_money // 100) * 100
            result[date] = milestone
    return result


if __name__ == "__main__":
    result = process()
    milestones = count_milestones(result)
    tables = generate_table(result)
    export_to_csv(tables[0], prefix='totalcount')
    export_to_csv(tables[1], prefix='moneytotal')
    export_to_csv([[key, *value]
                   for key, value in milestones.items()], prefix='milestones')
