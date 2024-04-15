"""Farms  points on Terraria Discord server."""

from __future__ import annotations

import datetime
import json
import logging
import os
import random
import time
from threading import Thread

import requests  # type: ignore[import-untyped]
from dotenv import load_dotenv

load_dotenv()
ds_token = os.getenv("DISCORD_TOKEN")

TRIVIA_CHAT = "https://discord.com/api/v9/channels/578675563301044234/messages"
SEARCH_REQ = "https://discord.com/api/v9/guilds/251072485095636994/messages/search?channel_id=578675563301044234"
TRIVIA_CHAT_TYPING = "https://discord.com/api/v9/channels/578675563301044234/typing"
EPIC_BATTLE_CHAT_TYPING = (
    "https://discord.com/api/v9/channels/615750969162203156/typing"
)
EPIC_BATTLE_CHAT = "https://discord.com/api/v9/channels/615750969162203156/messages"
DRUID_CHAT = "https://discord.com/api/v9/channels/1119710848387133461/messages"
DRUID_CHAT_TYPING = "https://discord.com/api/v9/channels/1119710848387133461/typing"

NOT_SPEAKING_CHANCE = 0.2
TYPO_CHANCE = 0.05

NON_QUESTIONS = [
    "You have been registered for the final battle.",
    "Trivia will begin in about 10 seconds. You will have 45 seconds to answer each question.",
    "Get ready for the next question!",
]


def __swap(text: str) -> str:
    if len(text) < 2:  # noqa: PLR2004
        return text

    index = random.randint(0, len(text) - 2)

    text_list = list(text)
    text_list[index], text_list[index + 1] = text_list[index + 1], text_list[index]

    return "".join(text_list)


def __get_question(limit: int, chat: str) -> str | None:
    try:
        request_get_question = requests.get(
            f"{chat}?limit={limit}",
            headers={"Authorization": ds_token},
            timeout=5,
        )
        info_question = json.loads(request_get_question.text)
        if chat == TRIVIA_CHAT:
            for elem in info_question:
                if elem["author"]["username"] == "Trivia Guide Bot":
                    return str(elem["embeds"][0]["description"])
        else:
            for elem in info_question:
                if elem["author"]["username"] == "Epic Battle Dryad Bot":
                    return str(elem["content"])
    except Exception:
        logging.exception("Error occured while getting the question")
        return None
    else:
        logging.error("Error occured while getting the question")
        return None


def __search(content: str, x: int = 1) -> str | None:
    try:
        request_get_answer1 = requests.get(
            f"{SEARCH_REQ}&content={content}",
            headers={"Authorization": ds_token},
            timeout=5,
        )
        info1 = json.loads(request_get_answer1.text)
        message_id = info1["messages"][x][0]["id"]

        request_get_answer2 = requests.get(
            f"{TRIVIA_CHAT}?limit=20&after={message_id}",
            headers={"Authorization": ds_token},
            timeout=5,
        )
        info2 = json.loads(request_get_answer2.text)

        list_of_answers: dict[str, tuple[str, bool]] = {}

        for elem in info2[::-1]:
            if elem["author"]["username"] == "Trivia Guide Bot" and elem["embeds"]:
                bot_message = elem["embeds"][0]["description"]
                break
            list_of_answers[elem["author"]["username"]] = (
                elem["content"],
                elem["edited_timestamp"] is None,
            )

        user_who_answered_correctly = bot_message.split("has ")[0]

        for user, answer in list_of_answers.items():
            if user.strip() == user_who_answered_correctly.strip():
                if answer[1]:
                    return answer[0]
                return __search(content, x=x + 1)
    except Exception:
        logging.exception("Error occured while searching for the answer")
        return None
    else:
        logging.error("Error occured while searching for the answer")
        return None


def __send_message(content: str, chat: str) -> None:
    try:
        requests.post(
            chat,
            data={"content": content},
            headers={"Authorization": ds_token},
            timeout=5,
        )
    except Exception:
        logging.exception("Error occured while sending a message")


def __random_events(answer: str) -> str | None:
    n1, n2 = (random.randint(1, 100) for _ in range(2))
    if n1 <= NOT_SPEAKING_CHANCE * 100:
        return None
    if n2 <= TYPO_CHANCE * 100:
        return __generate_typo(answer)
    return answer


def __generate_typo(line: str) -> str:
    if line.isdigit():
        chance = random.randint(1, 30)
        if chance == 1:
            return str(int(line) + random.randint(-5, 5))
    return __swap(line)


TRIVIA_FREQUENCY_MIN = 5
TRIVIA_SEC_OFFSET = 2


def trivia() -> None:
    """Plays the "trivia" game in Terraria Discord."""
    already_answered = False

    while True:
        current_min = datetime.datetime.now().minute  # noqa: DTZ005
        current_sec = datetime.datetime.now().second  # noqa: DTZ005
        if current_min % TRIVIA_FREQUENCY_MIN == 0 and current_sec == TRIVIA_SEC_OFFSET:
            question = __get_question(15, TRIVIA_CHAT)
            if not question:
                continue

            answer = __search(question)
            if answer and not already_answered:
                answer = __random_events(answer)
                if answer:
                    already_answered = True
                    requests.post(
                        TRIVIA_CHAT_TYPING,
                        headers={"Authorization": ds_token},
                        timeout=5,
                    )
                    sleeping_time = len(answer) * 0.15
                    time.sleep(sleeping_time)
                    __send_message(
                        (
                            answer.capitalize()
                            if random.randint(1, 5) == 1
                            else answer.lower()
                        ),
                        TRIVIA_CHAT,
                    )
                    logging.info("trivia: sent answer: %s", answer)
                else:
                    already_answered = False
                    logging.info("trivia: sent nothing")
            else:
                already_answered = False
                logging.info("trivia: sent nothing")
            time.sleep(60)
        time.sleep(0.5)


def __epic_battle_register() -> None:
    while True:
        selected_min = random.randint(28, 40)
        selected_sec = random.randint(0, 59)
        logging.info(
            "epic battle: selected time: %d:%d",
            selected_min,
            selected_sec,
        )

        current_min = datetime.datetime.now().minute  # noqa: DTZ005
        current_sec = datetime.datetime.now().second  # noqa: DTZ005
        if current_min == selected_min and current_sec == selected_sec:
            requests.post(
                EPIC_BATTLE_CHAT_TYPING,
                headers={"Authorization": ds_token},
                timeout=5,
            )
            time.sleep(1.2)
            __send_message("bb!register", EPIC_BATTLE_CHAT)
            logging.info("epic battle: registered")
            break
        time.sleep(0.5)


EPIC_BATTLE_START_MIN = 31
EPIC_BATTLE_START_SEC = 10


def __epic_battle_confirm_registration() -> None:
    while True:
        current_min = datetime.datetime.now().minute  # noqa: DTZ005
        current_sec = datetime.datetime.now().second  # noqa: DTZ005
        if (
            current_min == EPIC_BATTLE_START_MIN
            and current_sec == EPIC_BATTLE_START_SEC
        ):
            requests.post(
                EPIC_BATTLE_CHAT_TYPING,
                headers={"Authorization": ds_token},
                timeout=5,
            )
            time.sleep(0.1)
            __send_message(str(random.randint(0, 9)), DRUID_CHAT)
            break
        time.sleep(0.5)
    time.sleep(1)


def __epic_battle_play() -> None:
    non_questions = NON_QUESTIONS.copy()
    while True:
        question = __get_question(5, DRUID_CHAT)
        while question in non_questions:
            question = __get_question(5, DRUID_CHAT)
            time.sleep(0.1)
        if not question:
            continue

        if "The trivia is over!" in question:
            break
        answer = __search(question)
        if answer:
            answer = __random_events(answer)
            if answer:
                requests.post(
                    DRUID_CHAT_TYPING,
                    headers={"Authorization": ds_token},
                    timeout=5,
                )
                sleeping_time = len(answer) * 0.15
                time.sleep(sleeping_time)
                __send_message(
                    (
                        answer.capitalize()
                        if random.randint(1, 5) == 1
                        else answer.lower()
                    ),
                    DRUID_CHAT,
                )
                logging.info("epic battle: sent answer: %s", answer)
            else:
                logging.info("epic battle: sent nothing")
        else:
            logging.info("epic battle: sent nothing")
        non_questions.append(question)


def epic_battle() -> None:
    """Plays the "epic battle" game in Terraria Discord."""
    while True:
        __epic_battle_register()
        __epic_battle_confirm_registration()
        __epic_battle_play()


if __name__ == "__main__":
    t1 = Thread(target=trivia)
    t2 = Thread(target=epic_battle)

    t2.start()
    t1.start()
