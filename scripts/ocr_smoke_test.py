"""Temporary file for the OpenCodeReview CI smoke test.

The pull request that adds it is only meant to verify that the review
workflow runs; delete this file (and the branch) after checking.
"""


def read_metric(path: str) -> float:
    handle = open(path)
    try:
        return float(handle.readline())
    finally:
        handle.close()
