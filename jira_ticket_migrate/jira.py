"""Contains Jira related functionality."""

from typing import List
from jira import JIRA as Jira
from jira import resources as JiraResources


class JiraTicket:
    """Representation of a Jira project.

    Attributes:
        description (str): The description of the ticket.
        priority (str): The priority of the ticket. For example, "Medium".
        project (str): The name of the project.
        resolution (str): A string, or None, containing the resolution
            of the ticket (should there be one).
        source_link (str): The URL of the ticket on the source Jira
            server.
        summary (str): The summary of the ticket.
        labels (List[str]): List of labels
        components (List[str]): List of components
        status (str): ticket's status as name
        issuetype (str): issue type as name
        ticket_key (str): tickets key
    """

    def __init__(
        self,
        description: str,
        priority: str,
        project: str,
        resolution: str,
        source_link: str,
        summary: str,
        labels: List[str],
        components: List[str],
        status: str,
        issuetype: str,
        ticket_key: str
    ):
        """Initialize a Jira ticket.

        Args:
            description: The description of the ticket.
            priority: The priority of the ticket. For example, "Medium".
            project: The name of the project.
            resolution: A string, or None, containing the resolution of
                the ticket (should there be one).
            source_link: The URL of the ticket on the source Jira
                server.
            summary: The summary of the ticket.
        """
        self.description = description
        self.priority = priority
        self.project = project
        self.resolution = resolution
        self.source_link = source_link
        self.summary = summary
        self.labels = labels
        self.components = components
        self.status = status
        self.issuetype = issuetype
        self.ticket_key = ticket_key

def create_blank_ticket(project: str) -> JiraTicket:
    """Create a representation of a blank Jira ticket.

    It's not actually blank, but the point it that is contains nothing
    useful.

    Args:
        project: The name of the project.

    Returns:
        A "blank" JiraTicket.
    """
    return JiraTicket(
        description="",
        priority="Medium",
        project=project,
        resolution="Done",
        source_link="null",
        summary="Blank ticket",
        labels=[],
        components=[],
        status="Open",
        issuetype="Story",
        key="TEST-1"
    )


def translate_priority(priority: str) -> str:
    """Translate to new Jira priority types.

    Jira changed how their priority names, so some translation is
    necessary if migrating from an older Jira.

    Args:
        priority: A ticket priority.

    Returns:
        A valid Jira priority.
    """
    if priority in ("Blocker", "Critical"):
        return "Very High"
    elif priority == "High":
        return "High"
    elif priority == "Medium":
        return "Medium"
    elif priority == "Low":
        return "Low"

    return priority

def translate_issuetype(issuetype: str) -> str:
    """Translate issuetype

    Args:
       issuetype: A source issuetype

    Returns:
       a valid target issuetype
    """
    if issuetype in ("Defect", "Epic"):
        return issuetype
    else:
        return "Story"

def get_project_tickets(
    jira: Jira,
    project: str,
    insert_blank_tickets: bool = True,
    verbose: bool = True,
    source_query: str = "",
) -> List[JiraTicket]:
    """Get all tickets from a project in ascending order.

    This will fill in missing tickets with blank tickets if
    insert_blank_tickets is set to True.

    Args:
        jira: The Jira server to get tickets from.
        project: The project name.
        insert_blank_tickets (optional): If an intermediate ticket is
            not defined, fill in a blank ticket in its place. For
            example, if the project name is PROJ and PROJ-1 and PROJ-3
            exist on the Jira but not PROJ-2, this will fill a blank
            ticket for PROJ-2.  Defaults to True.
        verbose (optional): Whether to log the tickets being processed.
            Defaults to True.

    Returns:
        A list of JiraTickets from ticket number 1 to ticket N, where N
        is the last ticket number.
    """
    # Offsets for the API
    init = 0
    size = 100

    # Store all the API tickets to sort through later. Keys for this are
    # ticket number. Values are the ticket object we get from the Jira
    # SDK/API library.
    api_tickets_dict = {}

    # Fetch from the API until there's no tickets left
    while True:
        start = init * size

        api_tickets = jira.search_issues("project = %s and (%s)" % (project, source_query), start, size)

        # Check if we've reached the end
        if not api_tickets:
            break

        # Add the tickets
        for ticket in api_tickets:
            ticket_num = int(ticket.key.split("-")[-1])
            api_tickets_dict[ticket_num] = ticket

        # Move to next API page for next round
        init += 1

    # Keep track of what the ticket number "should" be if we're
    # inserting blank tickets
    ticket_counter = 1

    # Store JiraTicket objects for our tickets in here
    tickets = []

    # Create JiraTicket objects from the tickets collected above
    for ticket_num, ticket in sorted(api_tickets_dict.items()):
        if verbose:
            print("...loading %s" % ticket.key)

        # Insert blank tickets as necessary
        while insert_blank_tickets and ticket_counter < ticket_num:
            tickets.append(create_blank_ticket(project))

            ticket_counter += 1

        ticket_counter += 1

        # Insert *this* ticket. First deal with attributes that we
        # have to be careful with Nones with. Then make the ticket.
        description = ticket.fields.description

        if description is None:
            description = ""

        resolution = ticket.fields.resolution

        if resolution is not None:
            resolution = resolution.name

        components = []
        for comp in ticket.fields.components:
            components.append(comp.name)

        tickets.append(
            JiraTicket(
                description=description,
                priority=translate_priority(ticket.fields.priority.name),
                project=project,
                resolution=resolution,
                source_link=ticket.permalink(),
                summary=ticket.fields.summary,
                labels=ticket.fields.labels,
                components=components,
                status=ticket.fields.status.name,
                issuetype=translate_issuetype(ticket.fields.issuetype.name),
                ticket_key=ticket.key
            )
        )

    return tickets

def update_source_description(jira: Jira, ticket: JiraTicket, new_ticket: JiraResources.Issue):
    """Add a link to new ticket into source ticket's description.

    Args:
        jira: The original ticket's jira source object.
        ticket: the JiraTicket object for the source object
        new_ticket. jira issue object of new ticket.

    Returns:
        The modified description for the ticket.
    """
    link_message = "<*This ticket has been migrated to %s, please update your watches*>" % new_ticket.permalink()

    issue = jira.issue(ticket.ticket_key)
    issue.update(description=link_message + "\r\n\r\n" + ticket.description)

def add_source_link_to_description(description: str, link: str) -> str:
    """Add the source ticket URL to the description.

    Args:
        description: The original ticket's description.
        link: The URL to the source ticket.

    Returns:
        The modified description for the ticket.
    """
    link_message = "<This ticket was migrated from %s>" % link

    if description:
        link_message += "\r\n\r\n"

    return link_message + description


def push_ticket(jira: Jira, ticket: JiraTicket, dst_project: str):
    """Push a JiraTicket to a Jira server.

    Args:
        jira: The Jira server to get tickets from.
        ticket: The ticket to push to the Jira server.
    """
    # Create the ticket
    ticket_fields = {
        "description": add_source_link_to_description(
            ticket.description, ticket.source_link
        ),
        "issuetype": {"name": ticket.issuetype},
        "priority": {"name": ticket.priority},
        "project": {"id": jira.project(dst_project).id},
        "summary": ticket.summary,
        "components": ticket.components,
        "labels": ticket.labels
    }

    new_ticket = jira.create_issue(fields=ticket_fields)

    # Transition the ticket
    if ticket.resolution is not None or ticket.status != "Open":
        # List available transitions and search for the one we want (if
        # it exists)
        transitions = jira.transitions(new_ticket)

        id_ = None

        for transition in transitions:
            if transition["name"] == ticket.status:
                # Found it
                id_ = transition["id"]
                break

        # Transition not available. That's okay.
        if id_ is not None:
            jira.transition_issue(new_ticket, id_)

    return new_ticket
