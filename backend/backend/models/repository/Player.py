from django.db import connection
from django.db import transaction
from django.utils.html import strip_tags

from backend.helpers.Exception import CustomException
from backend.helpers.Database import Database as DBHelper


class Player:

    # Table: player



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int = 0, uuid: str = "") -> dict:
        c = connection.cursor()

        try:
            if id:
                # Get from id normally.
                c.execute(
                    "SELECT id, group_id, uuid, player_type, name, IFNULL(position, '') AS position, address, IFNULL(comment, '') AS comment, IFNULL(metrics, '') AS metrics, IFNULL(ssh_public_key, '') AS ssh_public_key "
                    "FROM player "
                    "WHERE id = %s", [id]
                )
            if uuid:
                # Get from uuid.
                c.execute(
                    "SELECT id, group_id, uuid, player_type, name, IFNULL(position, '') AS position, address, IFNULL(comment, '') AS comment, IFNULL(metrics, '') AS metrics "
                    "FROM player "
                    "WHERE uuid = %s", [uuid]
                )

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"Signage Orchestrator Backend": "Non existent player"})
        except Exception as e:
            raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list(groupId: int = 0) -> list:
        c = connection.cursor()

        try:
            if groupId:
                c.execute(
                    "SELECT id, uuid, player_type, name, IFNULL(position, '') AS position, address, IFNULL(comment, '') AS comment, IFNULL(metrics, '') AS metrics, IFNULL(ssh_public_key, '') AS ssh_public_key "
                    "FROM player "
                    "WHERE group_id = %s", [groupId]
                )
            else:
                c.execute(
                    "SELECT id, uuid, player_type, name, IFNULL(position, '') AS position, address, IFNULL(comment, '') AS comment, IFNULL(metrics, '') AS metrics "
                    "FROM player"
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
                c.execute("INSERT INTO player "+keys+" VALUES ("+s[:-1]+")", values) # user data are filtered by the serializer.

                return c.lastrowid
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=409, payload={"Signage Orchestrator Backend": "Duplicated player"})
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
            c.execute("UPDATE player SET " + sql[:-1] + " WHERE id = %s", values) # user data are filtered by the serializer.
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                raise CustomException(status=400, payload={"Signage Orchestrator Backend": "Duplicated player"})
            else:
                raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def addOrModifyIfExists(data: dict) -> None:
        doAdd = True
        s = sql = ""
        keys = "("
        values = []
        c = connection.cursor()

        try:
            with transaction.atomic():
                c.execute("SELECT id FROM player WHERE uuid = %s", [data["uuid"]])
                if DBHelper.asDict(c):
                    doAdd = False

                if doAdd:
                    for k, v in data.items():
                        s += "%s,"
                        keys += k + ","
                        values.append(strip_tags(v))
                    keys = keys[:-1]+")"

                    c.execute("INSERT INTO player "+keys+" VALUES ("+s[:-1]+")", values)
                else:
                    for k, v in data.items():
                        if k != "uuid":
                            sql += k + "=%s,"
                            if v is not None:
                                values.append(strip_tags(v))
                            else:
                                values.append(v)
                    values.append(data["uuid"])

                    c.execute("UPDATE player SET " + sql[:-1] + " WHERE uuid = %s", values)
        except Exception as e:
            raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def linkToGroup(id: int, groupId: int) -> None:
        try:
            Player.modify(id, {
                "group_id": groupId
            })
        except Exception as e:
            raise e



    @staticmethod
    def unlinkFromGroup(id: int, groupId: int) -> None:
        try:
            Player.modify(id, {
                "group_id": None
            })
        except Exception as e:
            raise e
