import requests
import os
from dotenv import load_dotenv
import json
import time
import random
import datetime
from threading import Thread

load_dotenv()
ds_token = os.getenv("DISCORD_TOKEN")

trivia_chat = "https://discord.com/api/v9/channels/578675563301044234/messages"
search_req = "https://discord.com/api/v9/guilds/251072485095636994/messages/search?channel_id=578675563301044234"
trivia_chat_typing = "https://discord.com/api/v9/channels/578675563301044234/typing"
epic_battle_chat_typing = (
    "https://discord.com/api/v9/channels/615750969162203156/typing"
)
epic_battle_chat = "https://discord.com/api/v9/channels/615750969162203156/messages"
druid_chat = "https://discord.com/api/v9/channels/1119710848387133461/messages"
druid_chat_typing = "https://discord.com/api/v9/channels/1119710848387133461/typing"

ch_of_not_speaking = 0.2
ch_of_typo = 0.05

not_questions_list = [
    "You have been registered for the final battle.",
    "Trivia will begin in about 10 seconds. You will have 45 seconds to answer each question.",
    "Get ready for the next question!",
]


def swap(text):
    if len(text) < 2:
        return text

    index = random.randint(0, len(text) - 2)

    text_list = list(text)
    text_list[index], text_list[index + 1] = text_list[index + 1], text_list[index]

    return "".join(text_list)


def get_question(limit, chat) -> str:
    try:
        request_get_question = requests.get(
            f"{chat}?limit={limit}", headers={"Authorization": ds_token}
        )
        info_question = json.loads(request_get_question.text)
        if chat == trivia_chat:
            for elem in info_question:
                if elem["author"]["username"] == "Trivia Guide Bot":
                    return elem["embeds"][0]["description"]
        else:
            for elem in info_question:
                if elem["author"]["username"] == "Epic Battle Dryad Bot":
                    return elem["content"]
    except Exception as e:
        print(
            f"ERROR occured while getting the question:\n\n{e}\n-----------------------------"
        )


def search(content: str, x=1) -> str:
    try:
        request_get_answer1 = requests.get(
            f"{search_req}&content={content}", headers={"Authorization": ds_token}
        )
        info1 = json.loads(request_get_answer1.text)
        message_id = info1["messages"][x][0]["id"]

        request_get_answer2 = requests.get(
            f"{trivia_chat}?limit=20&after={message_id}",
            headers={"Authorization": ds_token},
        )
        info2 = json.loads(request_get_answer2.text)

        list_of_answers = {}

        for elem in info2[::-1]:
            if elem["author"]["username"] == "Trivia Guide Bot" and elem["embeds"]:
                bot_message = elem["embeds"][0]["description"]
                break
            list_of_answers[elem["author"]["username"]] = (
                elem["content"],
                elem["edited_timestamp"] == None,
            )

        user_who_answered_correctly = bot_message.split("has ")[0]

        for user, answer in list_of_answers.items():
            if user.strip() == user_who_answered_correctly.strip():
                if answer[1]:
                    return answer[0]
                else:
                    return search(content, x=x + 1)
    except Exception as e:
        print(
            f"ERROR occured while searching for the answer:\n\n{e}\n-----------------------------"
        )


def send_message(content: str, chat: str):
    try:
        requests.post(
            chat,
            data={"content": content},
            headers={"Authorization": ds_token},
        )
    except Exception as e:
        print(
            f"TRIVIA ERROR occured while sending a message:\n\n{e}\n-----------------------------"
        )


def random_events(answer: str):
    n1, n2 = [random.randint(1, 100) for _ in range(2)]
    if n1 <= ch_of_not_speaking * 100:
        return None
    if n2 <= ch_of_typo * 100:
        return generate_typo(answer)
    return answer


def generate_typo(line: str):
    if line.isdigit():
        chance = random.randint(1, 30)
        if chance == 1:
            return str(int(line) + random.randint(-5, 5))
    else:
        type_of_typo = random.randint(1, 1)
        if type_of_typo == 1:
            return swap(line)


def trivia():

    already_answered = False

    while True:
        current_min = datetime.datetime.now().minute
        current_sec = datetime.datetime.now().second
        if current_min % 5 == 0 and current_sec == 2:
            question = get_question(15, trivia_chat)
            answer = search(question)
            if answer and not already_answered:
                answer = random_events(answer)
                if answer:
                    already_answered = True
                    requests.post(
                        trivia_chat_typing, headers={"Authorization": ds_token}
                    )
                    sleeping_time = len(answer) * 0.15
                    time.sleep(sleeping_time)
                    send_message(
                        (
                            answer.capitalize()
                            if random.randint(1, 5) == 1
                            else answer.lower()
                        ),
                        trivia_chat,
                    )
                    print("trivia: sent answer:", answer)
                else:
                    already_answered = False
                    print("trivia: sent nothing")
            else:
                already_answered = False
                print("trivia: sent nothing")
            time.sleep(60)
        time.sleep(0.5)


def epic_battle():
    while True:

        not_questions = not_questions_list.copy()

        selected_min = random.randint(0, 59)
        while 28 <= selected_min <= 40:
            selected_min = random.randint(0, 59)
        selected_sec = random.randint(0, 59)
        print(f"epic battle: selected time: {selected_min}:{selected_sec}")
        while True:
            current_min = datetime.datetime.now().minute
            current_sec = datetime.datetime.now().second
            if current_min == selected_min and current_sec == selected_sec:
                requests.post(
                    epic_battle_chat_typing, headers={"Authorization": ds_token}
                )
                time.sleep(1.2)
                send_message("bb!register", epic_battle_chat)
                print("epic battle: registered")
                break
            time.sleep(0.5)
        while True:
            current_min = datetime.datetime.now().minute
            current_sec = datetime.datetime.now().second
            if current_min == 31 and current_sec == 10:
                requests.post(
                    epic_battle_chat_typing, headers={"Authorization": ds_token}
                )
                time.sleep(0.1)
                send_message(str(random.randint(0, 9)), druid_chat)
                break
            time.sleep(0.5)
        time.sleep(1)
        while True:
            question = get_question(5, druid_chat)
            while question in not_questions:
                question = get_question(5, druid_chat)
                time.sleep(0.1)
            if "The trivia is over!" in question:
                break
            answer = search(question)
            if answer:
                answer = random_events(answer)
                if answer:
                    requests.post(
                        druid_chat_typing, headers={"Authorization": ds_token}
                    )
                    sleeping_time = len(answer) * 0.15
                    time.sleep(sleeping_time)
                    send_message(
                        (
                            answer.capitalize()
                            if random.randint(1, 5) == 1
                            else answer.lower()
                        ),
                        druid_chat,
                    )
                    print(f"epic battle: sent answer:", answer)
                else:
                    print(f"epic battle: sent nothing")
            else:
                print(f"epic battle: sent nothing")
            not_questions.append(question)


t1 = Thread(target=trivia)
t2 = Thread(target=epic_battle)

t2.start()
t1.start()
