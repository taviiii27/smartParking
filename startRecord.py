from abc import ABC, abstractmethod

class startRecord(ABC):
    def __init__(self, db):
        self.db = db

    @abstractmethod
    def createTableCars(self):
        pass

    @abstractmethod
    def writeCars(self):
        pass
