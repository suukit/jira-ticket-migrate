"""Contains the function for the program."""

from colorama import init, Style
from jira import JIRA as Jira
from tqdm import tqdm
import yaml
from .jira import get_project_tickets, push_ticket
from .runtime_args import parse_runtime_args


def main():
    """The main function."""
    # Get runtime args
    cli_args = parse_runtime_args()

    # Parse config file
    with open(cli_args.config, "r") as config_file:
        config_dict = yaml.load(config_file)

    # Initialize Colorama
    init()

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

    # Migrate
    for project in config_dict["projects-to-migrate"]:
        print(Style.BRIGHT + "Migrating {}".format(project) + Style.RESET_ALL)

        # Get tickets
        tickets = get_project_tickets(source_jira, project)

        # Push tickets
        print(
            Style.BRIGHT + "Pushing tickets to destination" + Style.RESET_ALL
        )

        for ticket in tqdm(tickets):
            push_ticket(destination_jira, ticket)
