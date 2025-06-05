import enum


class PrimeTime(enum.StrEnum):
    PRIME = 'Prime'
    OFF_PRIME = 'Off prime'


class SpotPosition(enum.StrEnum):
    FIRST = 'Первый'
    SECOND = 'Второй'
    MIDDLE = 'Середина'
    PENULTIMATE = 'Предпоследний'
    LAST = 'Последний'


class SaleType(enum.StrEnum):
    GRP = 'GRP'
    MIN = 'Min'


class Column(enum.StrEnum):
    DATE = 'Date'
    BREAK_START_TIME = 'Break Start time'
    SPOT_ID = 'Spot ID'
    SPOTS_COUNT = 'Spots count'
    SPOT_END_TIME = 'Spot end time'
    SPOT_POSITION = 'Spot position'
    SPOT_START_TIME = 'Spot start time'
    SPOT_TV_COMPANY = 'Spot TVCompany'
    SPOT_EXPECTED_DURATION = 'Spot expected duration'
    POSITION = 'Position'
    MONTH = 'Month'
    WEEK = 'Week'
    PRIME = 'Prime'
    AUDIENCE = 'Audience'
    ROUND = 'Round'
    SELLER = 'Seller'
    BLK_GRP_PERCENT = 'BlkGRP%'
    GRP = 'GRP'
    GRP_30_SEC = 'GRP [30 сек.]'
    BLK_GRP_PERCENT_30_SEC = 'BlkGRP% [30 сек.]'
    BLK_GRP_PERCENT_30_SEC_ROUNDED = 'BlkGRP% [30 сек.] (округл.)'
    BLK_GRP_PERCENT_30_SEC_NOT_ROUNDED = 'BlkGRP% [30 сек.] (округл. точн.)'
    GRP_30_SEC_ROUNDED = 'GRP [30 сек.] (округл.)'
    GRP_30_SEC_NOT_ROUNDED = 'GRP [30 сек.] (округл. точн.)'
    GRP_30_SEC_LOOKUP = 'GRP [30 sec.]'
    DOUBLE_SHARE = 'Double Share'
    UNIQUE_ID = 'unique_id'
    COUNT = 'count'


class ConfigKey(enum.StrEnum):
    AUDIENCE = 'audience'
    ROUND = 'round'
    SELLER = 'seller'


class Constant(enum.IntEnum):
    STANDARD_DURATION_SECONDS = 30
    STANDARD_ROUNDING_PRECISION = 2


class Seller(enum.StrEnum):
    IMS_MN = 'IMS/MN'
    VI = 'VI'
    TBM = 'TBM'
