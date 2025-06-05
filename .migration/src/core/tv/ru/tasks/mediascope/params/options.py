import enum


class Options(enum.StrEnum):
    KIT_ID = 'kitId'
    ISSUE_TYPE = 'issueType'


class KitIds(enum.IntEnum):
    """База данных."""

    TV_INDEX_ALL_RUSSIA = 1
    TV_INDEX_RUSSIA_100K_PLUS = 2
    TV_INDEX_CITIES = 3
    TV_INDEX_PLUS_ALL_RUSSIA = 4
    TV_INDEX_PLUS_RUSSIA_100K_PLUS = 5
    TV_INDEX_MOSCOW = 6


class BaseDateCalcTypes(enum.StrEnum):
    BY_RESEARCH_PERIOD = 'BY_RESEARCH_PERIOD'
    BY_ISSUES = 'BY_ISSUES'


class TotalTypes(enum.StrEnum):
    TOTAL_CHANNELS = 'TotalChannels'
    TOTAL_TV_SET = 'TotalTVSet'
    TOTAL_CHANNELS_THEM = 'TotalChannelsThem'


class IssueTypes(enum.StrEnum):
    PROGRAM = 'PROGRAM'
    BREAK = 'BREAKS'
    AD = 'AD'


class ViewingSubjects(enum.StrEnum):
    RESPONDENT = 'RESPONDENT'
    HOUSEHOLD = 'HOUSEHOLD'
