import logging
import re

import httpx

logger = logging.getLogger(__name__)

HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
NIQQUD_RE = re.compile(r"[\u0591-\u05C7]")

_ABBREV_MAP = {"מתני׳": "מתניתין", "גמ׳": "גמרא"}

_BASE = "https://www.sefaria.org.il"
_PATH = "/api/v3/texts/{}.{}{}"
_PARAMS = "version=primary&fill_in_missing_segments=1&return_format=wrap_all_entities"


def strip_html_tags(text: str) -> str:
    #cleaned = HTML_TAG_PATTERN.sub("", text)
    #cleaned = cleaned.replace("[", "").replace("]", "")
    cleaned = text.replace("\n", " ").replace("\r", " ").replace("\\", "").replace("–", " ").replace("—", " ")
    return re.sub(r"\s+", " ", cleaned).strip()


def remove_nikud(text: str) -> str:
    return NIQQUD_RE.sub("", text).strip()


def normalize_hebrew_text(text: str) -> str:
    for abbrev, expansion in _ABBREV_MAP.items():
        text = text.replace(abbrev, expansion)
    return text.replace("״", '"')


def clean_sefaria_line(line: str) -> str:
    return normalize_hebrew_text(remove_nikud(strip_html_tags(line)))


class SefariaClient:
    """Fetches Gemara text from the Sefaria v3 REST API."""

    def fetch_daf(self, massechet_name: str, daf_id: int) -> str | None:
        texts = []
        for amud in ("A", "B"):
            url = f"{_BASE}{_PATH.format(massechet_name, daf_id, amud)}?{_PARAMS}"
            logger.info("Fetching Sefaria: %s", url)
            try:
                response = httpx.get(url, timeout=30)
                if response.status_code == 404:
                    logger.debug("Amud not found: %s", url)
                    continue
                response.raise_for_status()
                versions = response.json().get("versions", [])
                if not versions:
                    logger.debug("No versions at %s", url)
                    continue
                lines = versions[0].get("text", [])
                cleaned = [clean_sefaria_line(line) for line in lines if isinstance(line, str)]
                text = " ".join(cleaned).strip()
                if text:
                    texts.append(text)
            except httpx.HTTPStatusError as e:
                logger.warning("Sefaria HTTP error %s: %s", url, e)
            except Exception as e:
                logger.warning("Failed to fetch %s: %s", url, e)

        return " ".join(texts) if texts else None
