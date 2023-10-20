from django.db import connection
from django.db import transaction
from django.utils.html import strip_tags

from backend.helpers.Exception import CustomException
from backend.helpers.Database import Database as DBHelper


class Playlist:

    # Table: playlist



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def get(id: int) -> dict:
        c = connection.cursor()

        try:
            c.execute(
                "SELECT id, playlist_type, name, IFNULL(mediaconf, '') AS mediaconf, IFNULL(transition, 0) AS transition, IFNULL(blend, 0) AS blend "
                "FROM playlist "
                "WHERE id = %s", [id]
            )

            return DBHelper.asDict(c)[0]
        except IndexError:
            raise CustomException(status=404, payload={"Signage Orchestrator Backend": "Non existent playlist"})
        except Exception as e:
            raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def list(filter: str = "") -> list:
        condition = "WHERE 1"
        c = connection.cursor()

        if filter == "signage":
            condition = "WHERE playlist_type LIKE 'signage'"
        if filter == "slideshow":
            condition = "WHERE playlist_type LIKE 'slideshow'"

        try:
            c.execute(
                "SELECT id, playlist_type, name, IFNULL(mediaconf, '') AS mediaconf, IFNULL(transition, 0) AS transition, IFNULL(blend, 0) AS blend "
                "FROM playlist " + condition
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
                c.execute("INSERT INTO playlist "+keys+" VALUES ("+s[:-1]+")", values) # user data are filtered by the serializer.

                return c.lastrowid
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                        raise CustomException(status=400, payload={"Signage Orchestrator Backend": "Duplicated playlist"})
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
            values.append(strip_tags(v)) # no HTML allowed.

        values.append(id)

        try:
            c.execute("UPDATE playlist SET " + sql[:-1] + " WHERE id = %s", values) # user data are filtered by the serializer.
        except Exception as e:
            if e.__class__.__name__ == "IntegrityError" \
                    and e.args and e.args[0] and e.args[0] == 1062:
                raise CustomException(status=400, payload={"Signage Orchestrator Backend": "Duplicated playlist"})
            else:
                raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()



    @staticmethod
    def delete(id: int) -> None:
        c = connection.cursor()

        try:
            c.execute("DELETE FROM playlist WHERE id = %s", [id])
        except Exception as e:
            raise CustomException(status=400, payload={"Signage Orchestrator Backend": e.__str__()})
        finally:
            c.close()
