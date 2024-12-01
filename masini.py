import json
from startRecord import *
import datetime
from Database import *
class Masina(startRecord):
    def __init__(self, RegisterNumber, brand, color, owner, nume_fisier='cars.json'):
        self.RegisterNumber = RegisterNumber
        self.brand = brand
        self.color = color
        self.owner = owner
        try:
            with open(nume_fisier, 'r') as f:
                self.listaExtrasa = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print("Fisier negasit")

    def createTableCars(self, query):
        query = '''  
            CREATE TABLE `cars`.`cars` ( 
                `idcar` INT NOT NULL AUTO_INCREMENT, 
                `Registernumber` VARCHAR(45) NOT NULL, 
                `brand` VARCHAR(45) NOT NULL, 
                `color` VARCHAR(45) NOT NULL,
                `owner` VARCHAR(45) NOT NULL, 
                `dates` DATETIME NOT NULL, 
                `direction` VARCHAR(45) NOT NULL,
                PRIMARY KEY (`idcar`)
            );
        '''
        self.db.executeConection(query)

    def writeCars(self, masina):
        listaExtrasa = []
        for car in self.listaExtrasa:
            if car['RegisterNumber'] == masina['RegisterNumber']:
                print('Masina exista deja!')
            self.listaExtrasa.append(masina)
            return listaExtrasa
        try:
            with open('cars.json', 'w') as file:
                json.dump(listaExtrasa, file)
        except IOError as e:
            print("Fisierul nu s-a putut salva!")

class Inregistrare(Database):
    def record(self, dates):
        query = """
            SELECT idcar,
                   MIN(dates) AS entry,
                   MAX(dates) AS `exit`
            FROM cars
            WHERE DATE(dates) = %s
            AND direction IN ("exit", "entry")
            GROUP BY idcar
        """
        result = self.resultConection(query, (dates,))
        oremasiniCautate = {}
        try:
            for masina in result:
                idcar, exit, entry = masina
                if isinstance(exit, str):
                    exit = datetime.datetime.strptime(exit, '%Y-%m-%d %H:%M:%S')
                if isinstance(entry, str):
                    entry = datetime.datetime.strptime(entry, '%Y-%m-%d %H:%M:%S')
                if isinstance(exit, datetime.datetime) and isinstance(entry, datetime.datetime):
                    stayingh = (exit - entry).total_seconds() / 3600 
                    oremasiniCautate[idcar] = stayingh
            return oremasiniCautate
        except Exception as e:
            print(f"Eroare la calcularea timpului: {str(e)}")
            return {}
