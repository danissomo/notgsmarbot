from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin
from yamldataclassconfig.config import YamlDataClassConfig
import os
import yaml
import argparse
from pkg_resources import Distribution, resource_filename, get_distribution
from email.parser import Parser
from notgsmarbot.logs import LOGGER
from typing import Optional


@dataclass
class Viewport(DataClassJsonMixin):
    width: int
    height: int
    deviceScaleFactor: float


@dataclass
class TGConfig(DataClassJsonMixin):
    token: str
    god_chat_id: str


@dataclass
class BrowserConfig(DataClassJsonMixin):
    args: list[str] = field(default_factory=lambda: list())
    viewport: Viewport = field(
        default_factory=lambda: Viewport(
            width=400, height=520, deviceScaleFactor=2),
        metadata={"dataclasses_json": {"mm_field": Viewport}}
    )
    execurable: Optional[str] = None


@dataclass
class Config(YamlDataClassConfig):
    tg: TGConfig = field(
        default=None, metadata={"dataclasses_json": {"mm_field": TGConfig}}
    )
    browser: BrowserConfig = field(
        default=None, metadata={"dataclasses_json": {"mm_field": BrowserConfig}}
    )


CONFIG = Config()


def parse_pkg_meta(pkg_name: str) -> dict:
    distribution: Distribution = get_distribution(pkg_name)
    metadata = distribution.get_metadata("METADATA")
    metadata_dict = Parser().parsestr(metadata)
    return metadata_dict


def parse_args():
    metadata_dict = parse_pkg_meta("notgsmarbot")
    ap = argparse.ArgumentParser(
        prog=metadata_dict["Name"],
        description=metadata_dict["Summary"],
        epilog=f"github: {metadata_dict['Home-page']
                          }, ver: {metadata_dict['Version']}",
    )
    ap.add_argument("-t", "--token", help="Your telegram token", default=None)
    ap.add_argument("--width", type=int,
                    help="width of viewport", default=None)
    ap.add_argument("--height", type=int,
                    help="height of viewpor", default=None)
    ap.add_argument("--scale", type=float,
                    help="scale of viewpor", default=None)
    ap.add_argument("-d", "--dryrun", action="store_true",
                    help="Do not update config")
    return ap.parse_args()


def merge_args2cfg(args):
    if args.token:
        CONFIG.tg.token = args.token
    if args.width:
        CONFIG.browser.viewport.width = args.width
    if args.height:
        CONFIG.browser.viewport.height = args.height
    if args.scale:
        CONFIG.browser.viewport.deviceScaleFactor = args.scale


def load_config():
    cliargs = parse_args()
    config_path = resource_filename("notgsmarbot", "files/config.yaml")
    if not os.path.exists(config_path):
        cfg = CONFIG.to_dict()
        cfg.pop("FILE_PATH")
        LOGGER.critical('Create config.yaml:\n' + yaml.dump(cfg))
        exit()
    CONFIG.load(config_path)
    merge_args2cfg(cliargs)
    if not cliargs.dryrun:
        LOGGER.debug("not dry-run")
        save_config()
    if os.name == "nt":
        CONFIG.browser.execurable = (
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
        )
        if not os.path.exists(CONFIG.browser.execurable):
            CONFIG.browser.execurable = (
                "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe"
            )
        if not os.path.exists(CONFIG.browser.execurable):
            LOGGER.critical(f"Why you don't have MS Edge on windows?🥴")
            exit(1)
    else:
        if os.name != "posix":
            LOGGER.warn(f"UNKNOW OS TYPE {os.name}, app may not work properly")
        # lib will install its own
        CONFIG.browser.execurable = None
    cfg = CONFIG.to_dict()
    cfg.pop("FILE_PATH")
    LOGGER.debug("Config:\n" + yaml.dump(cfg))


def save_config():
    config_path = resource_filename("notgsmarbot", "files/config.yaml")
    with open(config_path, "w") as file:
        cfg = CONFIG.to_dict()
        cfg.pop("FILE_PATH")
        yaml.dump(cfg, file)


if __name__ == "__main__":
    load_config()
    LOGGER.info('Config:\n' + yaml.dump(CONFIG.to_dict()))
