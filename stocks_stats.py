import os
import csv
from decimal import Decimal
from datetime import datetime

from stocks.readers import STOCK_CLASSES
from stocks.base import (
    OUTPUT_DIR,
    OUTPUT_FILE,
)


def process(stock_classes=STOCK_CLASSES):
    result = {}
    for stock_class in stock_classes:
        stock = stock_class()
        stock.read_files(result)
    return result


def generate_table(stats_dict, stock_classes=STOCK_CLASSES):

    def calc_currency(money, currency):
        point_replaced_money = str(money).replace('.', ',')
        if currency:
            template = "={point_replaced_money} * GOOGLEFINANCE(\"CURRENCY:{currency}USD\")"
            point_replaced_money = template.format(point_replaced_money=point_replaced_money, currency=currency)
        return point_replaced_money

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
            total, money, currency = stock_data.get(
                stock_class.stock_name, (0, Decimal(0), None))
            total_row += [total]
            money_row += [calc_currency(money, currency)]
        total_table += [total_row]
        money_table += [money_row]
    return total_table, money_table


def export_to_csv(table, prefix):
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = OUTPUT_FILE % (now, prefix)
    with open(filename, 'w', newline='') as output:
        writer = csv.writer(output, delimiter='\t')
        for row in table:
            writer.writerow(row)


def count_milestones(stats_dict):

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
    for date, data in sorted(stats_dict.items()):
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
    return result


if __name__ == "__main__":
    result = process()
    milestones = count_milestones(result)
    tables = generate_table(result)
    export_to_csv(tables[0], prefix='totalcount')
    export_to_csv(tables[1], prefix='moneytotal')
    export_to_csv([[key, *value]
                   for key, value in milestones.items()], prefix='milestones')
