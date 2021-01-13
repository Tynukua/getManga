from urllib.parse import urlparse
from . import parsers

PARSERS = parsers.PARSERS
ParserABC = parsers.ParserABC

class Manga:
    def __init__(self, url: str = None, domain: str = None, id_: str = None):
        self._id = id_
        self._url = url
        self._domain = domain

        self._parsertype: ParserABC = None
        self._chooseparser()

        self.title = None
        self.cover = None
        self.description = None
        self.lang = None
        self.rating = None
        self.last_chapter = None
        self.last_volume = None
        self.authors = None
        self.contents = {} # key - volnum, value chapters

        self._parser: ParserABC = self._parsertype(self)

    def _chooseparser(self):
        if self._url:
            domain = urlparse(self._url).netloc
            if not domain in PARSERS:
                raise ValueError(f"Not supported domain {domain}")
            self._parsertype = PARSERS[domain]
            self._domain = domain
            self._id = self._parsertype.urlparse(self._url)
        if not self._domain and not self._id:
            raise ValueError(f"Parsing is imposible")
        self._parsertype = PARSERS[domain]
        
    async def parse(self):
        await self._parser.parse_info()
