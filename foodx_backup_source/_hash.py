#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

"""Managing generation of hashes of archive files."""

import hashlib
import logging
import pathlib

log = logging.getLogger(__name__)


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


def create_hash_file(reference_file_path: pathlib.Path) -> pathlib.Path:
    """
    Record file hash in a file.

    Args:
        hash_hexdigest: Hash to be recorded.
        reference_file_path: Path to file that was hashed.
    """
    # co-locate the hash file with the reference file.
    hash_hexdigest = create_file_hash(reference_file_path)
    hash_file = (
        reference_file_path.parent / f"{reference_file_path.name}.sha256"
    )

    hash_file_content = f"{hash_hexdigest}  {reference_file_path.name}"
    log.info(f"creating hash file, {hash_file} ({hash_file_content} )")
    with hash_file.open("w") as h:
        h.write(hash_file_content)

    return hash_file
