from flask import Flask, jsonify, request
import json
from Database import *
from masini import *
from startRecord import *

app = Flask(__name__)

def findJSON(file_path):
    global dictionary
    try:
        with open(file_path, 'r') as file:
            dictionary = json.load(file)
        return dictionary
    except FileNotFoundError as e:
        print('Fisierul nu a putut fi găsit! Trebuie creat')
        dictionary = []
        return dictionary

@app.route('/cars', methods=['POST'])
def findcarsinJSON():
    input = request.json
    carCheck = False
    for car in dictionary:
        if car['id'] == input['id']:
            carCheck = True
            break
    if carCheck:
        return jsonify({"message": "Car found"}), 200
    else:
        dictionary.append(input)
        return jsonify({"message": "Added!"}), 200

@app.route('/cars', methods=['GET'])
def readfromDatabase():
    dates = request.args.get('dates')

    if not dates:
        return jsonify({"message": "No date provided"}), 400

    query = """
        SELECT idcar,
               MIN(dates) AS entry,
               MAX(dates) AS `exit`
        FROM cars
        WHERE DATE(dates) = %s
        AND direction IN ("exit", "entry")
        GROUP BY idcar
    """

    db = Database(host="localhost", user="root", password="root", database="cars")
    try:
        result = db.resultConection(query, (dates,))
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    if not result:
        return jsonify({"message": "No cars found for the specified date in the database"}), 400

    carsfromfile = [car['Registernumber']for car in dictionary]
    carsFromdb = [column[0] for column in result]
    carstoPaste = [car for car in carsFromdb if car not in carsfromfile]

    if not carstoPaste:
        return jsonify({"message": "No new cars found in database"}), 404
    else:
        rec = Record(host="localhost", user="root", password="root", database="cars")
        staying_times = rec.record(dates)

        return jsonify({
            "message": "New cars also found in db",
            "cars": carstoPaste,
            "staying_times": staying_times
        }), 200


@app.route('/cars/<name>', methods=['PUT'])
def addfromFile(name, file='cars.json'):
    try:
        with open(file, 'r') as f:
            dictonar = json.load(f)
            print(f"File loaded with {len(dictonar)} cars")
    except FileNotFoundError as e:
        dictonar = []
        return jsonify({"message": "File not found"}), 404
    
    if not dictonar:
        return jsonify({"message": "No cars to add!"}), 400
    
    db = Database(host="localhost", user="root", password="root", database="cars")
    existing_cars_query = "SELECT Registernumber FROM cars"
    try:
        existing_cars = db.resultConection(existing_cars_query)
        existing_cars_set = set(car[0] for car in existing_cars)  
    except Exception as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500

    for car in dictonar:
        if car['Registernumber'] not in existing_cars_set and car['owner'] == name:
            query1 = '''  
                INSERT INTO cars.cars(`Registernumber`, `brand`, `color`, `owner`, `direction`, `dates`) 
                VALUES(%s, %s, %s, %s, %s, %s)
            '''
            values = (car['Registernumber'], car['brand'], car['color'], car['owner'], car['direction'], car['dates'])
            
            try:
                print(f"Inserting car: {car['Registernumber']}") 
                db.executeConection(query1, values)
                print(f"Car {car['Registernumber']} added successfully")
            except Exception as e:
                print(f"Error inserting car {car['Registernumber']}: {str(e)}")
                return jsonify({"message": f"Error inserting car {car['Registernumber']}: {str(e)}"}), 500
    
    return jsonify({"message": f"Cars added successfully for {name}"}), 200


if __name__ == "__main__":
    file_path = 'cars.json'
    findJSON(file_path)
    app.run(host="0.0.0.0", port=5000, debug=True)
