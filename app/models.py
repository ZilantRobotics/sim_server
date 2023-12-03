from enum import auto, Enum

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import ChoiceType
from strenum import StrEnum

from app import db


class Roles(Enum):
    spectator = 0
    common_folk = 1
    admin = 2


class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = Column(String(100), unique=True)
    password = Column(String(256))
    name = Column(String(32))
    role = Column(ChoiceType(Roles, impl=Integer()), default=Roles.common_folk, nullable=False)
