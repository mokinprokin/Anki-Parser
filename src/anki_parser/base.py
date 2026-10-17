import logging
from abc import ABC


class BaseExecutionComponent(ABC):
    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"anki_parser.{self.__class__.__name__}")