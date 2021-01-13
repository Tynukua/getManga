from abc import ABC, abstractmethod, abstractclassmethod

class ParserABC(ABC):
    def __init__(self, manga):
        self._manga = manga
        self._page: str = None
        self.contents = {}

    @abstractclassmethod
    def urlparse(cls, url: str)->str:
        pass

    @abstractmethod
    async def parse_info(self):
        pass

    @abstractmethod
    async def parse_images(self, vol = None, ch = None):
        pass
    
