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
                "SELECT "
                    "id, "
                    "playlist_type, "
                    "name, "
                
                    "IFNULL(url, '') AS url, "
                    "IFNULL(compatibility, 0) AS compatibility, "
                    "IFNULL(pointer_disabled, 0) AS pointer_disabled, "
                    "IFNULL(reset_time_min, 0) AS reset_time_min, "
                    "IFNULL(reload_time_s, 0) AS reload_time_s, "
                
                    "IFNULL(mediaconf, '') AS mediaconf, "                
                    "IFNULL(transition, 0) AS transition, "
                    "IFNULL(blend, 0) AS blend "
                "FROM playlist "
                "WHERE id = %s", [id]
            )

            o = DBHelper.asDict(c)[0]
            o["compatibility"] = bool(o.get("compatibility", 0))
            o["pointer_disabled"] = bool(o.get("pointer_disabled", 0))

            return o
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

        if filter == "web":
            condition = "WHERE playlist_type LIKE 'web'"
        if filter == "slideshow":
            condition = "WHERE playlist_type LIKE 'slideshow'"

        try:
            c.execute(
                "SELECT "
                    "id, "
                    "playlist_type, "
                    "name, "
                
                    "IFNULL(url, '') AS url, "
                    "IFNULL(compatibility, 0) AS compatibility, "
                    "IFNULL(pointer_disabled, 0) AS pointer_disabled, "
                    "IFNULL(reset_time_min, 0) AS reset_time_min, "
                    "IFNULL(reload_time_s, 0) AS reload_time_s, "
                
                    "IFNULL(mediaconf, '') AS mediaconf, "                
                    "IFNULL(transition, 0) AS transition, "
                    "IFNULL(blend, 0) AS blend "
                "FROM playlist " + condition
            )

            l = DBHelper.asDict(c)
            for el in l:
                el["compatibility"] = bool(el.get("compatibility", 0))
                el["pointer_disabled"] = bool(el.get("pointer_disabled", 0))

            return l
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
            if k in ("compatibility", "pointer_disabled"):
                values.append(int(v))
            else:
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
            if k != "playlist_type":
                sql += k + "=%s,"
                if k in ("compatibility", "pointer_disabled"):
                    values.append(int(v))
                else:
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
