from peewee import *

database = PostgresqlDatabase('chat_project', user='chat_root_user')


class BaseModel(Model):
    class Meta:
        database = database


class User(BaseModel):
    username = CharField(unique=True)
    password = IntegerField()

    class Meta:
        db_table = 'users'