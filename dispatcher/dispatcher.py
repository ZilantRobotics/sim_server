from __future__ import annotations
import asyncio
import json
import os
from asyncio import sleep
from multiprocessing import Process, Queue, Manager
from typing import Type, List, Dict
from websockets.legacy.server import WebSocketServerProtocol

from dispatcher.balancer import BaseBalancer, Client, CommandRequest, DummyBalancer, Status
from sim_runner.src.api.core import Command, Opcodes, ModeEnum
from sim_runner.src.api.packable_dataclass import BaseEvent
from sim_runner.src.api.websocket_connection.websocket_server import Server

manager = Manager()


class BaseDispatcher:
    host: str
    port: int
    balancer: BaseBalancer

    process: Process

    def __init__(self, host: str, port: int, bal: Type[BaseBalancer], *args, **kwargs):
        self.host = host
        self.port = port
        self.balancer = bal(*args, **kwargs)

    def start_server(self):
        pass


class DummyDispatcher:
    host: str
    port: int
    balancer: DummyBalancer
    cert: str
    key: str

    process: Process

    def __init__(self, host: str, port: int, cert: str, key: str, bal: Type[DummyBalancer], *args, **kwargs):
        self.host = host
        self.port = port
        self.cert = cert
        self.key = key
        self.balancer = bal()

    def start_server(self):
        def server_process(
                clients: Dict[str, Client], data: Queue[CommandRequest],
                responses: List[str]):
            async def echo(_: WebSocketServerProtocol, f: BaseEvent) -> None:
                print(f)

            async def join_cb(uuid: str, name: str):
                clients[uuid] = Client(
                    name=name,
                    uuid=uuid,
                    status=Status.ok
                )

            async def leave_cb(uuid: str, name: str):
                clients.pop(uuid)
                responses.clear()

            srv = Server(host=self.host,
                         port=self.port,
                         cert=self.cert,
                         key=self.key,
                         join_callback=join_cb,
                         leave_callback=leave_cb)

            async def consume_msgs():
                while True:
                    if not data.empty():
                        req = data.get()
                        print('got data', str(req))
                        if clients[req.client_uuid].status == Status.ok:
                            f = clients.pop(req.client_uuid)
                            f.status = Status.running
                            clients[req.client_uuid] = f
                            await srv.workers[req.client_uuid].connection.send(
                                json.dumps(Command(
                                    opcode=Opcodes.start_sim,
                                    kwargs={
                                        'mode': ModeEnum.SITL,
                                        'start_3d_sim': False
                                    }
                                ).pack())
                            )
                        await srv.workers[req.client_uuid].connection.send(
                            json.dumps(req.command.pack())
                        )
                    await sleep(0.1)

            async def get_responses():
                while True:
                    if srv.workers:
                        responses.append(str(next(iter((await srv.recv()).values()))))
                    await sleep(0.1)

            async def main():
                await asyncio.gather(
                    srv.run(),
                    consume_msgs(),
                    get_responses()
                )
            asyncio.run(main())

        self.balancer.initialize(
            manager.dict(),
            manager.Queue(),
            manager.list()
        )

        self.process = Process(
            target=server_process,
            args=(self.balancer.clients, self.balancer.data, self.balancer.responses)
        )
        self.process.start()

