"""
Messages classes ancestors.
"""

from abc import ABC, abstractmethod
# from bismuthcore.helpers import base_app_log


__version__ = "0.0.1"


class Message(ABC):
    """Abstract Ancestor for all messages. Supports both legacy and bin format"""

    __slots__ = ("_valid_answers", "_params", "_legacy_answer", "legacy_command")

    def __init__(self):
        # self.app_log = base_app_log(app_log)
        self.valid_answers = ()
        self.legacy_command = ""
        self._params = None
        self._legacy_answer = None

    @abstractmethod
    def valid(self) -> bool:
        """Is the received message valid or an "OK" status?"""
        pass

    @abstractmethod
    def to_legacy(self) -> object:
        """Native object payload to be json encoded by legacy transport layer"""
        pass

    @abstractmethod
    def set_legacy_answer(self, answer: object) -> None:
        pass

    @abstractmethod
    def valid_answer(self) -> bool:
        pass


class StringMessage(Message):
    """Abstract Ancestor for all messages. Supports both legacy and bin format"""

    def __init__(self, param: str):
        self._params = param

    def valid(self) -> bool:
        """Is the received message valid or an "OK" status?"""
        return True

    def to_legacy(self) -> str:
        return self._params
