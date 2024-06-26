import argparse
import asyncio
import base64
import pathlib
import signal
import sys
import tempfile
import json

import nats
import scenic
from nats.aio.client import Client

from typing import Optional


def show_usage():
    usage = """
    nats-pub [-s SERVER] <subject>

    Example:

    nats-pub -s demo.nats.io help -q workers
    """
    print(usage)


def show_usage_and_die():
    show_usage()
    sys.exit(1)


print("Starting NATS server")


async def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--servers", default="nats://127.0.0.1:4222")
    parser.add_argument("-q", "--queue", default="")
    parser.add_argument("--creds", default="")
    args = parser.parse_args()

    print(f"Running scenic NATS server { args.servers }")

    async def error_cb(e):
        print("Error: ", e)

    async def closed_cb():
        await asyncio.sleep(0.2)
        loop.stop()

    async def reconnected_cb():
        print("Reconnected to NATS")

    nc: Optional[Client] = None
    options = {
        "error_cb": error_cb,
        "closed_cb": closed_cb,
        "reconnected_cb": reconnected_cb,
    }
    try:
        if len(args.servers) > 0:
            options["servers"] = args.servers
        nc = await nats.connect(**options)
    except Exception as e:
        print(e)
        show_usage_and_die()
        return

    shape_map = {
        "SpheroidShape": "SphereGeometry",
        "BoxShape": "BoxGeometry",
        "ConeShape": "ConeGeometry",
        "CylinderShape": "CylinderGeometry",
    }

    async def string_message_handler(msg):
        """The scenic string handler processes scenic programs sent over the NATS bus as strings

        Args:
            msg (nats.Message): the NATS message receved for this handler
        """
        subject = msg.subject
        reply = msg.reply
        data = msg.data
        print(f"Received messaged on '{ subject } {reply}': {data}")

        scenario = scenic.scenarioFromString(base64.b64decode(data).decode("utf-8"))
        scene, _ = scenario.generate()
        for obj in scene.objects:
            # for now, one of box, cylinder, cone, spheroid
            shape = shape_map.get(type(obj.shape).__name__, "BoxGeometry")
            print("SHAPE", shape)
            if shape == "BoxGeometry":
                request = {
                    "type": shape,
                    # "orientation": [obj.yaw, obj.pitch, obj.roll],
                    # "position": obj.toVector().coordinates,
                    "height": 1,
                    "width": 1,
                    "depth": 1,
                }
            elif shape == "SphereGeometry":
                request = {
                    "type": shape,
                    # "orientation": [obj.yaw, obj.pitch, obj.roll],
                    # "position": obj.toVector().coordinates,
                    "radius": 2,
                }
            else:
                print("got ", shape)
                request = {}
            print(json.dumps(request))
            await nc.publish(
                "meshcat.geometries.bg", json.dumps(request).encode("utf-8")
            )
            await nc.flush()

    # async def file_message_handler(msg):
    #     subject = msg.subject
    #     reply = msg.reply
    #     data = msg.data.decode()
    #     print(f"Received messaged on '{ subject } {reply}': {data}")
    #
    #     scenario = scenic.scenarioFromFile(msg.data)
    #     with open(pathlib.Path(tempfile.gettempdir()) / "test_scene", "rb") as f:
    #         data = f.read()
    #     scenario = scenic.scenarioFromFile(data)
    #     print(f"Got scenario: { scenario }")
    #
    def signal_handler():
        if nc and nc.is_closed:
            return
        asyncio.create_task(nc.drain())

    for sig in ("SIGINT", "SIGTERM"):
        asyncio.get_running_loop().add_signal_handler(
            getattr(signal, sig), signal_handler
        )

    await nc.subscribe(
        "sunset.scenic.generate.string", "workers", string_message_handler
    )
    # await nc.subscribe("sunset.scenic.generate.file", "workers", file_message_handler)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    try:
        loop.run_forever()
    finally:
        loop.close()
