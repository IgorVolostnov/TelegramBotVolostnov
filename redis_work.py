import redis
import json

red = redis.Redis(
  host='redis-19616.c1.asia-northeast1-1.gce.cloud.redislabs.com',
  port=19616,
  password='pmrPV5ZfIwpFOB9K5VLizdhYV7sbwPpb')


# dict1 = {'key1': 'value1', 'key2': 'value2'}  # создаём словарь для записи
# red.set('dict1', json.dumps(dict1))  # с помощью функции dumps() из модуля json превратим наш словарь в строчку
# converted_dict = json.loads(red.get('dict1'))  # с помощью знакомой нам функции превращаем данные,
# # полученные из кеша обратно в словарь
# print(type(converted_dict))  # убеждаемся, что мы получили действительно словарь
# print(converted_dict)  # ну и выводим его содержание

# red.delete('dict1')  # удаляются ключи с помощью метода .delete()
# print(red.get('dict1'))

cont = True

while cont:
    action = input('action:\t')
    if action == 'write':
        name = input('name:\t')
        phone = input('phone:\t')
        red.set(name, phone)
    elif action == 'read':
        name = input('name:\t')
        phone = red.get(name)
        if phone:
            print(f'{name}\'s phone is {str(phone)}')
    elif action == 'delete':
        name = input('name:\t')
        phone = red.delete(name)
        if phone:
            print(f"{name}'s phone is deleted")
        else:
            print(f"Not found {name}")
    elif action == 'stop':
        break
