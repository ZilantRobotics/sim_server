import asyncio
import json

from websockets.legacy.server import WebSocketServerProtocol

from sim_runner.src.api.core import Pose, Vector3, Transform, Command, Opcodes, AgentName
from sim_runner.src.api.packable_dataclass import BaseEvent
from sim_runner.src.api.websocket_connection.websocket_server import Server


async def echo(_: WebSocketServerProtocol, data: BaseEvent) -> None:
    print(data)

if __name__ == '__main__':
    a = Server(
        host='localhost',
        port=9990,
        cert='./ca/ca_cert.pem',
        key='./ca/ca.pem',
        recv_callback=echo
    )

    async def _srv():
        await a.run(blocking=False)

    p = Pose(
        velocity=Vector3(12, 3, 4),
        angular_velocity=Vector3(12, 3, 4),
        transform=Transform(
            position=Vector3(12, 3, 4),
            rotation=Vector3(12, 3, 4)
        )
    )

    cmd = Command(
        opcode=Opcodes.spawn_agent,
        args=[],
        kwargs={'agent_name': AgentName.octo_amazon, 'position': p}
    )

    async def _msg():
        while True:
            await asyncio.sleep(5)
            for worker in a.workers.values():
                await worker.connection.send(
                    json.dumps(cmd.pack())
                )

    async def main():
        await asyncio.gather(
            _srv(),
            _msg()
        )

    asyncio.run(main())