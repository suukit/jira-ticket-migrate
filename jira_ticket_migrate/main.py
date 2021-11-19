"""Contains the function for the program."""

import sys
from colorama import init, Style
from jira import JIRA as Jira
from jira.exceptions import JIRAError as JiraError
from tqdm import tqdm
import yaml
from .jira import get_project_tickets, push_ticket
from .runtime_args import parse_runtime_args
from typing import List

def map_component(components: List[str]):
    """map ticket's components, transfer 1:1 if no mapping is given"""


def main():
    """The main function."""
    # Get runtime args
    cli_args = parse_runtime_args()

    # Parse config file
    # with open(cli_args.config, "r") as config_file:
    with open("config-MULTICLOUD.yaml", "r") as config_file:
        config_dict = yaml.safe_load(config_file)

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

    source_query=""
    if "source_query" in config_dict.keys():
        source_query=config_dict["source_query"]

    # Migrate

    print(Style.BRIGHT + "Migrating {}".format(config_dict["source-jira"]["project"]) + Style.RESET_ALL)

    # Get tickets
    try:
        tickets = get_project_tickets(source_jira, config_dict["source-jira"]["project"], False, True, source_query)
    except JiraError as e:
        print(
            Style.BRIGHT
            + "Jira call failed! Here's the error:"
            + Style.RESET_ALL
        )
        print(e)
        sys.exit(1)

    # Push tickets
    print(
        Style.BRIGHT + "Pushing tickets to destination" + Style.RESET_ALL
    )

    for ticket in tqdm(tickets):
        # map components
        if "component-mapping" in config_dict.keys():
            trans_comp = []
            for comp in ticket.components:
                if comp in config_dict["component-mapping"].keys():
                    trans_comp.append({"name":config_dict["component-mapping"][comp]})
            ticket.components = trans_comp

        if ticket.components == []:
            ticket.components.append({"name":"CIEA"})

        # map status
        if "status-mapping" in config_dict.keys():
            ticket.status = config_dict["status-mapping"][ticket.status]

        # add labels
        if "add-labels" in config_dict.keys():
            ticket.labels.extend(config_dict["add-labels"])

        # remove labels
        if "del-labels" in config_dict.keys():
            ticket.labels = [label for label in ticket.labels if label not in config_dict["del-labels"]]

        try:
            new_ticket = push_ticket(destination_jira, ticket, config_dict["destination-jira"]["project"])
        except JiraError as e:
            print(
                Style.BRIGHT
                + "Jira call failed! Here's the error:"
                + Style.RESET_ALL
            )
            print(e)
            sys.exit(1)

        try:
            destination_jira.add_simple_link(new_ticket.id,
            {"url":ticket.source_link,
            "title":"Original Ticket %s" % ticket.ticket_key})
        except JiraError as e:
            print(
                Style.BRIGHT
                + "Jira call failed! Here's the error:"
                + Style.RESET_ALL
            )
            print(e)
            sys.exit(1)

