# Used to generate JSON Validations chema for requirements.
import re
import sys
from typing import Any, List, Mapping, Optional, Union

from pydantic import BaseModel, ConstrainedStr, Extra, Field

from . import consts

if sys.version_info >= (3, 8):
    from typing import Literal  # pylint: disable=no-name-in-module
else:
    from typing_extensions import Literal


class MoleculeDependencyModel(BaseModel):
    # https://github.com/ansible-community/toolset/blob/main/requirements.in
    name: Literal[
        "galaxy",
        "shell",
    ]
    command: Optional[str]
    options: Optional[Mapping[str, Any]]
    env: Optional[Mapping[str, Any]]
    enabled: Optional[bool] = Field(default=True)

    class Config:
        extra = Extra.forbid


class MoleculeDriverOptionsModel(BaseModel):
    managed: Optional[bool]
    login_cmd_template: Optional[str]
    ansible_connection_options: Optional[Mapping[str, str]]

    class Config:
        extra = Extra.forbid


class MoleculeDriverModel(BaseModel):
    # https://github.com/ansible-community/toolset/blob/main/requirements.in
    name: Optional[
        Literal[
            "azure",
            "ec2",
            "delegated",
            "docker",
            "containers",
            "openstack",
            "podman",
            "vagrant",
            "digitalocean",
            "gce",
            "libvirt",
            "lxd",
        ]
    ]
    options: Optional[MoleculeDriverOptionsModel]
    # vagrant
    provider: Optional[Mapping[str, Any]]

    class Config:
        extra = Extra.forbid


class ContainerRegistryModel(BaseModel):
    url: str

    class Config:
        extra = Extra.forbid


class NetworkModeServiceString(ConstrainedStr):
    regex = re.compile(r'^service:[a-zA-Z0-9:_.\\-]+$')


class NetworkModeContainerString(ConstrainedStr):
    regex = re.compile(r'^container:[a-zA-Z0-9][a-zA-Z0-9_.-]+$')


class MoleculePlatformModel(BaseModel):
    name: str
    hostname: Optional[str]
    environment: Optional[Mapping[str, str]]
    groups: Optional[List[str]]
    # container specific
    image: Optional[str]
    pre_build_image: Optional[bool]
    registry: Optional[ContainerRegistryModel]
    dockerfile: Optional[str]
    volumes: Optional[List[str]]
    tmpfs: Optional[List[str]]
    command: Optional[str]
    network_mode: Union[
        Optional[
            Literal[
                "bridge",
                "host",
                "none",
            ]
        ],
        NetworkModeServiceString,
        NetworkModeContainerString,
    ]
    privileged: Optional[bool]
    ulimits: Optional[List[str]]
    # other
    pkg_extras: Optional[str]
    box: Optional[str]
    memory: Optional[int]
    cpus: Optional[int]
    provider_raw_config_args: Optional[List[str]]

    class Config:
        extra = Extra.forbid


class ProvisionerConfigOptionsModel(BaseModel):
    class ProvisionerConfigOptionsDefaultsModel(BaseModel):
        ansible_managed: Optional[str] = Field(
            default="Ansible managed: Do NOT edit this file manually!"
        )
        display_failed_stderr: Optional[bool] = Field(default=True)
        fact_caching: Optional[str]
        fact_caching_connection: Optional[str]
        forks: Optional[int] = Field(default=50)
        host_key_checking: Optional[bool] = Field(default=False)
        interpreter_python: Optional[str] = Field(
            default="auto_silent",
            description="See https://docs.ansible.com/ansible/devel/reference_appendices/interpreter_discovery.html",
        )
        nocows: Optional[int] = Field(default=1)
        retry_files_enabled: Optional[bool] = Field(default=False)

        class Config:
            extra = Extra.forbid

    class ProvisionerConfigOptionsSshConnectionModel(BaseModel):
        control_path: Optional[str] = Field(default="%(directory)s/%%h-%%p-%%r")
        scp_if_ssh: Optional[bool] = Field(default=True)

        class Config:
            extra = Extra.forbid

    defaults: Optional[ProvisionerConfigOptionsDefaultsModel]
    ssh_connection: Optional[ProvisionerConfigOptionsSshConnectionModel]

    class Config:
        extra = Extra.forbid


class ProvisionerModel(BaseModel):
    name: Optional[Literal["ansible"]]
    log: Optional[bool]
    env: Optional[Mapping[str, Any]]
    playbooks: Optional[Mapping[str, Any]]
    inventory: Optional[Mapping[str, Any]]
    config_options: Optional[ProvisionerConfigOptionsModel]

    class Config:
        extra = Extra.forbid


class VerifierModel(BaseModel):
    # https://github.com/ansible-community/toolset/blob/main/requirements.in
    name: Optional[Literal["ansible", "goss", "inspec", "testinfra"]] = Field(
        default="ansible"
    )

    class Config:
        extra = Extra.forbid


class MoleculeScenarioModel(BaseModel):
    log: Optional[bool] = Field(default=True)
    dependency: Optional[MoleculeDependencyModel]
    driver: MoleculeDriverModel
    lint: Optional[str]
    platforms: List[MoleculePlatformModel]
    provisioner: Optional[ProvisionerModel]
    scenario: Mapping[
        Literal[
            "check_sequence",
            "cleanup_sequence",
            "converge_sequence",
            "create_sequence",
            "dependency_sequence",
            "destroy_sequence",
            "idempotence_sequence",
            "lint_sequence",
            "prepare_sequence",
            "side_effect_sequence",
            "syntax_sequence",
            "test_sequence",
            "verify_sequence",
        ],
        List[
            Literal[
                "check",
                "cleanup",
                "converge",
                "create",
                "dependency",
                "destroy",
                "idempotence",
                "lint",
                "prepare",
                "side_effect",
                "syntax",
                "test",
                "verify",
            ]
        ],
    ]
    verifier: Optional[VerifierModel]

    class Config:
        extra = Extra.forbid
        title = "Molecule Scenario Schema"
        schema_extra = {
            "$schema": consts.META_SCHEMA_URI,
            "examples": ["molecule/*/molecule.yml"],
        }
