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
import logging
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

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DEFAULT_OUTPUT_PATH = pathlib.Path(".")

GitReferences = typing.Dict[str, str]


def _strip_paths(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
    """Ensure source filesystem absolute paths are not reflected in tar file."""
    original_path = pathlib.Path(tarinfo.name)
    tarinfo.name = f"{original_path.name}"

    return tarinfo


def _isoformat_now() -> str:
    """Generate an iso format date for tar file naming."""
    return datetime.datetime.utcnow().isoformat()[:-3] + "Z"


def _apply_user_refs(
    data: BackupDefinitions, git_refs: GitReferences
) -> BackupDefinitions:
    if git_refs:
        names = git_refs.keys()
        for x in data:
            if x.name in names:
                log.info(
                    f"applying user git reference, {x.name}, {git_refs[x.name]}"
                )
                x.configuration.release.ref = git_refs[x.name]

    return data


async def _launch_packaging(
    project_name: str,
    project_directory: pathlib.Path,
    output_directory: pathlib.Path,
    token: typing.Optional[str],
    git_refs: GitReferences,
) -> typing.List[pathlib.Path]:
    files: PathSet = discover_backup_definitions(project_directory)
    data: BackupDefinitions = await load_backup_definitions(files)

    data = _apply_user_refs(data, git_refs)

    with tempfile.TemporaryDirectory() as d:
        archive_directory = pathlib.Path(d)

        snapshot_packages = await asyncio.gather(
            *[do_snapshot(x, archive_directory, token) for x in data]
        )

        now = _isoformat_now()
        tar_path = output_directory / f"{project_name}-{now}.tar.gz"

        log.info(f"saving tar file package, {tar_path}")
        with tarfile.open(tar_path, mode="w:gz") as f:
            for package in snapshot_packages:
                f.add(str(package), filter=_strip_paths)
                f.add((str(package) + ".sha256"), filter=_strip_paths)

        hash_path = create_hash_file(tar_path)

        return [tar_path, hash_path]


def _process_gitref_options(
    git_ref: typing.Optional[typing.List[str]],
) -> GitReferences:
    processed_refs: GitReferences = dict()
    if git_ref:
        for x in git_ref:
            tokens = x.split("=")
            if len(tokens) != 2:
                raise RuntimeError(f"Malformed git ref option, {x}")

            processed_refs[tokens[0].strip()] = tokens[1].strip()

    return processed_refs


def main(
    project_name: str,
    project_directory: pathlib.Path,
    output_dir: pathlib.Path,
    git_ref: typing.Optional[typing.List[str]],
    token_value: typing.Optional[str],
) -> typing.List[pathlib.Path]:
    """
    Package repositories for archiving.

    Args:
        project_name: Name of project to use as file name prefix.
        project_directory: Directory
        output_dir: Directory to output package files.
        git_ref: User overrides of application git references.
        token_value:

    Returns:
        List of files created.
    """
    processed_refs = _process_gitref_options(git_ref)
    created_files = asyncio.run(
        _launch_packaging(
            project_name,
            project_directory,
            output_dir,
            token_value,
            processed_refs,
        )
    )

    return created_files


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
    "--git-ref",
    default=None,
    help="""Specify a git reference for the named repo.

The reference is specified in the form `<name>=<gitref>` where the name is
an entry in the dependencies YAML files acquired from PROJECT_DIRECTORY.
""",
    multiple=True,
    type=str,
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
def click_entry(
    project_name: str,
    project_directory: pathlib.Path,
    output_dir: pathlib.Path,
    git_ref: typing.Optional[typing.List[str]],
    token_file: typing.Optional[io.TextIOBase],
) -> None:
    """
    Package repositories for archiving.

    Repositories specified in YAML "dependencies" files are packaged into a
    gzipped tar file at the specified git commit reference and then the
    collection of tar files is packaged into a single gzipped tar file for
    archiving. A sha256sum file for each tar package is also generated.
    """
    try:
        token_value = None
        if token_file:
            token_value = token_file.read().strip()

        main(project_name, project_directory, output_dir, git_ref, token_value)
    except KeyboardInterrupt:
        click.echo("User aborted execution. Exiting.")
