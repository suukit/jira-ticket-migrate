"""Contains Jira related functionality."""

from jira import JIRA as Jira


class JiraProject:
    """Representation of a Jira project.

    Attributes:
    """

    def __init__(self):
        pass


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
        status (str): The status of the ticket. For example, "Resolved".
        title (str): The title of the ticket.
        type_ (str): The issue type of the ticket. For example,
            "Improvement".
    """

    def __init__(
        self,
        description: str,
        priority: str,
        project: str,
        resolution: str,
        title: str,
        type_: str,
        source_link: str,
        status: str,
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
            status: The status of the ticket. For example, "Resolved".
            title: The title of the ticket.
            type_: The issue type of the ticket. For example,
                "Improvement".
        """
        self.description = description
        self.priority = priority
        self.project = project
        self.resolution = resolution
        self.title = title
        self.type = type_
        self.source_link = source_link
        self.status = status
