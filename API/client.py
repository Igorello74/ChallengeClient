from datetime import datetime, timezone
from typing import TypeVar
from urllib.parse import quote as url_encode
from urllib.parse import urljoin

import requests

from .contracts import Challenge, Round, Task, TaskStatus
from .errors import NoRoundCurrentlyRunningError, TasksOverError
from .json_magic import deserialize

T = TypeVar("T")


class Client:
    """A client for the challenge API

    Public methods:
        __init__: constructor
        fetch_new_task: fetch a new task
        submit_answer: submit an answer to the given task
        get_tasks: get tasks of the given type and status
        get_task: get a task by its id
        get_challenge: get a challenge by its id

    Public instance variables (fields):
        secret: a string with the secret token of the team
        round: an instance of Round (used in `fetch_new_task` and `get_tasks`)

    Both of the fields are set in the constructor, but you can easily
    change their values during runtime if you need to.
    """
    secret: str
    round: Round
    _base_url: str

    def __init__(
        self,
        secret: str,
        base_url: str,
        *,
        round_id: str | None = None,
        challenge_id: str | None = None
    ):
        """Init a new Client instance.

        Note: you may pass round_id explicitly or have the currently
        running round chosen automatically, in that case you have to
        provide challenge_id. In other words, either round_id or
        challenge_id must not be None.

        Also, you MUST NOT add the "api/" suffix to the base_url, since
        it is automatically added inside.

        Args:
            secret: a secret token the team was given.
            base_url: the url of the challenge site (e.g. "https://urfav-challenge.ru/"). You MUST NOT add the "api/" suffix to the url.
            round_id: the round id (e.g. "projects-course-1"). If None, the current round is automatically chosen.
            challenge_id: the challenge id (e.g. "projects-course"). May be None if round_id is provided.

        Raises:
            ValueError: if both round_id and challenge_id are None
            NoRoundCurrentlyRunning: if round_id is None and no round is currently running.
        """
        self.secret = secret
        self._base_url = urljoin(base_url, "api/")

        if round_id is None:
            if challenge_id is None:
                raise ValueError(
                    "Either round_id or challenge_id must be not None")
            self.round = self._get_current_round(challenge_id)
        else:
            self.round = Round(round_id, datetime.min, datetime.max, True)

    def fetch_new_task(self, type: str | None) -> Task:
        """Fetch a new task of a given type.

        Args:
            type: type of the task (e.g. "math"). If None, a task of random type is fetched.

        Raises:
            ValueError: if you provide a type whereas this round doesn't allow you doing so
            TasksOver: when there are no more tasks of this type (on this round)

        Returns:
            an instance of contracts.Task
        """

        params = {'round': self.round.id}
        if type is not None:
            if self.round.can_choose_type:
                params['type'] = type
            else:
                raise ValueError(
                    "You are not allowed to choose the task type in this round")

        try:
            data = self._post("tasks", params)
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 400:
                raise TasksOverError(type)
            raise

        return deserialize(data, Task)

    def submit_answer(self, task_id: str, answer: str) -> Task:
        """Submit an answer to the given task.

        Args:
            task_id: the task id.
            answer: the answer

        Returns:
            the new state of the Task (you are likely interested in the status field)
        """

        response = self._post(
            f"tasks/{task_id}",
            json={"answer": answer})

        return deserialize(response, Task)

    def get_tasks(self, type: str, status: TaskStatus,
                  offset: int = 0, count: int = 50) -> list[Task]:
        """Get tasks of the given type and status.

        Note: it doesn't fetch NEW tasks.

        Args:
            type: type of the task (e.g. "cypher")
            status: status of the task (checkout contracts.TaskStatus)
            offset: Cursor offset. Defaults to 0.
            count: Maximum number of tasks to get. Must be <= 50. Defaults to 50.

        Raises:
            ValueError: if count > 50

        Returns:
            a list of Tasks (checkout contracts.Task)

        """
        if count > 50:
            raise ValueError("count has to be <= 50")

        return self._get_and_deserialize(list[Task], "tasks", {
            'round': self.round.id,
            'type': type,
            'status': status.value,
            'offset': offset,
            'count': count
        })

    def get_task(self, id: str) -> Task:
        """Get a task by its id.

        Args:
            task_id: id of the task

        Returns:
            an instance of contracts.Task
        """
        return self._get_and_deserialize(Task, f"tasks/{id}")

    def get_challenge(self, id: str) -> Challenge:
        """Get a challenge by its id.

        Args:
            id: id of the challenge

        Returns:
            an instance of contracts.Challenge
        """
        return self._get_and_deserialize(Challenge, f"challenges/{id}/")

    def _get_current_round(self, challenge_id: str) -> Round:
        """Get the currently running round."""
        rounds = self.get_challenge(challenge_id).rounds

        now = datetime.now(tz=timezone.utc)
        for round in rounds:
            if round.start_timestamp <= now <= round.end_timestamp:
                return round

        raise NoRoundCurrentlyRunningError()

    def _get_and_deserialize(
        self,
        cls: type[T],
        subpath: str,
        params: dict | None = None,
        **kwargs
    ) -> T:
        """GET a subpath and deserialize the response."""
        return deserialize(self._get(subpath, params, **kwargs), cls)

    def _get(self, subpath: str, params: dict | None = None, **kwargs) -> str:
        """Perform the GET request by the given subpath."""
        return self._request("GET", subpath, params or {}, **kwargs)

    def _post(self, subpath: str, params: dict | None = None, **kwargs) -> str:
        """Perform the POST request by the given subpath."""
        return self._request("POST", subpath, params or {}, **kwargs)

    def _request(self, method: str, subpath: str, params: dict, **kwargs) -> str:
        """Perform a request of a given method by the given subpath.

        Note: self.secret param is automatically added to the request.

        Args:
            method: HTTP method (POST, GET, etc.)
            subpath: the subpath of the url
            params: query params (like "?key1=val1&key2=val2")

        Returns:
            The text body of the response.

        Raises:
            requests.HTTPError in case of non-success response status code.
        """
        response = requests.request(
            method,
            urljoin(self._base_url, url_encode(subpath)),
            params=params | {"secret": self.secret},
            **kwargs
        )

        response.raise_for_status()

        return response.text
