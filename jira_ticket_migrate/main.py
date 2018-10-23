"""Contains the function for the program."""

from .runtime_args import parse_runtime_args


def main():
    """The main function."""
    # Get runtime args
    cli_artgs = parse_runtime_args()
