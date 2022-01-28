import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from data import group_token
from random import randrange
from get_frends import search_friends, get_photo, sort_likes
from dbase import engine, Session, add_user, add_user_photos, check_db_user

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)
session = Session()
connection = engine.connect()

def listener():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                msg_text = event.text
                return msg_text, event.user_id

def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})

if __name__ == '__main__':
    while True:
        msg_text, user_id = listener()
        if msg_text.lower() == "привет":
            write_msg(user_id, f"Вас приветствует программа VKinder, введите параметры поиска друзей.\n"
                      f"Введите пол кандидата М/Ж:"
                      )
            msg_text, user_id = listener()
            if msg_text.lower() == "Ж":
                sex = 1
            elif msg_text.lower() == "M":
                sex = 2
            else:
                write_msg(user_id, f"Пол введён не корректно")
            write_msg(user_id, f"Введите возраст кондидата, от 18 лет:")
            msg_text, user_id = listener()
            age = int(msg_text)
            write_msg(user_id, f"Введите город, в котором вы проживаете:")
            msg_text, user_id = listener()
            city = msg_text.lower()
            friends_list = search_friends(sex, age, city)
            for i in range(len(friends_list)):
                dating_user = check_db_user(friends_list[i][3])
                for friend in friends_list:
                    friend_photo = get_photo(friend[3])
                    if friend_photo == 'нет доступа к фото':
                        continue
                    friend_photo_sorted = sort_likes(friend_photo)
                    write_msg(user_id, f' {friend[0]} {friend[1]} {friend[2]}')
                    write_msg(user_id, f' фото1:', attachment=friend_photo_sorted[0][1])
                    write_msg(user_id, f' фото2:', attachment=friend_photo_sorted[1][1])
                    write_msg(user_id, f' фото3:', attachment=friend_photo_sorted[2][1])
                    try:
                        add_user(user_id, friends_list[i][3], friends_list[i][1], friends_list[i][0], city, friends_list[i][2])
                        add_user_photos(user_id, friend_photo_sorted[0][1], friend_photo_sorted[1][1], friend_photo_sorted[2][1])
                    except AttributeError:
                        write_msg(user_id, 'Вы не зарегистрировались!')
                        break



