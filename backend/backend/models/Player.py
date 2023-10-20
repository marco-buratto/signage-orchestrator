from __future__ import annotations
from typing import List, TYPE_CHECKING

from django.conf import settings
from django.core.cache import cache

from backend.models.repository.Player import Player as Repository

if TYPE_CHECKING:
    from backend.models.Group import Group

from backend.helpers.Misc import Misc
from backend.helpers.Exception import CustomException
from backend.helpers.Cryptography import Cryptography


class Player:
    def __init__(self, id: int = 0, uuid: str = "", loadGroup: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.uuid: str = uuid
        self.player_type: str = ""
        self.name: str = ""
        self.position: str = ""
        self.address: str = ""
        self.comment: str = ""
        self.metrics: str = ""
        self.ssh_public_key: str = ""

        self.group: Group = None

        self.__load(loadGroup=loadGroup)



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



    def linkToGroup(self, groupId: int) -> None:
        try:
            Repository.linkToGroup(self.id, groupId)
        except Exception as e:
            raise e



    def unlinkFromGroup(self, groupId: int) -> None:
        try:
            Repository.unlinkFromGroup(self.id, groupId)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(groupId: int = 0, loadOnlyAlive: bool = True, loadGroup: bool = False) -> List[Player]:
        players = []

        try:
            if groupId:
                l = Repository.list(groupId) # players belonging to a group.
            else:
                l = Repository.list() # all players.

            for player in l:
                if loadOnlyAlive:
                    # Load only alive players.
                    if cache.get(player["uuid"]):
                        players.append(
                            Player(id=player["id"], loadGroup=loadGroup)
                        )
                else:
                    # Load all saved players.
                    players.append(
                        Player(id=player["id"], loadGroup=loadGroup)
                    )

            return players
        except Exception as e:
            raise e



    @staticmethod
    def addOrUpdate(data: dict) -> None:
        # try:
        #     Repository.add(data)
        # except CustomException as e:
        #     if e.status == 409:
        #         Player(uuid=data["uuid"]).modify(data)
        #     else:
        #         raise e
        # -> ids increase at every run.

        try:
            Repository.addOrModifyIfExists(data)

            # Save information into a global cache.
            cache.set(data["uuid"], "added", timeout=settings.PLAYER_KEEPALIVE)

            # Save received SSH public key into known hosts.
            Cryptography.addKnownHost(data["address"], data["ssh_public_key"])
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self, loadGroup: bool = False) -> None:
        from backend.models.Group import Group

        try:
            info = Repository.get(id=self.id, uuid=self.uuid)

            # Set attributes.
            for k, v in info.items():
                if k == "group_id":
                    if loadGroup:
                        # Load Group composition, if set.
                        if v:
                            try:
                                self.group = Group(id=v)
                            except CustomException as e:
                                if e.status == 404:
                                    self.group = None
                                else:
                                    raise e
                    else:
                        del self.group
                else:
                    setattr(self, k, v)
        except Exception as e:
            raise e
