from __future__ import annotations
from typing import List

from backend.models.repository.Playlist import Playlist as Repository

from backend.helpers.Misc import Misc
from backend.helpers.Log import Log


class Playlist:
    def __init__(self, id: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.playlist_type: str = ""
        self.name: str = ""
        self.mediaconf: str = "" # base64.
        self.transition: int = 0
        self.blend: int = 0

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def repr(self):
        return Misc.deepRepr(self)



    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.id, data)

            for k, v in Misc.toDict(data).items():
                setattr(self, k, v)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id)
            del self
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(filter: str = "") -> List[Playlist]:
        playlists = []

        try:
            for playlist in Repository.list(filter=filter):
                playlists.append(
                    Playlist(id=playlist["id"])
                )

            return playlists
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        try:
            Repository.add(data)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.id)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
