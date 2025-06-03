#!/usr/bin/env python3

import random
import datetime
import holidays
import yaml
import os
import requests
from pathlib import Path


def load_config(filename="greetings.yml"):
    script_dir = Path(__file__).resolve().parent
    config_path = script_dir / filename
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_seasonal_message(today):
    month = today.month
    if month in [12, 1, 2]:
        return "Stay cozy — it's coding season ❄️"
    elif month in [3, 4, 5]:
        return "Let’s spring into action 🌱"
    elif month in [6, 7, 8]:
        return "Summer heat, clean commits ☀️"
    elif month in [9, 10, 11]:
        return "Fall in love with your backlog 🍂"
    return ""


def get_greeting(today, config, us_holidays):
    holiday_name = us_holidays.get(today)
    if holiday_name and holiday_name in config.get("holiday_greetings", {}):
        return random.choice(config["holiday_greetings"][holiday_name])

    weekday = today.weekday()
    if weekday == 0:
        return random.choice(config.get("monday_greetings", []))
    elif weekday == 4:
        return random.choice(config.get("friday_greetings", []))
    else:
        return random.choice(config.get("generic_greetings", []))


def post_to_slack(message):
    webhook_url = os.getenv("DAVEBOT_SLACKHOOK")
    if webhook_url:
        requests.post(webhook_url, json={"text": message})


def main():
    today = datetime.date.today()
    us_holidays = holidays.US(years=today.year)
    config = load_config()

    greeting = get_greeting(today, config, us_holidays)
    emoji = random.choice(config.get("emojis", []))
    message_lines = [f"*{greeting}* {emoji}"]

    roll = random.randint(1, 60)

    if roll % 10 in [1, 2]:
        question = random.choice(config.get("questions", []))
        message_lines.append(f"> {question}")
    elif roll % 10 == 0:
        joke = random.choice(config.get("dad_jokes", []))
        message_lines.append(f"> _Dad joke of the day:_ {joke}")

    if roll in [5, 20, 35, 55]:
        seasonal = get_seasonal_message(today)
        message_lines.append(f"_{seasonal}_")

    final_message = "\n".join(message_lines)
    print(final_message)
    post_to_slack(final_message)


if __name__ == "__main__":
    main()
