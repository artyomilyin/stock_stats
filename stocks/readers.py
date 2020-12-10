from datetime import datetime

from .base import (
    StockStatNotUniqDate,
    StockStatUniqDate,
)


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
    currency = "JPY"


class FreePikStat(StockStatUniqDate):
    stock_name = 'FreePik'
    date_col = 0
    date_format = '%Y-%m-%d'
    delimiter = ','
    total_col = 1
    total_money_col = 2
    currency = "EUR"

    def preproc_date(self, date):
        return datetime.fromtimestamp(int(date)/1000).strftime(self.date_format)


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
