import logging

import yaml
from yaml import Loader

import definitions
import knowledge_building, oa_data_harvesting, retrieval, resources


def get_logger(module) -> logging.Logger:
    custom = "%(asctime)-15s %(module)-8s %(message)s"
    logging.basicConfig(format=custom, level=logging.INFO)
    log = logging.getLogger(module)
    return log


def get_config(config_file=f"{definitions.CONFIG_PATH}") -> dict:
    conf = yaml.load(open(config_file), Loader=Loader)
    return conf


logger = get_logger(__name__)
config = get_config()

__version__ = "v1.1.0"
__all__= ["knowledge_building", "oa_data_harvesting", "retrieval", "definitions", "config", "logger", "resources", "get_logger"]


def initialize():
    logger.info(f"Starting {__name__} version {__version__}")
    logger.info(f"config : {config}")


# @todo move towards the .cfg file


initialize()