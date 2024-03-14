from bs4 import BeautifulSoup
from termcolor import colored
from timeit import default_timer as timer


class openFanbaseXml(object):
    def __init__(self, file_name):
        self.file_name = file_name

    def __enter__(self):
        print(colored("Opening:", "blue"), f"'{self.file_name}'")
        self.file = open(self.file_name, "r", encoding="utf-8")
        text = (
            self.file.read()
        )  # .decode('utf-8', "replace")#.encode("utf-32", "replace")
        xml_soup = BeautifulSoup(text, features="lxml")
        print(colored("Opened, ready for reading:", "blue"), f"'{self.file_name}'")
        return xml_soup

    def __exit__(self, *args):
        print(colored("Closing:", "blue"), f"'{self.file_name}'")
        self.file.close()


class Timer:
    def __init__(self):
        self._start_time = None
        self.delta = None

    def start(self):
        self._start_time = timer()

    def stop(self):
        if self._start_time is None:
            raise Exception(f"Timer is not running. Use .start() to start it")

        self.delta = timer() - self._start_time
        self._start_time = None
        return self.delta

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exc_info):
        self.stop()
