"""Created by agarc at 23/10/2023
Features:
"""
import logging
import os

import yaml


def load_llm_settings(llm_settings_file: str = "app/llm_settings.YAML") -> dict:
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
