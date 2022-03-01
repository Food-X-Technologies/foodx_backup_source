#  Copyright (c) 1700-2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

"""A backup utility for FoodX source code."""

# make the main executable path available as an importable function.
from ._main import main as backup_source  # noqa: F401
from ._version import __version__  # noqa: F401
