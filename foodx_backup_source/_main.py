#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

"""Primary execution path."""

import asyncio
import datetime
import io
import pathlib
import tarfile
import tempfile
import typing

import click

from ._file_io import (
    BackupDefinitions,
    PathSet,
    discover_backup_definitions,
    load_backup_definitions,
)
from ._hash import create_hash_file
from ._snapshot import do_snapshot

DEFAULT_OUTPUT_PATH = pathlib.Path(".")


def _strip_paths(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
    """Ensure source filesystem absolute paths are not reflected in tar file."""
    original_path = pathlib.Path(tarinfo.name)
    tarinfo.name = f"{original_path.name}"

    return tarinfo


def _isoformat_now() -> str:
    """Generate an iso format date for tar file naming."""
    return datetime.datetime.utcnow().isoformat()[:-3] + "Z"


async def _gather(
    project_name: str,
    project_directory: pathlib.Path,
    output_directory: pathlib.Path,
    token: typing.Optional[str],
) -> None:
    files: PathSet = discover_backup_definitions(project_directory)
    data: BackupDefinitions = await load_backup_definitions(files)

    with tempfile.TemporaryDirectory() as d:
        archive_directory = pathlib.Path(d)

        snapshot_packages = await asyncio.gather(
            *[do_snapshot(x, archive_directory, token) for x in data]
        )

        now = _isoformat_now()
        tar_path = output_directory / f"{project_name}-{now}.tar.gz"

        with tarfile.open(tar_path, mode="w:gz") as f:
            for package in snapshot_packages:
                f.add(str(package), filter=_strip_paths)
                f.add((str(package) + ".sha256"), filter=_strip_paths)

        create_hash_file(tar_path)


@click.command()
@click.argument("project_name", type=str)
@click.argument(
    "project_directory",
    type=click.Path(
        dir_okay=True, exists=True, file_okay=False, path_type=pathlib.Path
    ),
)
@click.option(
    "--output-dir",
    default=DEFAULT_OUTPUT_PATH,
    help="Directory path to save output tar file and SHA.",
    type=click.Path(
        dir_okay=True, exists=True, file_okay=False, path_type=pathlib.Path
    ),
)
@click.option(
    "--token-file",
    default=None,
    help="""Personal access token for authenticating against repositories.

A single token must have read access to all the repositories defined in the
backup.
""",
    type=click.File(mode="r"),
)
def main(
    project_name: str,
    project_directory: pathlib.Path,
    output_dir: pathlib.Path,
    token_file: typing.Optional[io.TextIOBase],
) -> None:
    """Primary entry point and execution path of backup utility."""
    try:
        token_value = None
        if token_file:
            token_value = token_file.read().strip()
        asyncio.run(
            _gather(project_name, project_directory, output_dir, token_value)
        )
    except KeyboardInterrupt:
        click.echo("User aborted execution. Exiting.")
