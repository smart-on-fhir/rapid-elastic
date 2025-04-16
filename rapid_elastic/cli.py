import argparse
import asyncio
import sys
from typing import NoReturn

import rich.console

from rapid_elastic import config, filetool, pipeline


def fatal_error(message: str) -> NoReturn:
    stderr = rich.console.Console(stderr=True)
    stderr.print(message, style="bold red", highlight=False)
    sys.exit(1)  # raises a SystemExit exception


async def main(argv: list[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--diseases",
        metavar="FILE",
        help="disease config (default is the RAPID collection of rare diseases)",
        default=filetool.resource("disease_names_expanded.json"),
    )
    parser.add_argument(
        "--output", "-o",
        metavar="DIR",
        help="output folder (default is ./output/)",
        default="output",
    )
    parser.add_argument("--fields", metavar="FILE", help="elasticsearch field config")
    args = parser.parse_args(argv)

    if not config.ELASTIC_USER or not config.ELASTIC_PASS:
        fatal_error("You must first set the ELASTIC_USER and ELASTIC_PASS environment variables.")

    pipeline.pipe_file(args.diseases, output_base=args.output, fields_config=args.fields)


def main_cli():
    asyncio.run(main(sys.argv[1:]))  # pragma: no cover


if __name__ == "__main__":
    main_cli()  # pragma: no cover
