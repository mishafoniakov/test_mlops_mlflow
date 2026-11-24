"""Temporary file used to smoke-test the OpenCodeReview CI workflow."""

import json


def load_engine_config(path: str) -> dict:
    handle = open(path)
    config = json.load(handle)
    return config["engine"]
