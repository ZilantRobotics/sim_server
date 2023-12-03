from argparse import ArgumentParser
from os import linesep

from strenum import StrEnum
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import app
from app.models import Roles, User

load_dotenv()


class Commands(StrEnum):
    NEW_USER = 'create_user'


argparser = ArgumentParser()
subparsers = argparser.add_subparsers(dest='command')
subparsers.required = True

create_user = subparsers.add_parser(
    Commands.NEW_USER,
    help='create new user'
)
create_user.add_argument(
    '--name', required=True, type=str, dest='name')
create_user.add_argument(
    '--mail', required=True, type=str, dest='email')
create_user.add_argument(
    '--pass', required=True, type=str, dest='password')
create_user.add_argument(
    '--role', default=Roles.common_folk.name,
    choices=[x.name for x in list(Roles)], dest='role')

arguments = argparser.parse_args()
role = Roles({f.name: f.value for f in list(Roles)}[arguments.role])
if arguments.command == Commands.NEW_USER:
    with app.create_app().app_context():
        user = User(
            email=arguments.email,
            name=arguments.name,
            password=generate_password_hash(arguments.password),
            role=arguments.role
        )
        app.db.session.add(user)
        app.db.session.commit()
