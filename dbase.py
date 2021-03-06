import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import sqlalchemy as sq
from random import randrange
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from data import user_token, version, group_token
from sqlalchemy.exc import IntegrityError, InvalidRequestError

auth_vk = vk_api.VkApi(token=user_token)
longpoll = VkLongPoll(auth_vk)
Base = declarative_base()
engine = sq.create_engine('postgresql://user@localhost:5432/vkinder_db', client_encoding='utf8')
Session = sessionmaker(bind=engine)
vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)
session = Session()
connection = engine.connect()

class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)

class Friends(Base):
    __tablename__ = 'dating_user'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    vk_id = sq.Column(sq.Integer, unique=True)
    first_name = sq.Column(sq.String)
    second_name = sq.Column(sq.String)
    city = sq.Column(sq.String)
    link = sq.Column(sq.String)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id', ondelete='CASCADE'))

class Photos(Base):
    __tablename__ = 'photos'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    link_photo = sq.Column(sq.String)
    count_likes = sq.Column(sq.Integer)
    id_dating_user = sq.Column(sq.Integer, sq.ForeignKey('dating_user.id', ondelete='CASCADE'))

def write_msg(user_id, message, attachment=None):
    vk.method('messages.send',
              {'user_id': user_id,
               'message': message,
               'random_id': randrange(10 ** 7),
               'attachment': attachment})

def check_db_user(ids):
    dating_user = session.query(Friends).filter_by(
        vk_id=ids).first()
    return dating_user

def add_user(event_id, vk_id, first_name, second_name, city, link, id_user):
    try:
        new_user = Friends(
            vk_id=vk_id,
            first_name=first_name,
            second_name=second_name,
            city=city,
            link=link,
            id_user=id_user
        )
        session.add(new_user)
        session.commit()
        write_msg(event_id,
                  '???????????????????????? ?????????????? ???????????????? ?? ??????????????????')
        return True
    except (IntegrityError, InvalidRequestError):
        write_msg(event_id,
                  '???????????????????????? ?????? ?? ??????????????????.')
        return False

def add_user_photos(event_id, link_photo, count_likes, id_dating_user):
    try:
        new_user = Photos(
            link_photo=link_photo,
            count_likes=count_likes,
            id_dating_user=id_dating_user
        )
        session.add(new_user)
        session.commit()
        write_msg(event_id,
                  '???????? ???????????????????????? ?????????????????? ?? ??????????????????')
        return True
    except (IntegrityError, InvalidRequestError):
        write_msg(event_id,
                  '???????????????????? ???????????????? ???????? ?????????? ????????????????????????(?????? ??????????????????)')
        return False

if __name__ == '__main__':
    Base.metadata.create_all(engine)