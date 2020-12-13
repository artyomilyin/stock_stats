import os
import csv
from decimal import Decimal
from datetime import datetime

from stocks.readers import STOCK_CLASSES
from stocks.base import (
    OUTPUT_DIR,
    OUTPUT_FILE,
)


class App:

    def __init__(self, stock_classes):
        self.stock_classes = stock_classes

    def _process(self):
        result = {}
        for stock_class in self.stock_classes:
            stock = stock_class()
            stock.read_files(result)
        self.stats_dict = result

    def _generate_table(self):

        def calc_currency(money, currency):
            point_replaced_money = str(money).replace('.', ',')
            if currency:
                template = "={point_replaced_money} * GOOGLEFINANCE(\"CURRENCY:{currency}USD\")"
                point_replaced_money = template.format(point_replaced_money=point_replaced_money, currency=currency)
            return point_replaced_money

        total_table = []
        money_table = []
        first_row = ["Date"] + \
            [stock_class.stock_name for stock_class in self.stock_classes]
        total_table += [first_row]
        money_table += [first_row]
        for date, stock_data in sorted(self.stats_dict.items()):
            total_row = [date]
            money_row = [date]
            for stock_class in self.stock_classes:
                total, money, currency = stock_data.get(
                    stock_class.stock_name, (0, Decimal(0), None))
                total_row += [total]
                money_row += [calc_currency(money, currency)]
            total_table += [total_row]
            money_table += [money_row]
        return total_table, money_table

    def _export_to_csv(self, table, prefix):
        if not os.path.exists(OUTPUT_DIR):
            os.mkdir(OUTPUT_DIR)
        now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = OUTPUT_FILE % (now, prefix)
        with open(filename, 'w', newline='') as output:
            writer = csv.writer(output, delimiter='\t')
            for row in table:
                writer.writerow(row)

    def _count_milestones(self):

        def calc_currency(money, currency):
            if currency:
                if currency not in _currencies:
                    _currencies[currency] = Decimal(input(f"{currency} to USD exchange rate:"))
                rate = _currencies[currency]
                return money * rate
            return money

        _currencies = {}
        result = {}
        new_total = new_money = 0
        for date, data in sorted(self.stats_dict.items()):
            old_total = new_total
            old_money = new_money
            new_total += sum([stock_data[0] for _, stock_data in data.items()])
            new_money += sum([calc_currency(stock_data[1], stock_data[2]) for _, stock_data in data.items()])
            if old_total // 100 < new_total // 100:
                milestone = result.get(date, [None, None])
                milestone[1] = (new_total // 100) * 100
                result[date] = milestone
            if old_money // 100 < new_money // 100:
                milestone = result.get(date, [None, None])
                milestone[0] = (new_money // 100) * 100
                result[date] = milestone
        self.milestones = result

    def run(self):
        self._process()
        self._count_milestones()
        tables = self._generate_table()
        self._export_to_csv(tables[0], prefix='totalcount')
        self._export_to_csv(tables[1], prefix='moneytotal')
        self._export_to_csv([[key, *value]
                       for key, value in self.milestones.items()], prefix='milestones')


if __name__ == "__main__":
    app = App(STOCK_CLASSES)
    app.run()
