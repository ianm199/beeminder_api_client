from unittest.mock import Mock, patch

import pytest

from beeminder import BeeminderAPI
from models import BeeminderGoal, BeeminderUser, Datapoint


BASE_URL = "https://www.beeminder.com/api/v1"


def response_with(payload):
    response = Mock()
    response.json.return_value = payload
    return response


@patch("beeminder.requests.get")
def test_get_goal_constructs_request_and_parses_nested_datapoints(mock_get):
    mock_get.return_value = response_with(
        {
            "slug": "reading",
            "title": "Read every day",
            "datapoints": [{"id": "dp-1", "value": 12.5, "comment": "pages"}],
        }
    )
    client = BeeminderAPI("secret", default_user="alice")

    goal = client.get_goal(None, "reading", datapoints=True)

    mock_get.assert_called_once_with(
        f"{BASE_URL}/users/alice/goals/reading.json",
        params={"datapoints": "true", "auth_token": "secret"},
    )
    mock_get.return_value.raise_for_status.assert_called_once_with()
    assert isinstance(goal, BeeminderGoal)
    assert goal.slug == "reading"
    assert goal.datapoints[0].value == 12.5
    assert goal.datapoints[0].comment == "pages"


@patch("beeminder.requests.get")
def test_get_all_goals_uses_explicit_user_and_parses_models(mock_get):
    mock_get.return_value = response_with([{"slug": "run"}, {"slug": "read"}])

    goals = BeeminderAPI("key", default_user="ignored").get_all_goals("bob")

    mock_get.assert_called_once_with(
        f"{BASE_URL}/users/bob/goals.json", params={"auth_token": "key"}
    )
    assert [goal.slug for goal in goals] == ["run", "read"]
    assert all(isinstance(goal, BeeminderGoal) for goal in goals)


@patch("beeminder.requests.get")
def test_get_user_builds_optional_query_and_parses_user(mock_get):
    mock_get.return_value = response_with(
        {"username": "alice", "goals": ["read"], "created_at": 10, "updated_at": 20}
    )

    user = BeeminderAPI("key").get_user(
        "alice", associations=True, diff_since=123, skinny=True, datapoints_count=7
    )

    mock_get.assert_called_once_with(
        f"{BASE_URL}/users/alice.json",
        params={
            "associations": "true",
            "skinny": "true",
            "diff_since": 123,
            "datapoints_count": 7,
            "auth_token": "key",
        },
    )
    assert isinstance(user, BeeminderUser)
    assert user.goals == ["read"]


@patch("beeminder.requests.post")
def test_create_goal_posts_auth_and_parses_goal(mock_post):
    mock_post.return_value = response_with({"slug": "meditate", "title": "Meditate"})
    goal_data = {"slug": "meditate", "title": "Meditate"}

    goal = BeeminderAPI("key", "alice").create_goal(None, goal_data)

    mock_post.assert_called_once_with(
        f"{BASE_URL}/users/alice/goals.json",
        data={"slug": "meditate", "title": "Meditate", "auth_token": "key"},
    )
    mock_post.return_value.raise_for_status.assert_called_once_with()
    assert isinstance(goal, BeeminderGoal)
    assert goal.slug == "meditate"


@patch("beeminder.requests.get")
def test_get_datapoints_sends_filters_and_parses_each_result(mock_get):
    mock_get.return_value = response_with(
        [{"id": "one", "value": 1}, {"id": "two", "value": 2.5}]
    )

    points = BeeminderAPI("key", "alice").get_datapoints(
        None, "water", sort="timestamp", count=2, page=3, per=10
    )

    mock_get.assert_called_once_with(
        f"{BASE_URL}/users/alice/goals/water/datapoints.json",
        params={
            "sort": "timestamp",
            "count": 2,
            "page": 3,
            "per": 10,
            "auth_token": "key",
        },
    )
    assert [point.value for point in points] == [1.0, 2.5]
    assert all(isinstance(point, Datapoint) for point in points)


@patch("beeminder.requests.post")
def test_create_datapoint_posts_fields_and_parses_response(mock_post):
    mock_post.return_value = response_with(
        {"id": "new", "value": 3.5, "timestamp": 1700000000, "comment": "cups"}
    )

    point = BeeminderAPI("key", "alice").create_datapoint(
        None, "water", 3.5, timestamp=1700000000, comment="cups", requestid="req-1"
    )

    mock_post.assert_called_once_with(
        f"{BASE_URL}/users/alice/goals/water/datapoints.json",
        data={
            "value": 3.5,
            "timestamp": 1700000000,
            "comment": "cups",
            "requestid": "req-1",
            "auth_token": "key",
        },
    )
    assert isinstance(point, Datapoint)
    assert point.id == "new"


@patch("beeminder.requests.post")
def test_update_datapoint_preserves_zero_and_empty_values(mock_post):
    mock_post.return_value = response_with({"id": "dp-1", "value": 0, "comment": ""})

    point = BeeminderAPI("key", "alice").update_datapoint(
        None, "water", "dp-1", value=0, timestamp=0, comment=""
    )

    mock_post.assert_called_once_with(
        f"{BASE_URL}/users/alice/goals/water/datapoints/dp-1.json",
        data={"value": 0, "timestamp": 0, "comment": "", "auth_token": "key"},
    )
    assert point.value == 0


@patch("beeminder.requests.delete")
def test_delete_datapoint_authenticates_and_parses_deleted_point(mock_delete):
    mock_delete.return_value = response_with({"id": "dp-1", "value": 4})

    point = BeeminderAPI("key", "alice").delete_datapoint(None, "water", "dp-1")

    mock_delete.assert_called_once_with(
        f"{BASE_URL}/users/alice/goals/water/datapoints/dp-1.json",
        params={"auth_token": "key"},
    )
    mock_delete.return_value.raise_for_status.assert_called_once_with()
    assert isinstance(point, Datapoint)
    assert point.id == "dp-1"


@patch("beeminder.requests.get")
def test_missing_user_fails_before_any_request(mock_get):
    with pytest.raises(ValueError, match="User must be provided"):
        BeeminderAPI("key").get_goal(None, "reading")

    mock_get.assert_not_called()
