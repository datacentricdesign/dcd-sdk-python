
import logging
import os
import time
# from .thing import Thing
from .properties.property import Property

class ThingLogger:

    def __init__(self, thing):

        self.LOG_PATH = os.getenv("LOG_PATH", "./logs/")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
        self.DATA_PATH = os.getenv("DATA_PATH", "./data/")

        self.thing = thing
        self.set_log_level(self.LOG_LEVEL)
        self.setup_logger()

    def set_log_level(self, log_level: str):
        if log_level == "INFO":
            logging.basicConfig(level=logging.INFO)
        elif log_level == "ERROR":
            logging.basicConfig(level=logging.ERROR)
        elif log_level == "WARNING":
            logging.basicConfig(level=logging.WARNING)
        elif log_level == "DEBUG":
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.error("Unknown log level " + log_level)

    def setup_logger(self):
        self.logger = logging.getLogger(self.thing.thing_id or "Thing")
        self.log_folder = self.LOG_PATH + "/" + self.thing.thing_id
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)
        self.data_folder = self.DATA_PATH + "/" + self.thing.thing_id
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        fh = logging.FileHandler(
            self.log_folder + "/" + str(time.strftime("%Y-%m-%d_%H")) + ".log")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def error(self, payload):
        self.logger.error(payload)

    def debug(self, payload):
        self.logger.debug(payload)
    
    def info(self, payload):
        self.logger.info(payload)
    
    def warn(self, payload):
        self.logger.warn(payload)

    def data(self, property: Property):
        try:
            file = open(self.data_folder + "/" + property.property_id + "_" + str(time.strftime("%Y-%m-%d_%H")) + ".csv", "a")
            for val in property.values:
                file.write(",".join(str(x) for x in val))
                file.write("\n")
        except Exception as e:
            self.debug("[logger] Could not log data in file.")
            self.debug(e)
        finally:
            file.close()