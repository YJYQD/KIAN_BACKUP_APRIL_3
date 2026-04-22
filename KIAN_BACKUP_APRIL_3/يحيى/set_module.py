import os
import colorsys
import sys

print('INSTALL MODULES ')



try: 
    import telebot 
except:
    os.system(f'"{sys.executable}" -m pip install pyTelegramBotAPI')
try: 
    import kvsqlite 
except:
    os.system(f'"{sys.executable}" -m pip install kvsqlite')

try: 
    import schedule 
except:
    os.system(f'"{sys.executable}" -m pip install schedule')

try: 
    import requests 
except:
    os.system(f'"{sys.executable}" -m pip install requests')

try: 
    import user_agent 
except:
    os.system(f'"{sys.executable}" -m pip install user_agent')

try: 
    import base64 
except:
    pass

try: 
    import ipaddress 
except:
    pass

try: 
    import struct 
except:
    pass

try: 
    import pathlib 
except:
    pass

try: 
    import typing 
except:
    pass

try: 
    import aiosqlite 
except:
    os.system(f'"{sys.executable}" -m pip install aiosqlite')

try: 
    import telethon 
except:
    os.system(f'"{sys.executable}" -m pip install telethon')

try: 
    import pyrogram 
except:
    os.system(f'"{sys.executable}" -m pip install pyrogram')

try: 
    import opentele
except:
    os.system(f'"{sys.executable}" -m pip install pyqt5')
    os.system(f'"{sys.executable}" -m pip install opentele')

try: 
    import secrets 
except:
    pass
