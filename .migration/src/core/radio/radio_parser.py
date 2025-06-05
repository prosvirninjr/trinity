from app_assets import (
    load_advertisers,
    load_broadcast,
    load_drivetimes,
    load_placement,
    load_radiostations,
    load_status,
)
from core.utils.parser import Parser


class RadioParser(Parser):
    @staticmethod
    def parse_advertiser(advertiser: str) -> str | None:
        choices = load_advertisers()
        parsed_advertiser: str | None = Parser.parse_object(advertiser, choices)

        return parsed_advertiser

    @staticmethod
    def parse_radiostation(radiostation: str) -> str | None:
        choices = load_radiostations()
        parsed_radiostation: str | None = Parser.parse_object(radiostation, choices)

        return parsed_radiostation

    @staticmethod
    def parse_broadcast(broadcast: str) -> str | None:
        choices = load_broadcast()
        parsed_broadcast: str | None = Parser.parse_object(broadcast, choices)

        return parsed_broadcast

    @staticmethod
    def parse_placement(placement: str) -> str | None:
        choices = load_placement()
        parsed_placement: str | None = Parser.parse_object(placement, choices)

        return parsed_placement

    @staticmethod
    def parse_status(status: str) -> str | None:
        choices = load_status()
        parsed_status: str | None = Parser.parse_object(status, choices)

        return parsed_status

    @staticmethod
    def parse_drivetime(drivetime: str) -> str | None:
        choices = load_drivetimes()
        parsed_drivetime: str | None = Parser.parse_object(drivetime, choices)

        return parsed_drivetime
