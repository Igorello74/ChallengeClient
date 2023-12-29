# ChallengeClient
Hi! This neat lib allows you to perform challenges without having to worry
about the challenges site api - it lets you focus on the main thing - tasks.

# Example
```python
from API import Client, TaskStatus

client = Client(
    "<secret>",
    "https://d5du86l4q39mtqf01fce.apigw.yandexcloud.net/",
    challenge_id="projects-course")

def solve(data: str) -> str:
    return "42"

for i in range(50):
    task = client.fetch_new_task('starter')
    answer = solve(task.question)

    status = client.submit_answer(task.id, answer).status
    if status != TaskStatus.Success:
        print("failed")
        break
    print("solved")
```

# Docs
The most important part of this package is the the Client class in the client.py file,
so you can use its docstrings.

# Feedback
If you encounter any kind of problem with this lib,
don't hestitate to write me: sidneff.igor@ya.ru

Good luck with challenges :)