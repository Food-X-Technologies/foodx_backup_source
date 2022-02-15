#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of backup_source.
#
#  You should have received a copy of the MIT License along with
#  backup_source. If not, see <https://opensource.org/licenses/MIT>.

import pathlib
import tempfile

import git

from ._hash import create_file_hash
from .schema import ApplicationDefinition


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
            prefix=f"{name}",
        )

    hash_hexdigest = create_file_hash(tarfile_path)
    hash_file = tarfile_path.parent / f"{tarfile_path.name}.sha256"
    with hash_file.open("w") as h:
        h.write(f"{hash_hexdigest}  {tarfile_path.name}")


async def do_snapshot(
    definition: ApplicationDefinition, archive_directory: pathlib.Path
) -> pathlib.Path:
    """
    Take a snapshot of the specified git repository for backup purposes.

    Args:
        definition: application definitions
        archive_directory: directory to write tar and SHA sum files

    Returns:
        Path of tar file created
    """
    with tempfile.TemporaryDirectory() as d:
        working_directory = pathlib.Path(d)

        cloned_repo = git.Repo.clone_from(
            definition.configuration.backup.repo_url,
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
