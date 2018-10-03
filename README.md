# Telegram Bot Librarry

### Usage:
```python
from tbotlib import Telegram
from tbotlib import Request
from tbotlib import Message

bot = Telegram(token)
resp = bot.get_resp()

for msg in resp: print Message(msg)
```

