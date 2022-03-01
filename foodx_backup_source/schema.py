#  Copyright (c) 2022 Food-X Technologies
#
#  This file is part of foodx_backup_source.
#
#  You should have received a copy of the MIT License along with
#  foodx_backup_source. If not, see <https://opensource.org/licenses/MIT>.

"""Application backup dependency definitions."""

import typing

import pydantic


class RepoBackupDefinition(pydantic.BaseModel):
    """Git repository definitions."""

    repo_url: pydantic.HttpUrl
    branch_name: str


class DockerImageDefinition(pydantic.BaseModel):
    """Docker image definitions."""

    image_name: str
    tag_prefix: str


class ReleaseReference(pydantic.BaseModel):
    """Define git reference to be used for repository backup."""

    ref: str


class ApplicationDependency(pydantic.BaseModel):
    """Definition of git, docker dependencies of an application."""

    backup: RepoBackupDefinition
    docker: DockerImageDefinition
    release: ReleaseReference


ApplicationDependencies = typing.Dict[str, ApplicationDependency]


class ContextDeclaration(pydantic.BaseModel):
    """Application dependency declarations within template context."""

    dependencies: ApplicationDependencies


class DependencyFile(pydantic.BaseModel):
    """Template context declaration."""

    context: ContextDeclaration


class ApplicationDefinition(pydantic.BaseModel):
    """Application backup definition."""

    name: str
    configuration: ApplicationDependency
