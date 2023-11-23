"""Created by agarc at 23/10/2023
Features:
"""
import fnmatch
import logging
import os

import yaml


def load_llm_settings() -> dict:
    # find the YAML file
    filename = "llm_settings.YAML"
    llm_settings_file = None
    for root, _, files in os.walk(os.path.abspath(os.path.dirname(__file__))):
        for file in fnmatch.filter(files, filename):
            llm_settings_file = os.path.join(root, file)

    """Load llm settings YAML file and push the data to environment variable."""
    if os.path.exists(llm_settings_file):
        with open(llm_settings_file, encoding="utf-8") as file:
            llm_settings = yaml.safe_load(file)
        # push all values in os.environ variables
        for key_1, dict_2 in llm_settings.items():
            for key_2, value in dict_2.items():
                environ_key = key_1 + "__" + key_2
                os.environ[environ_key] = value
        logging.info("llm settings.YAML loaded and pushed to os.environ variables.")
    else:
        log_string = f"{llm_settings_file} does not exist."
        logging.info(log_string)
        err = f"{llm_settings_file} does not exist."
        raise FileNotFoundError(err)

    return llm_settings
