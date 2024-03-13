import json
import logging
import traceback


class Log:
    @staticmethod
    def log(o: any, title: str = "") -> None:
        log = logging.getLogger("django")
        if title:
            if "_" in title:
                for j in range(79):
                    title = title + "_"
            log.debug(title)

        try:
            if not isinstance(o, str):
                log.debug(json.dumps(o))
            else:
                log.debug(o)
        except Exception:
            log.debug(o)

        if title:
            title = ""
            for j in range(80):
                title = title + "_"
            log.debug(title)



    @staticmethod
    def clog(o: any) -> None:
        Log.log(o, "_")



    @staticmethod
    def dump(o: any) -> None:
        import re
        log = logging.getLogger("django")

        oOut = dict()
        oVars = vars(o)
        oDir = dir(o)

        for i, v in enumerate(oDir):
            if v in oVars:
                oOut[v] = oVars[v]
            else:
                if not re.search("^__(.*)__$", str(v)):
                    oOut[v] = getattr(o, v)

        log.debug(oOut)



    @staticmethod
    def logException(e: Exception) -> None:
        # Logs the stack trace information and the raw output if any.
        Log.log(traceback.format_exc(), 'Error')

        try:
            Log.log(e.raw, 'Raw backend data')
        except Exception:
            pass



    @staticmethod
    def actionLog(o: any, user: dict = None) -> None:
        # Sends input logs to the "backend" logger (settings).
        user = user or {}
        log = logging.getLogger("django")

        try:
            if "username" in user:
                log.debug("[" + user['username'] + "] " + o)
            else:
                log.debug(o)
        except Exception:
            pass
