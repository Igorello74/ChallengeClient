from API import Client, TaskStatus

client = Client(
    "tkBOCFVdpTEHRHY6qIPrara/mf5pH2xK",
    "https://igorello.free.beeceptor.com/",
    round_id="projects-course-5-2")

for task in client.get_tasks("math", TaskStatus.Pending, count=50):
    print(task)
    # for i in range(5):
    #     print(client.submit_answer(task.id, answer='123'))