import re
from enum import Enum
from typing import Optional


class UpdateType(Enum):
    NEW = 1
    SALE = 2
    RAISE = 3


def get_report_messages(report: dict) -> (Optional[str], Optional[str], Optional[str]):
    new_candles_message_html = _get_category_message(report['new_candles'], UpdateType.NEW)
    lower_prices_message_html = _get_category_message(report['lowered_prices'], UpdateType.SALE)
    higher_prices_message_html = _get_category_message(report['raised_prices'], UpdateType.RAISE)

    return new_candles_message_html, lower_prices_message_html, higher_prices_message_html


def _get_category_message(updates: dict, update_type: UpdateType = UpdateType.NEW) -> Optional[str]:
    regex = r'^(.*?)\s+3'

    if updates is None or len(updates) == 0:
        return None

    message: str
    match update_type:
        case UpdateType.NEW:
            message = 'Here are new candles:\n'
        case UpdateType.SALE:
            message = 'Here are <b>lowered</b> prices:\n'
        case UpdateType.RAISE:
            message = 'Here are <b>raised</b> prices:\n'
        case _:
            raise Exception('Incorrect update type label was passed.')

    for update in updates:
        name_match = re.match(regex, update['name'])
        if name_match:
            name = name_match.group(1).strip()
        else:
            continue  # Skip this update if name doesn't match the regex

        match update_type:
            case UpdateType.NEW:
                to_append = f'<a href="{update["url"]}">{name}</a>\n'
            case UpdateType.SALE | UpdateType.RAISE:
                old_price = update["old_price"]
                new_price = update["new_price"]
                to_append = f'<a href="{update["url"]}">{name}</a>: {old_price} -> {new_price}\n'

        message += to_append

    return message
