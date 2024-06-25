import argparse
import asyncio
import base64
import pathlib
import signal
import sys
import tempfile

import nats
import scenic


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

    async def string_message_handler(msg):
        """The scenic string handler processes scenic programs sent over the NATS bus as strings

        Args:
            msg (nats.Message): the NATS message receved for this handler
        """
        subject = msg.subject
        reply = msg.reply
        data = msg.data
        # print(f"Received messaged on '{ subject } {reply}': {decoded_data}")
        print(str(data))
        scenario = scenic.scenarioFromString(base64.b64decode(data).decode("utf-8"))
        scene, _ = scenario.generate()
        for obj in scene.objects[:1]:
            # for each of the objects, get its shape, and post a request to the object tree
            # use the
            for attr in dir(obj):
                print(attr)

    async def file_message_handler(msg):
        subject = msg.subject
        reply = msg.reply
        data = msg.data.decode()
        print(f"Received messaged on '{ subject } {reply}': {data}")

        scenario = scenic.scenarioFromFile(msg.data)
        with open(pathlib.Path(tempfile.gettempdir()) / "test_scene", "rb") as f:
            data = f.read()
        scenario = scenic.scenarioFromFile(data)
        print(f"Got scenario: { scenario }")

    options = {
        "error_cb": error_cb,
        "closed_cb": closed_cb,
        "reconnected_cb": reconnected_cb,
    }

    nc = None
    try:
        if len(args.servers) > 0:
            options["servers"] = args.servers
        nc = await nats.connect(**options)
    except Exception as e:
        print(e)
        show_usage_and_die()
        return

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
    await nc.subscribe("sunset.scenic.generate.file", "workers", file_message_handler)


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
    try:
        loop.run_forever()
    finally:
        loop.close()
