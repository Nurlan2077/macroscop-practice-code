import sqlite3


# Добавление человека в базу данных.
def add_person(external_id):
    connect = sqlite3.connect("clients.db")
    cursor = connect.cursor()

    cursor.execute("INSERT INTO clients VALUES ('" + external_id + "', 0)")
    connect.commit()
    connect.close()


# Получает количество баллов клиента по идентификатору.
def get_person_points(external_id):
    connect = sqlite3.connect("clients.db")
    cursor = connect.cursor()

    cursor.execute('SELECT points_num FROM clients WHERE id = "' + external_id + '"')
    points_num = cursor.fetchall()
    connect.commit()
    connect.close()

    return points_num[0][0]


# Изменение количества баллов.
def update_person_points(external_id, new_points):
    connect = sqlite3.connect("clients.db")
    cursor = connect.cursor()

    cursor.execute('UPDATE clients SET points_num = ' + str(new_points) + ' WHERE id = "' + external_id + '"')
    connect.commit()
    connect.close()
