from typing import Dict

from .abcparser import ParserABC
from .readmanga import ReadManga


PARSERS: Dict[str,ParserABC] = {
        'readmanga.live': ReadManga,
        'mintmanga.live': ReadManga,
}


