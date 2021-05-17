# Over-the-air file that retrieve the game from GitHub
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

exec(urllib.request.urlopen("https://raw.githubusercontent.com/Jah-On/Ultimate-Connect-4/main/Connect4.py").read())
