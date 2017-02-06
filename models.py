from peewee import *
from playhouse.pool import PooledPostgresqlExtDatabase

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
    password = IntegerField()

    class Meta:
        db_table = 'users'


class Room(BaseModel):
    name = CharField(unique=True)

    class Meta:
        db_table = 'rooms'

    def to_dict(self):
        return dict(self._data.items())


def init_db():
    try:
        db.connect()
        map(lambda l: db.drop_table(l, True, True), [Room])
        print "tables dropped"
        [m.create_table() for m in [Room]]
        print "tables created"
    except:
        db.rollback()
        raise

if __name__ == '__main__':
    init_db()
