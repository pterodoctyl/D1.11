import sys
import requests

base_url = "https://api.trello.com/1/{}"
board_id = "ugiG2O7N"

# Данные авторизации в API Trello
auth_params = {
    'key': "dee4442d8392908c23485c0bd62cd1a5",
    'token': "7361526b2b7c4b2a7ee46c6a533be577921829618f39caff50375e905d349674", }

def read():
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    for column in column_data:
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(f"\n{column['name']} ({len(task_data)})")
        if not task_data:
            print('\t' + '--Нет задач--')
            continue
        for task in task_data:
            print(f"\t\u2022 {task['name']} \t id: {task['id']}")
    print("\n")

def create(name, column_name):
	# Получим данные всех колонок на доске
	column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
	column_names =[]
	for column in column_data:
		column_names.append(column['name'])
		if column['name'] == column_name:
			requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
			print("\nЗадача создана")
			read()
			exit()
				
	if column_name not in column_names:
		print(f"\nСписок << {column_name} >> не найден. Все задачи:")
		read()

def move(name, column_name):
	# Получим данные всех колонок на доске
	column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
	# Находим все задачи с указанным именем
	search, column_names = [], []
	for column in column_data:
		column_names.append(column['name'])
		column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
		for task in column_tasks:
			if task['name'] == name:
				search.append((task['id'], column['name']))
	if column_name not in column_names or not search:
		print(f"\nСписок << {column_name} >> или задача << {name} >> не найдены. Все задачи:")
		read()
		exit()
	
	choice = 0
	
	# в случае нескольких задач с одинаковым заданием
	if len(search) > 1:
		print(f'У вас несколько задач с названием "{name}":')
		for id in search:
			print(f"{search.index(id) + 1} id: {id[0]} в списке {id[1]}")
		while True:
			try:
				choice = int(input(f"Выберите нужную задачу (1-{len(search)}): ")) - 1
				if choice not in range(len(search)):
					print("Введено некорректное значение")
					continue
				elif search[choice][1] == column_name:
					print("Задача уже находится в указанном списке")
					exit()
				id = search[choice][0]
				break
			except (IndexError, ValueError):
				print("Введено некорректное значение")
				continue
	
	id = search[choice][0]
	# Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
	for column in column_data:
		if column['name'] == column_name:
			# И выполним запрос к API для перемещения задачи в нужную колонку
			requests.put(base_url.format('cards') + '/' + id + '/idList', data={'value': column['id'], **auth_params})
			print("Задача перемещена")
     
def new_column(column_name):
	board_info = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()
	requests.post(base_url.format('lists') + '/', data={'name': column_name, 'idBoard': board_info['id'], **auth_params})
	print(f"Список {column_name} создан")
	read()


def usage():
	print("\nUsage:\n\tpython client.py \t - Список всех задач\
				\n\tpython client.py <options>\
				\n\t\t new <column_name> \t\t - Создать колонку <column_name>\
				\n\t\t create <name> <column_name> \t - Cоздать задачу <name> в колонке <column_name>\
				\n\t\t move <name> <column_name> \t - Переместить задачу <name> в колонку <column_name>\n")

if __name__ == "__main__":
	try:
		if len(sys.argv) == 1:
			read()
		elif sys.argv[1] == 'create':
			create(sys.argv[2], sys.argv[3])
		elif sys.argv[1] == 'move':
			move(sys.argv[2], sys.argv[3])
		elif sys.argv[1] == 'new':
			new_column(sys.argv[2])
		else:
			usage()
	except IndexError:
		usage()

