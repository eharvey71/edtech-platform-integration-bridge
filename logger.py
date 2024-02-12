
import datetime

def log(message):
    dt = datetime.datetime.now()
    x = dt.strftime("%m-%d-%Y %H:%M:%S")
    f = open("./logs/log", "a")
    f.write("[" + x + "] " + message + "\n")
    f.close()