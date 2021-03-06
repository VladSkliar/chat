from peewee import *
from playhouse.pool import PooledPostgresqlExtDatabase
import datetime

db = PooledPostgresqlExtDatabase(database="tzifpvtf", user="tzifpvtf",
                                 password="E4nmiUrYsxPsZi2g883Zxp-hE-SXkx-s", host="horton.elephantsql.com", port=5432,
                                 register_hstore=False, autorollback=True)
db.commit_select = True
db.autorollback = True


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    username = CharField(unique=True)
    password = CharField()

    class Meta:
        db_table = 'users'


class Room(BaseModel):
    name = CharField(unique=True)

    class Meta:
        db_table = 'rooms'

    def to_dict(self):
        return dict(self._data.items())


class Message(BaseModel):
    user = ForeignKeyField(User, related_name='messages')
    roomname = CharField()
    datetime = DateTimeField(default=datetime.datetime.now)
    message = CharField()

    class Meta:
        db_table = 'messages'

    def to_dict(self):
        data = dict(self._data.items())
        data.update({"username": self.user.username})
        data.update({"data": self.message})
        data.update({"datetime": "Created at {:d}:{:02d}".format(self.datetime.hour, self.datetime.minute)})
        return data


def init_db():
    try:
        db.connect()
        map(lambda l: db.drop_table(l, True, True), [User, Room, Message])
        print "tables dropped"
        [m.create_table() for m in [User, Room, Message]]
        print "tables created"
    except:
        db.rollback()
        raise

if __name__ == '__main__':
    init_db()
