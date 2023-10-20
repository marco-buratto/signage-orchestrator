from __future__ import annotations
from typing import List, TYPE_CHECKING

from backend.models.repository.Group import Group as Repository

if TYPE_CHECKING:
    from backend.models.Player import Player

from backend.helpers.Misc import Misc
from backend.helpers.Log import Log


class Group:
    def __init__(self, id: int, loadPlayers: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.name: str = ""
        self.comment: str = ""

        self.players: List[Player] = []

        self.__load(loadPlayers=loadPlayers)



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



    def linkPlayer(self, playerId: int) -> None:
        from backend.models.Player import Player

        try:
            Player(id=playerId).linkToGroup(groupId=self.id)
        except Exception as e:
            raise e



    def unlinkPlayer(self, playerId: int) -> None:
        from backend.models.Player import Player

        try:
            Player(id=playerId).unlinkFromGroup(self.id)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(loadPlayers: bool = False) -> List[Group]:
        groups = []

        try:
            for group in Repository.list():
                groups.append(
                    Group(id=group["id"], loadPlayers=loadPlayers)
                )

            return groups
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

    def __load(self, loadPlayers: bool = False) -> None:
        from backend.models.Player import Player

        try:
            info = Repository.get(self.id)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)

            if loadPlayers:
                for player in Player.list(groupId=self.id):
                    self.players.append(
                        Player(player.id)
                    )
            else:
                del self.players
        except Exception as e:
            raise e
