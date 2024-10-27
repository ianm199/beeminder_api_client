import requests
from typing import Optional, List, Dict, Any
from pydantic import ValidationError
from models import BeeminderGoal, BeeminderUser, Datapoint


class BeeminderAPI:
    """
    Python client for the Beeminder API.

    This client allows interaction with Beeminder's goal-tracking API.
    It supports retrieving, creating, and updating goals and datapoints.

    Attributes:
        api_key (str): The API key used to authenticate with Beeminder.
        default_user (Optional[str]): An optional default user to use for API calls.
    """

    BASE_URL = "https://www.beeminder.com/api/v1"

    def __init__(self, api_key: str, default_user: Optional[str] = None):
        """
        Initialize the Beeminder API client.

        Args:
            api_key (str): The API key for authenticating requests.
            default_user (Optional[str]): An optional default user for API calls.
        """
        self.api_key = api_key
        self.default_user = default_user

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Internal method for making GET requests to the Beeminder API.

        Args:
            endpoint (str): The API endpoint to call.
            params (Optional[Dict[str, Any]]): Additional query parameters for the request.

        Returns:
            Dict[str, Any]: The JSON response from the API.
        """
        if params is None:
            params = {}
        params["auth_token"] = self.api_key
        response = requests.get(f"{self.BASE_URL}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method for making POST requests to the Beeminder API.

        Args:
            endpoint (str): The API endpoint to call.
            data (Dict[str, Any]): The data to send in the request.

        Returns:
            Dict[str, Any]: The JSON response from the API.
        """
        data["auth_token"] = self.api_key
        response = requests.post(f"{self.BASE_URL}{endpoint}", data=data)
        response.raise_for_status()
        return response.json()

    def get_goal(self, user: Optional[str], goal_slug: str, datapoints: bool = False) -> BeeminderGoal:
        """
        Get information about a specific goal and return a BeeminderGoal instance.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.
            goal_slug (str): The slug identifier for the goal.
            datapoints (bool): Whether to include datapoints in the response.

        Returns:
            BeeminderGoal: The goal information as a BeeminderGoal object.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")

        params = {"datapoints": str(datapoints).lower()}
        response_data = self._get(f"/users/{user}/goals/{goal_slug}.json", params)

        try:
            return BeeminderGoal(**response_data)
        except ValidationError as e:
            raise ValueError(f"Error parsing Beeminder goal data: {e}")

    def get_all_goals(self, user: Optional[str]) -> List[BeeminderGoal]:
        """
        Get all goals for a user and return them as a list of BeeminderGoal instances.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.

        Returns:
            List[BeeminderGoal]: A list of goals as BeeminderGoal objects.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")

        response_data = self._get(f"/users/{user}/goals.json")

        try:
            return [BeeminderGoal(**goal) for goal in response_data]
        except ValidationError as e:
            raise ValueError(f"Error parsing Beeminder goals data: {e}")

    def create_goal(self, user: Optional[str], goal_data: Dict[str, Any]) -> BeeminderGoal:
        """
        Create a new goal for a user and return the created goal as a BeeminderGoal instance.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.
            goal_data (Dict[str, Any]): The data required to create the goal.

        Returns:
            BeeminderGoal: The created goal information.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")

        response_data = self._post(f"/users/{user}/goals.json", goal_data)

        try:
            return BeeminderGoal(**response_data)
        except ValidationError as e:
            raise ValueError(f"Error parsing Beeminder goal data: {e}")

    def get_archived_goals(self, user: Optional[str]) -> List[BeeminderGoal]:
        """
        Get all archived goals for a user and return them as a list of BeeminderGoal instances.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.

        Returns:
            List[BeeminderGoal]: A list of archived goals as BeeminderGoal objects.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")

        response_data = self._get(f"/users/{user}/goals/archived.json")

        try:
            return [BeeminderGoal(**goal) for goal in response_data]
        except ValidationError as e:
            raise ValueError(f"Error parsing Beeminder archived goals data: {e}")

    def update_goal(self, user: Optional[str], goal_slug: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a goal for a user.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.
            goal_slug (str): The slug identifier for the goal.
            update_data (Dict[str, Any]): The data to update the goal.

        Returns:
            Dict[str, Any]: The updated goal information.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")
        return self._post(f"/users/{user}/goals/{goal_slug}.json", update_data)

    def get_user(
            self,
            username: Optional[str] = None,
            associations: bool = False,
            diff_since: Optional[int] = None,
            skinny: bool = False,
            datapoints_count: Optional[int] = None
    ) -> BeeminderUser:
        """
        Get information about a Beeminder user.

        Args:
            username (Optional[str]): The username to fetch. If None, uses default_user or 'me'.
            associations (bool): If True, fetches all information about user including goals and datapoints.
            diff_since (Optional[int]): Unix timestamp. Only returns goals/datapoints updated since then.
            skinny (bool): If True with diff_since, returns minimal goal attributes and last datapoint only.
            datapoints_count (Optional[int]): If set, limits number of returned datapoints per goal.

        Returns:
            BeeminderUser: The user information as a BeeminderUser object.
        """
        username = username or self.default_user or 'me'

        params = {
            'associations': str(associations).lower(),
            'skinny': str(skinny).lower(),
        }

        if diff_since is not None:
            params['diff_since'] = diff_since
        if datapoints_count is not None:
            params['datapoints_count'] = datapoints_count

        response_data = self._get(f"/users/{username}.json", params)

        try:
            return BeeminderUser(**response_data)
        except ValidationError as e:
            raise ValueError(f"Error parsing Beeminder user data: {e}")

    def authenticate_and_redirect(
            self,
            username: Optional[str],
            redirect_to_url: str
    ) -> Dict[str, Any]:
        """
        Authenticate a user and redirect them to a specific URL on Beeminder.

        Args:
            username (Optional[str]): The username to authenticate. If None, uses default_user.
            redirect_to_url (str): The URL to redirect to after authentication.

        Returns:
            Dict[str, Any]: The API response data.
        """
        username = username or self.default_user
        if not username:
            raise ValueError("Username must be provided either in arguments or as default.")

        params = {
            'redirect_to_url': redirect_to_url
        }

        return self._get(f"/users/{username}.json", params)


    def get_datapoints(
        self,
        user: Optional[str],
        goal_slug: str,
        sort: Optional[str] = None,
        count: Optional[int] = None,
        page: Optional[int] = None,
        per: Optional[int] = None
    ) -> List[Datapoint]:
        """
        Get all datapoints for a specific goal.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.
            goal_slug (str): The slug identifier for the goal.
            sort (Optional[str]): Attribute to sort on, descending. Defaults to id.
            count (Optional[int]): Limit results to count number of datapoints.
            page (Optional[int]): Page number for pagination (1-indexed).
            per (Optional[int]): Number of results per page. Default 25.

        Returns:
            List[Datapoint]: List of datapoints for the goal.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")

        params = {}
        if sort:
            params["sort"] = sort
        if count is not None:
            params["count"] = count
        if page:
            params["page"] = page
        if per:
            params["per"] = per

        response_data = self._get(f"/users/{user}/goals/{goal_slug}/datapoints.json", params)
        return [Datapoint(**point) for point in response_data]

    def create_datapoint(
        self,
        user: Optional[str],
        goal_slug: str,
        value: float,
        timestamp: Optional[int] = None,
        daystamp: Optional[str] = None,
        comment: Optional[str] = None,
        requestid: Optional[str] = None
    ) -> Datapoint:
        """
        Create a new datapoint for a goal.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.
            goal_slug (str): The slug identifier for the goal.
            value (float): The value for the datapoint.
            timestamp (Optional[int]): Unix timestamp for the datapoint.
            daystamp (Optional[str]): Date stamp (YYYYMMDD format).
            comment (Optional[str]): Comment for the datapoint.
            requestid (Optional[str]): Unique identifier for this datapoint.

        Returns:
            Datapoint: The created datapoint.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")

        data = {"value": value}
        if timestamp:
            data["timestamp"] = timestamp
        if daystamp:
            data["daystamp"] = daystamp
        if comment:
            data["comment"] = comment
        if requestid:
            data["requestid"] = requestid

        response_data = self._post(f"/users/{user}/goals/{goal_slug}/datapoints.json", data)
        return Datapoint(**response_data)

    def create_multiple_datapoints(
        self,
        user: Optional[str],
        goal_slug: str,
        datapoints: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create multiple datapoints for a goal.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.
            goal_slug (str): The slug identifier for the goal.
            datapoints (List[Dict[str, Any]]): List of datapoint objects to create.

        Returns:
            Dict[str, Any]: Response containing lists of successful and failed datapoints.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")

        data = {"datapoints": datapoints}
        return self._post(f"/users/{user}/goals/{goal_slug}/datapoints/create_all.json", data)

    def update_datapoint(
        self,
        user: Optional[str],
        goal_slug: str,
        datapoint_id: str,
        value: Optional[float] = None,
        timestamp: Optional[int] = None,
        comment: Optional[str] = None
    ) -> Datapoint:
        """
        Update an existing datapoint.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.
            goal_slug (str): The slug identifier for the goal.
            datapoint_id (str): The ID of the datapoint to update.
            value (Optional[float]): New value for the datapoint.
            timestamp (Optional[int]): New timestamp for the datapoint.
            comment (Optional[str]): New comment for the datapoint.

        Returns:
            Datapoint: The updated datapoint.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")

        data = {}
        if value is not None:
            data["value"] = value
        if timestamp is not None:
            data["timestamp"] = timestamp
        if comment is not None:
            data["comment"] = comment

        response_data = self._post(f"/users/{user}/goals/{goal_slug}/datapoints/{datapoint_id}.json", data)
        return Datapoint(**response_data)

    def delete_datapoint(
        self,
        user: Optional[str],
        goal_slug: str,
        datapoint_id: str
    ) -> Datapoint:
        """
        Delete a datapoint.

        Args:
            user (Optional[str]): The Beeminder username. If None, use default_user.
            goal_slug (str): The slug identifier for the goal.
            datapoint_id (str): The ID of the datapoint to delete.

        Returns:
            Datapoint: The deleted datapoint.
        """
        user = user or self.default_user
        if not user:
            raise ValueError("User must be provided either in arguments or as default.")

        endpoint = f"/users/{user}/goals/{goal_slug}/datapoints/{datapoint_id}.json"
        response_data = self._delete(endpoint)
        return Datapoint(**response_data)



if __name__ == '__main__':
    client = BeeminderAPI(api_key="-8KxLews6xXKXksayesy", default_user="ianm118")
    goal = "deepworkhours"
    data = client.get_goal(user="ianm118", goal_slug=goal, datapoints=True)
    print(data)