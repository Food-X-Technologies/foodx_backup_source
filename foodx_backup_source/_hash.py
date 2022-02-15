#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of backup_source.
#
#  You should have received a copy of the MIT License along with
#  backup_source. If not, see <https://opensource.org/licenses/MIT>.

"""Managing generation of hashes of archive files."""

import hashlib
import pathlib


def create_file_hash(file_path: pathlib.Path) -> str:
    """
    Create a hash of a file.

    Replicates function of ``sha365sum`` linux command.

    Args:
        file_path: Path of file to hash.

    Returns:
        Hex digest of file SHA.
    """
    this_hash = hashlib.sha256()
    file_size = file_path.stat().st_size
    with file_path.open(mode="rb") as f:
        while f.tell() != file_size:
            this_hash.update(f.read(0x40000))

    return this_hash.hexdigest()
