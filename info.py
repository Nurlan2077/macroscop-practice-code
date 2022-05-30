import requests
import json
import ast
import uuid
import socketio

# Создает сокет.
sio = socketio.Client()


# Событие на подключение клиента.
@sio.event
def connect():
    print('connection established')


# Событие на отключение клиента.
@sio.event
def disconnect():
    sio.disconnect()


# Подключение к хосту вебсокета.
sio.connect('http://localhost:9092')


# Получает данные о лицах с вебкамеры.
def get_info_from_webcam():
    # Base64 обнаруженного лица.
    image_bytes = 0

    external_id = 0

    # Постоянный http для приема для данных от системы Macroscop.
    r = requests.get('http://127.0.0.1:8080/event?login=root&password=&responsetype=json',
                     stream=True)

    # Проходит по каждой строке полученных данных.
    for line in r.iter_lines():
        # Если есть внешний id, то отправляет сообщение по сокету для вывода информации на интерфейс.
        if line.decode('utf-8').startswith("\t\"ExternalId\""):
            external_id = ast.literal_eval("{" + line.decode('utf-8') + "}")["ExternalId"]
            print("Распознан")

            if external_id != "":
                sio.emit('external_id', str(external_id))
        # Если id нет, отправляет данные о лице на сервер - для дальнейшего подтверждения добавления нового клиента.
        elif line.decode('utf-8').startswith("\t\"ImageBytes\""):
            image_bytes = ast.literal_eval("{" + line.decode('utf-8') + "}")["ImageBytes"]
            # print(image_bytes)

            url = 'http://127.0.0.1:9091/add_person'
            send_data = {"image_bytes": str(image_bytes)}

            x = requests.post(url, json=send_data)

# Запускает бесконечный приём данных.
get_info_from_webcam()
