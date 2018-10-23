"""Contains the function for the program."""

from jira import JIRA as Jira
import yaml
from .runtime_args import parse_runtime_args


def main():
    """The main function."""
    # Get runtime args
    cli_args = parse_runtime_args()

    # Parse config file
    with open(cli_args.config, "r") as config_file:
        config_dict = yaml.load(config_file)

    # Create Jira client objects for source and destination servers
    source_jira = Jira(
        server=config_dict["source-jira"]["url"],
        basic_auth=(
            config_dict["source-jira"]["auth"]["username"],
            config_dict["source-jira"]["auth"]["password"],
        ),
    )

    destination_jira = Jira(
        server=config_dict["destination-jira"]["url"],
        basic_auth=(
            config_dict["destination-jira"]["auth"]["username"],
            config_dict["destination-jira"]["auth"]["password"],
        ),
    )
