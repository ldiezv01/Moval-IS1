from datetime import datetime, timezone

class Clock:
        def now_utc(self):
            return datetime.now(timezone.utc)