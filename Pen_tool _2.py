import subprocess
import threading
import mechanize
import LogEditor
import platform
import argparse
import datetime
import difflib
import socket
import copy
import time
import sys
import os

from termcolor import colored

# from Threads import MyThread

class PenTool:

    def __init__(self):
        self.__Log = LogEditor.LogFile()
        self.open_ports = list()
        self.vulnerable_urls = list()


    def ping(self, hostname):

        started_time = datetime.datetime.now().strftime("%H:%M:%S")
	if platform.system().lower() == "windows":
	    parametre = "-n"
	else:
	    parametre = "-c"

        command = ["ping", parametre, "1", hostname]
        process_statu = None
        try:
            subprocess.check_output(command)
            process_statu = "Başarılı"
            ret = "{0} adresinden cevap alındı!".format(hostname)
        except:
            ret = "{0} adresinden cevap alınamadı.".format(hostname)
            process_statu = "Başarısız"
        finished_time = datetime.datetime.now().strftime("%H:%M:%S")  # İşlem burada bittiğinden dolayı bitiş
                                                                      # zamanını buraya yerleştirdik
        process_name = "Ping"
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        details = "{0} adresine ping ataması gerçekleştirilmiştir.\n".format(hostname)\

        self.__Log.insert_to_log(process_name, process_statu, date, started_time, finished_time, details)
        return ret

    