from API import Client, TaskStatus
from tasks.json import solve

client = Client(
    "pfefcQ4kcNxiptieTbKOwC1WRBESHwH",
    "https://d5du86l4q39mtqf01fce.apigw.yandexcloud.net/",
    challenge_id="projects-course-personal")

for i in range(50):
    task = client.fetch_new_task('json')
    answer = solve(task.question)

    status = client.submit_answer(task.id, answer).status
    if status != TaskStatus.Success:
        print("failed")
        break
    print("solved")
