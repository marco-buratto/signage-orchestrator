from django.db import connection
from django.db import transaction
from django.utils.html import strip_tags

from backend.helpers.Exception import CustomException
from backend.helpers.Database import Database as DBHelper


class Event:

    # Table: event



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int) -> dict:
        c = connection.cursor()

        try:
            c.execute(
                "SELECT id, group_id, playlist_id, start_date, end_date, IFNULL(text, '') AS text "
                "FROM event "
                "WHERE id = %s", [id]
            )

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"Signage Orchestrator Backend": "Non existent event"})
        except Exception as e:
            raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list(groupId: int = 0, startDate: str = "", endDate: str = "") -> list:
        q = "WHERE 1=1 "
        v = []

        if groupId:
            q += "AND group_id = %s "
            v.append(groupId)
        if startDate:
            q += "AND start_date = %s "
            v.append(startDate)
        if endDate:
            q += "AND end_date = %s "
            v.append(endDate)

        c = connection.cursor()

        try:
            c.execute(
                "SELECT id, group_id, playlist_id, start_date, end_date, IFNULL(text, '') AS text "
                "FROM event " + q, v
            )

            return DBHelper.asDict(c)
        except Exception as e:
            raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def add(data: dict) -> int:
        s = ""
        keys = "("
        values = []

        c = connection.cursor()

        # Build SQL query according to dict fields (only whitelisted fields pass).
        for k, v in data.items():
            s += "%s,"
            keys += k + ","
            values.append(strip_tags(v)) # no HTML allowed.

        keys = keys[:-1]+")"

        try:
            with transaction.atomic():
                c.execute("INSERT INTO event "+keys+" VALUES ("+s[:-1]+")", values) # user data are filtered by the serializer.

                return c.lastrowid
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=400, payload={"Signage Orchestrator Backend": "Duplicated event"})
            else:
                raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def modify(id: int, data: dict) -> None:
        sql = ""
        values = []
        c = connection.cursor()

        # %s placeholders and values for SET.
        for k, v in data.items():
            sql += k + "=%s,"
            if v is not None:
                values.append(strip_tags(v)) # no HTML allowed.
            else:
                values.append(v)

        values.append(id)

        try:
            c.execute("UPDATE event SET " + sql[:-1] + " WHERE id = %s", values) # user data are filtered by the serializer.
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                raise CustomException(status=400, payload={"Signage Orchestrator Backend": "Duplicated event"})
            else:
                raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def linkToGroup(id: int, groupId: int) -> None:
        try:
            Event.modify(id, {
                "group_id": groupId
            })
        except Exception as e:
            raise e



    @staticmethod
    def linkToPlaylist(id: int, playlistId: int) -> None:
        try:
            Event.modify(id, {
                "playlist_id": playlistId
            })
        except Exception as e:
            raise e



    @staticmethod
    def unlinkFromPlaylist(id: int, playlistId: int) -> None:
        try:
            Event.modify(id, {
                "playlist_id": None
            })
        except Exception as e:
            raise e



    @staticmethod
    def delete(id: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM event WHERE id = %s", [id])
        except Exception as e:
            raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()
