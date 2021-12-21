#  Copyright (c) 2020 Russell Smiley
#
#  This file is part of build_harness.
#
#  You should have received a copy of the MIT License along with build_harness.
#  If not, see <https://opensource.org/licenses/MIT>.

"""Package version management."""

import pathlib

from ._default_values import DEFAULT_RELEASE_ID


def acquire_version() -> str:
    """
    Acquire PEP-440 compliant version from VERSION file.

    Returns:
        Acquired version text.
    Raises:
        RuntimeError: If version is not valid.
    """
    here = pathlib.Path(__file__).parent
    version_file_path = (here / "VERSION").absolute()

    if version_file_path.is_file():
        with version_file_path.open(mode="r") as version_file:
            version = version_file.read().strip()
    else:
        version = DEFAULT_RELEASE_ID

    if not version:
        raise RuntimeError("Unable to acquire version")

    return version


__version__ = acquire_version()
