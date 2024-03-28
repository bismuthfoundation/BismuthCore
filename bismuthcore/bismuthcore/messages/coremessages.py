""" """

from bismuthcore.messages.basemessages import StringMessage


class VersionMessage(StringMessage):
    """Version message, communication starter"""

    __slots__ = ("ok",)

    def __init__(self, version: str):
        # self.app_log = base_app_log(app_log)
        super().__init__(version)
        self._valid_answers = ("str",)
        self.legacy_command = "version"
        self.ok = False

    def set_legacy_answer(self, answer: object) -> None:
        self.ok = True if answer == "ok" else False

    def valid_answer(self) -> bool:
        return self.ok
