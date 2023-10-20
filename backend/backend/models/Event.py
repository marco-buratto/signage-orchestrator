from __future__ import annotations
from typing import List, TYPE_CHECKING

from backend.models.repository.Event import Event as Repository

if TYPE_CHECKING:
    from backend.models.Group import Group
    from backend.models.Playlist import Playlist

from backend.helpers.Misc import Misc
from backend.helpers.Exception import CustomException
from backend.helpers.Datetime import Datetime
from backend.helpers.Log import Log


class Event:
    def __init__(self, id: int, loadGroup: bool = False, loadGroupPlayers: bool = False, loadPlaylist: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.start_date: str = ""
        self.end_date: str = ""
        self.text: str = ""

        self.group: Playlist = None
        self.playlist: Playlist = None

        self.__load(loadGroup=loadGroup, loadGroupPlayers=loadGroupPlayers, loadPlaylist=loadPlaylist)



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



    def linkToGroup(self, groupId: int) -> None:
        try:
            Repository.linkToGroup(self.id, groupId)
        except Exception as e:
            raise e



    def linkToPlaylist(self, playlistId: int) -> None:
        try:
            Repository.linkToPlaylist(self.id, playlistId)
        except Exception as e:
            raise e



    def unlinkFromPlaylist(self, playlistId: int) -> None:
        try:
            Repository.unlinkFromPlaylist(self.id, playlistId)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(groupId: int = 0, startDate: str = "", endDate: str = "", loadGroup: bool = False, loadGroupPlayers: bool = False, loadPlaylist: bool = False) -> List[Event]:
        events = []

        if startDate == "now":
            startDate = Datetime.now()
        if endDate == "now":
            endDate = Datetime.now()

        try:
            if groupId:
                ev = Repository.list(groupId=groupId, startDate=startDate, endDate=endDate) # events belonging to a group.
            else:
                ev = Repository.list(startDate=startDate, endDate=endDate) # all events.

            for event in ev:
                events.append(
                    Event(id=event["id"], loadGroup=loadGroup, loadGroupPlayers=loadGroupPlayers, loadPlaylist=loadPlaylist)
                )

            return events
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        try:
            Repository.add(data) # @todo: forbid overlap.
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self, loadGroup: bool = False, loadGroupPlayers: bool = False, loadPlaylist: bool = False) -> None:
        from backend.models.Group import Group
        from backend.models.Playlist import Playlist

        try:
            info = Repository.get(self.id)

            # Set attributes.
            for k, v in info.items():
                if k == "group_id":
                    if loadGroup:
                        # Load Group composition, if set.
                        if v:
                            try:
                                self.group = Group(id=v, loadPlayers=loadGroupPlayers)
                            except CustomException as e:
                                if e.status == 404:
                                    self.group = None
                                else:
                                    raise e
                    else:
                        del self.group
                elif k == "playlist_id":
                    if loadPlaylist:
                        # Load Playlist composition, if set.
                        if v:
                            try:
                                self.playlist = Playlist(id=v)
                            except CustomException as e:
                                if e.status == 404:
                                    self.playlist = None
                                else:
                                    raise e
                    else:
                        del self.playlist
                else:
                    setattr(self, k, v)
        except Exception as e:
            raise e
