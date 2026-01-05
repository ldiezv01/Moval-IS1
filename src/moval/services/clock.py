from datetime import datetime
from zoneinfo import ZoneInfo

class Clock:
    def now(self):
        return datetime.now(ZoneInfo("Europe/Madrid"))
