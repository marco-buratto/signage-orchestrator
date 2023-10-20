from datetime import datetime, timezone


class Datetime:
    @staticmethod
    def now() -> str:
        return str(datetime.now(timezone.utc).astimezone()).split(".")[0]
