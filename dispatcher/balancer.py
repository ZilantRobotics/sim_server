from dataclasses import dataclass
from enum import auto
from multiprocessing import Array, Queue
from multiprocessing.managers import BaseProxy
from typing import cast, List, Dict

from strenum import StrEnum

from sim_runner.src.api.core import Command


class Status(StrEnum):
    ok = auto()
    running = auto()
    error = auto()
    dead = auto()


@dataclass
class Client:
    name: str
    uuid: str
    status: Status


@dataclass
class CommandRequest:
    command_id: int
    client_uuid: str
    command: Command


class BaseBalancer:
    def __init__(self, *args, **kwargs):
        pass

    def check_failed_msgs(self):
        pass

    def route_command(self, command: Command):
        pass


class DummyBalancer:
    clients: BaseProxy
    data: BaseProxy
    responses: BaseProxy
    id: int = 0

    def initialize(self, clients: BaseProxy, data: BaseProxy, responses: BaseProxy):
        self.clients = clients
        self.data = data
        self.responses = responses

    def route_message(self, command: Command):
        if not self.clients:
            return -1
        print('routing', str(command))
        cast(Queue, self.data).put(
            CommandRequest(
                command_id=self.id,
                client_uuid=list(cast(Dict[str, Client], self.clients).values())[0].uuid,
                command=command
            )
        )
        self.id += 1



