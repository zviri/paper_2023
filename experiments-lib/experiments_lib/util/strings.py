import re
from typing import Optional

import unidecode


def remove_accents(s) -> str:
    return unidecode.unidecode(s)


def normalize_whitespace(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())


def remove_whitespace(s: str) -> str:
    return re.sub(r"\s+", "", s)


def string_id(s: str) -> str:
    return re.sub(r"\W+", "", remove_accents(s)).lower()


def compare_normalized(str1: str, str2: str) -> bool:
    return string_id(str1) == string_id(str2)


def ocred_str2int(int_string: str) -> Optional[int]:
    recovered_str = (
        int_string.lower()
        .replace("s", "5")
        .replace("l", "1")
        .replace("|", "1")
        .replace("o", "0")
        .replace("z", "2")
        .replace("b", "8")
    )

    cleaned_str = re.sub("[^0-9]", "", recovered_str)
    if cleaned_str.isdigit():
        return int(cleaned_str)
    return None
