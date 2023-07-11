import requests

access_token = input('Введите свой токен доступа: ')
group_id = input('Введите идентификатор группы: ')
api_version = 5.131
print('')



#Нахождение спам-постов
print('!!!!!!!!!!!!!!! ПОИСК СПАМА !!!!!!!!!!!!!!!\n')
count = 100
offset = 0
all_count = 0 #Суммарное число репостов всех постов группы
all_post = [] #Массив id всех постов группы
SPAM = 0

#Нахождение нормального количества репостов
while offset < 1000:
    response = requests.get('https://api.vk.com/method/wall.get',
                            params={
                                'domain': group_id,
                                'access_token': access_token,
                                'v': api_version,
                                'count': count,
                                'offset': offset
                            }
                            )
    wall = response.json()
    offset += 100
    if 'response' in wall:
        wall_items = wall['response']['items']
        wall_count = wall['response']['count'] #Количество постов в группе
        for post in wall_items:
            post_id = post['id']
            all_post.append(post_id)
            owner_id = post['owner_id']
            reposts_response = requests.get('https://api.vk.com/method/wall.getById',
                                            params={
                                                'posts': f'{owner_id}_{post_id}',
                                                'access_token': access_token,
                                                'v': api_version
                                            })

            reposts_data = reposts_response.json()
            if 'response' in reposts_data:
                repost_count = reposts_data['response'][0]['reposts']['count']
                all_count += repost_count

number = (all_count / wall_count) + 1 #Норма количества репостов
print('Норма репостов: не более', int(number))
print('')
for post in range(0, wall_count):
    reposts_response = requests.get('https://api.vk.com/method/wall.getById',
                                    params={
                                        'posts': f'{owner_id}_{all_post[post]}',
                                        'access_token': access_token,
                                        'v': api_version
                                    })

    reposts_data = reposts_response.json()
    if 'response' in reposts_data:
        repost_count = reposts_data['response'][0]['reposts']['count']
        if repost_count > number:
            SPAM = 1
            print(f"Подозрение на спам поста с ID: {all_post[post]};  Количество репостов - {repost_count} \n")
if (SPAM == 0):
    print('Нет подозрений на спам в этой группе')
print('')



#Нахождение фейковых аккаунтов
print('!!!!!!!!!!!!!!! ПОИСК ФЕЙКОВ !!!!!!!!!!!!!!!\n')

#Нахождение id аккаунтов, состоящих в группе и их колличества
response = requests.get('https://api.vk.com/method/groups.getMembers',
                        params={
                            'group_id': group_id,
                            'access_token': access_token,
                            'v': api_version
                        }
                        )
info_items = response.json()["response"]["items"]
info_count = response.json()["response"]["count"] #Колличество участников группы
FAKE = 0
for man in range (0, info_count):
        fields = 'is_closed,first_name,last_name,sex,bdate,about,relation,status,country,city,career,universities,counters,blacklisted'
        url = f'https://api.vk.com/method/users.get?user_ids={info_items[man]}&fields={fields}&access_token={access_token}&v={api_version}'
        response = requests.get(url)
        data = response.json()
        if 'response' in data:
            user = data['response'][0]
            fake = 0
            if (user["is_closed"] == True):
                print(f'Невозможно получить информацию о пользователе {user["first_name"]} {user["last_name"]} c ID: {user["id"]}, так как у него скрытый профиль \n')
            else:
                if  (user.get("first_name", "") == ""):
                    fake += 1
                if (user.get("last_name", "") == ""):
                    fake += 1
                if  (user.get("sex") == 0):
                    fake += 1
                if  (user.get("bdate", "") == ""):
                    fake += 1
                if  (user.get("about", "") == ""):
                    fake += 1
                if  (user.get("status", "") == ""):
                    fake += 1
                if  (user.get("country", {}).get("title", "") == ""):
                    fake += 1
                if  (user.get("city", {}).get("title", "") == ""):
                    fake += 1
                if (user.get("counters", {}).get("friends", 0) <= 20):
                    fake += 1
            if (fake > 4):
                FAKE = 1
                print(f'Подозрения на фейк {user["first_name"]} {user["last_name"]} c ID: {user["id"]}')
                print('Не указаны:')
                if  (user.get("first_name", "") == ""):
                   print('Имя')
                if (user.get("last_name", "") == ""):
                    print('Фамилия')
                if  (user.get("sex") == 0):
                    print('Пол')
                if  (user.get("bdate", "") == ""):
                    print('Дата рождения')
                if  (user.get("about", "") == ""):
                    print('О себе')
                if  (user.get("status", "") == ""):
                    print('Статус')
                if  (user.get("country", {}).get("title", "") == ""):
                    print('Страна')
                if  (user.get("city", {}).get("title", "") == ""):
                    print('Город')
                if (user.get("counters", {}).get("friends", 0) <= 20):
                    print('Количество друзей меньше 20')
                print('')
        else:
            print('Ошибка соединения \n')

if (FAKE == 0):
    print('Нет подозрений на фейк в этой группе')
