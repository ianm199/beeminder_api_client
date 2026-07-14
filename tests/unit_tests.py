from unittest.mock import Mock, patch

import pytest

from beeminder_client.beeminder import BeeminderAPI
from beeminder_client.models import BeeminderGoal, BeeminderUser, Datapoint


BASE_URL = "https://www.beeminder.com/api/v1"


def response_with(payload):
    response = Mock()
    response.json.return_value = payload
    return response


@pytest.fixture
def client():
    return BeeminderAPI("secret-token", default_user="alice")


def test_get_goal_constructs_request_and_parses_nested_datapoints(client):
    payload = {
        "slug": "read",
        "title": "Read books",
        "datapoints": [{"id": "dp-1", "value": 2, "comment": "chapters"}],
    }
    response = response_with(payload)

    with patch("beeminder_client.beeminder.requests.get", return_value=response) as get:
        goal = client.get_goal(None, "read", datapoints=True)

    get.assert_called_once_with(
        f"{BASE_URL}/users/alice/goals/read.json",
        params={"datapoints": "true", "auth_token": "secret-token"},
    )
    response.raise_for_status.assert_called_once_with()
    assert isinstance(goal, BeeminderGoal)
    assert isinstance(goal.datapoints[0], Datapoint)
    assert goal.datapoints[0].value == 2


def test_get_all_and_archived_goals_use_expected_endpoints(client):
    with patch.object(client, "_get", side_effect=[
        [{"slug": "current"}],
        [{"slug": "retired"}],
    ]) as get:
        current = client.get_all_goals(None)
        archived = client.get_archived_goals("bob")

    assert [goal.slug for goal in current] == ["current"]
    assert [goal.slug for goal in archived] == ["retired"]
    get.assert_any_call("/users/alice/goals.json")
    get.assert_any_call("/users/bob/goals/archived.json")


def test_create_and_update_goal_construct_post_requests(client):
    create_response = response_with({"slug": "write", "title": "Write"})
    update_response = response_with({"slug": "write", "title": "Write daily"})

    with patch(
        "beeminder_client.beeminder.requests.post",
        side_effect=[create_response, update_response],
    ) as post:
        created = client.create_goal(None, {"slug": "write", "title": "Write"})
        updated = client.update_goal("bob", "write", {"title": "Write daily"})

    assert isinstance(created, BeeminderGoal)
    assert updated["title"] == "Write daily"
    assert post.call_args_list[0].args == (f"{BASE_URL}/users/alice/goals.json",)
    assert post.call_args_list[0].kwargs == {
        "data": {"slug": "write", "title": "Write", "auth_token": "secret-token"}
    }
    assert post.call_args_list[1].args == (f"{BASE_URL}/users/bob/goals/write.json",)
    assert post.call_args_list[1].kwargs == {
        "data": {"title": "Write daily", "auth_token": "secret-token"}
    }
    create_response.raise_for_status.assert_called_once_with()
    update_response.raise_for_status.assert_called_once_with()


def test_get_user_constructs_optional_params_and_parses_model(client):
    payload = {
        "username": "alice",
        "goals": ["read"],
        "created_at": 10,
        "updated_at": 20,
        "timezone": "America/New_York",
    }
    with patch.object(client, "_get", return_value=payload) as get:
        user = client.get_user(
            associations=True, diff_since=123, skinny=True, datapoints_count=4
        )

    get.assert_called_once_with(
        "/users/alice.json",
        {
            "associations": "true",
            "skinny": "true",
            "diff_since": 123,
            "datapoints_count": 4,
        },
    )
    assert isinstance(user, BeeminderUser)
    assert user.goals == ["read"]


def test_authenticate_and_redirect_uses_get_with_token(client):
    with patch.object(client, "_get", return_value={"redirect": "ok"}) as get:
        result = client.authenticate_and_redirect(None, "https://example.test/after")

    get.assert_called_once_with(
        "/users/alice.json",
        {
            "redirect_to_url": "https://example.test/after",
        },
    )
    assert result == {"redirect": "ok"}


def test_get_datapoints_constructs_filters_and_parses_models(client):
    with patch.object(
        client, "_get", return_value=[{"id": "dp-1", "value": 3.5}]
    ) as get:
        datapoints = client.get_datapoints(
            None, "read", sort="timestamp", count=2, page=3, per=10
        )

    get.assert_called_once_with(
        "/users/alice/goals/read/datapoints.json",
        {
            "sort": "timestamp",
            "count": 2,
            "page": 3,
            "per": 10,
        },
    )
    assert isinstance(datapoints[0], Datapoint)
    assert datapoints[0].value == 3.5


def test_create_datapoint_constructs_payload_and_parses_model(client):
    payload = {"id": "dp-1", "value": 1.25, "timestamp": 100, "comment": "done"}
    with patch.object(client, "_post", return_value=payload) as post:
        datapoint = client.create_datapoint(
            None,
            "read",
            1.25,
            timestamp=100,
            daystamp="20260714",
            comment="done",
            requestid="request-1",
        )

    post.assert_called_once_with(
        "/users/alice/goals/read/datapoints.json",
        {
            "value": 1.25,
            "timestamp": 100,
            "daystamp": "20260714",
            "comment": "done",
            "requestid": "request-1",
        },
    )
    assert isinstance(datapoint, Datapoint)
    assert datapoint.id == "dp-1"


def test_create_multiple_datapoints_constructs_payload(client):
    points = [{"value": 1}, {"value": 2, "comment": "two"}]
    with patch.object(client, "_post", return_value={"created": 2}) as post:
        result = client.create_multiple_datapoints(None, "read", points)

    post.assert_called_once_with(
        "/users/alice/goals/read/datapoints/create_all.json",
        {"datapoints": points},
    )
    assert result == {"created": 2}


def test_update_datapoint_includes_explicit_zero_and_empty_comment(client):
    response = response_with({"id": "dp-1", "value": 0, "comment": ""})

    with patch("beeminder_client.beeminder.requests.put", return_value=response) as put:
        datapoint = client.update_datapoint(
            None, "read", "dp-1", value=0, timestamp=0, comment=""
        )

    put.assert_called_once_with(
        f"{BASE_URL}/users/alice/goals/read/datapoints/dp-1.json",
        params={"auth_token": "secret-token"},
        data={"value": 0, "timestamp": 0, "comment": ""},
    )
    response.raise_for_status.assert_called_once_with()
    assert isinstance(datapoint, Datapoint)
    assert datapoint.value == 0


def test_delete_datapoint_constructs_authenticated_delete_and_parses_model(client):
    response = response_with({"id": "dp-1", "value": 4})

    with patch("beeminder_client.beeminder.requests.delete", return_value=response) as delete:
        datapoint = client.delete_datapoint(None, "read", "dp-1")

    delete.assert_called_once_with(
        f"{BASE_URL}/users/alice/goals/read/datapoints/dp-1.json",
        params={"auth_token": "secret-token"},
    )
    response.raise_for_status.assert_called_once_with()
    assert isinstance(datapoint, Datapoint)
    assert datapoint.id == "dp-1"


@pytest.mark.parametrize(
    ("method", "args"),
    [
        ("get_goal", (None, "read")),
        ("get_all_goals", (None,)),
        ("create_goal", (None, {"slug": "read"})),
        ("get_archived_goals", (None,)),
        ("update_goal", (None, "read", {})),
        ("get_datapoints", (None, "read")),
        ("create_datapoint", (None, "read", 1)),
        ("create_multiple_datapoints", (None, "read", [])),
        ("update_datapoint", (None, "read", "dp-1")),
        ("delete_datapoint", (None, "read", "dp-1")),
    ],
)
def test_goal_methods_require_a_user(method, args):
    client = BeeminderAPI("secret-token")

    with pytest.raises(ValueError, match="provided"):
        getattr(client, method)(*args)
