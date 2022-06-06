import ast

import requests
from flask import Flask, request, jsonify, render_template
from multiprocessing import Process
import uuid
from requests.auth import HTTPBasicAuth
from flask_cors import CORS

import db_controller

app = Flask(__name__)

act_external_id = 0
act_image_bytes = 0


# Внесение нового пользователя. Подготавливает данные для подтверждения добавления.
@app.route('/add_person', methods=['POST'])
def index():
    global act_external_id, act_image_bytes

    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        json = request.json
        # print(json)

        act_image_bytes = [json["image_bytes"]]

        return json
    else:
        return 'Content-Type should be json compatible!'


cors = CORS(app, resources={r"/confirm_add_person": {"origins": "*"},
                            r"/client_points": {"origins": "*"},
                            r"/add_points": {"origins": "*"},
                            r"/withdraw_points": {"origins": "*"}})


# Подтверждает добавление нового клиента и делает запись в БД.
@app.route('/confirm_add_person', methods=['POST'])
def confirm_add_person():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        json = request.json
        print(json)

        url = 'http://127.0.0.1:8080/api/faces?module=light'

        external_id = str(uuid.uuid4())

        send_data = {
            "external_id": external_id,
            "face_images": act_image_bytes
        }

        print(send_data)
        x = requests.post(url, json=send_data, auth=HTTPBasicAuth('root', ''))
        print(x.text)

        if x.text.startswith("{\"ErrorMessage"):
            print("error here haha")

            json = ast.literal_eval(x.text.replace("'", ""))

        else:
            print("no error, have a nice day!")
            db_controller.add_person(external_id)
            print("person added")

        return json
    else:
        return 'Content-Type should be json compatible!'


# Выводит страницу администратора.
@app.route('/admin', methods=['GET'])
def admin_page():
    return render_template('admin/admin.html')


# Добавление баллов клиента.
@app.route('/add_points', methods=['POST'])
def add_points():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        json = request.json
        # print(json)

        id = json["external_id"]
        purchase_amount = json["purchase_amount"]

        actual_points = db_controller.get_person_points(id)

        # 0.05 - 5% от суммы заказа - можно менять.
        new_points = int(actual_points + purchase_amount * 0.05)

        res = jsonify({"new_points": new_points})

        print("Новые баллы: " + str(new_points))

        db_controller.update_person_points(id, new_points)

        return res
    else:
        return 'Content-Type should be json compatible!'


# Снятие баллов клиента.
@app.route('/withdraw_points', methods=['POST'])
def withdraw_points():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        json = request.json
        # print(json)

        id = json["external_id"]
        withdraw_num = json["withdraw_num"]

        actual_points = db_controller.get_person_points(id)
        new_points = int(actual_points - withdraw_num)

        res = jsonify({"new_points": new_points})

        print("Новые баллы: " + str(new_points))

        db_controller.update_person_points(id, new_points)

        return res
    else:
        return 'Content-Type should be json compatible!'


# Выводит страницу клиента.
@app.route('/client', methods=['GET'])
def client_page():
    return render_template('client/client.html')


# Выводит страницу клиента с его баллами.
@app.route('/client_points', methods=['POST'])
def show_client_points():
    content_type = request.headers.get('Content-Type')

    if content_type == 'application/json':
        json = request.json
        print(json)
        print(db_controller.get_person_points(json["external_id"]))

        client_points = db_controller.get_person_points(json["external_id"])

        send_data = {
            "client_points": client_points
        }

        print(send_data)

        return jsonify(send_data)
    else:
        return 'Content-Type should be json compatible!'


if __name__ == "__main__":
    app.run(debug=True, port=9091)
