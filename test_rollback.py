from service.sync import emergency_reorg
from tortoise import Tortoise
import asyncio
import config


async def main():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    await emergency_reorg(3438263)


if __name__ == "__main__":
    asyncio.run(main())
