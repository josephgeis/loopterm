# -*- coding: utf-8 -*-
import sys
import time
import threading
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)


class Spinner:
    CHARS = '⠙⠸⠴⠦⠇⠋'

    def __init__(self, message):
        self.message = message
        self.run = False
        self.job = threading.Thread(None, self.spin)
        self.index = 0

    def spin(self):
        while self.run:
            self.generate_string()
            time.sleep(0.1)

    def generate_string(self):
        string = f"\r{Fore.MAGENTA}{self.CHARS[self.index % len(self.CHARS)]} {Fore.WHITE}{self.message}"
        sys.stdout.write(string)
        sys.stdout.flush()
        self.index += 1

    def start(self):
        self.run = True
        self.job.start()

    def stop(self):
        self.run = False
        sys.stdout.write("\033K\n")
