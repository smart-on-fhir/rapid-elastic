import argparse
import asyncio
import sys
from typing import NoReturn

import rich.console

from rapid_elastic import config, pipeline


def fatal_error(message: str) -> NoReturn:
    stderr = rich.console.Console(stderr=True)
    stderr.print(message, style="bold red", highlight=False)
    sys.exit(1)  # raises a SystemExit exception


async def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config", metavar="diseases.json")
    parser.add_argument(
        "--output", "-o",
        metavar="DIR",
        help="output folder (default is ./output/)",
        default="output",
    )
    parser.add_argument("--field-config", metavar="FILE", help="elasticsearch field config")
    args = parser.parse_args(argv)

    if not config.ELASTIC_USER or not config.ELASTIC_PASS:
        fatal_error("You must first set the ELASTIC_USER and ELASTIC_PASS environment variables.")

    pipeline.pipe_file(args.config, output_base=args.output, fields_config=args.field_config)


def main_cli():
    asyncio.run(main(sys.argv[1:]))  # pragma: no cover


if __name__ == "__main__":
    main_cli()  # pragma: no cover
