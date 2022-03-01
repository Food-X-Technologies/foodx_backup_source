#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

import logging
import pathlib
import tempfile
import typing
from urllib.parse import urlparse

import git

from ._hash import create_hash_file
from .schema import ApplicationDefinition

log = logging.getLogger(__name__)


def _construct_tarfile_path(
    name: str,
    git_ref: str,
    archive_path: pathlib.Path,
) -> pathlib.Path:
    file_path = archive_path / f"{name}-{git_ref}.tar.gz"

    return file_path


def _create_tarfile(
    name: str, git_ref: str, tarfile_path: pathlib.Path, this_repo: git.Repo
) -> None:
    with tarfile_path.open(mode="wb") as f:
        this_repo.archive(
            f,
            git_ref,
            format="tar.gz",
            prefix=f"{name}/",
        )

    create_hash_file(tarfile_path)


async def do_snapshot(
    definition: ApplicationDefinition,
    archive_directory: pathlib.Path,
    token: typing.Optional[str],
) -> pathlib.Path:
    """
    Take a snapshot of the specified git repository for backup purposes.

    Args:
        definition: application definitions
        archive_directory: directory to write tar and SHA sum files

    Returns:
        Path of tar file created
    """
    this_url = definition.configuration.backup.repo_url

    parsed_url = urlparse(this_url)
    authorized_url = (
        f"{parsed_url.scheme}://:{token}@{parsed_url.netloc}"
        f"{parsed_url.path}"
    )

    with tempfile.TemporaryDirectory() as d:
        working_directory = pathlib.Path(d)

        log.info(f"cloning repo, {this_url}")
        cloned_repo = git.Repo.clone_from(
            authorized_url,
            working_directory,
        )

        tarfile_path = _construct_tarfile_path(
            definition.name,
            definition.configuration.release.ref,
            archive_directory,
        )
        _create_tarfile(
            definition.name,
            definition.configuration.release.ref,
            tarfile_path,
            cloned_repo,
        )

        return tarfile_path
