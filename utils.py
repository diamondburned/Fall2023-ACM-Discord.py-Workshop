import os
from typing import List, Tuple, Dict
import discord


class GameState:
    def __init__(self):
        # Hold the players and the score as the value
        self.scores: Dict[str, int] = {}
        # Holds the question, choices, answer
        self.questions: List[Tuple] = []
        # Store current answer
        self.answer: Dict[str, str] = {}
        # If game is running
        self.is_running: bool = False


def is_env_set() -> str:
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN is None:
        raise EnvironmentError("'DISCORD_TOKEN' is not set!")

    return TOKEN


def return_sorted_leaderboard_msg(players: Dict[str, int]):
    message_description = ""

    # Briefly explain sorting dictionaries!
    # A lambda function is a concise way to create small, anonymous functions in Python.
    sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)
    # Reverse = True -> High to low

    for player, score in sorted_players:
        message_description += f"{player} - {score}\n"

    embed = discord.Embed(
        title=f"**LEADERBOARD**",
        color=discord.Color.purple(),
        description=message_description,
    )

    return embed


async def ask_question(interaction, questions, class_answer, players):
    # Do this at the end (SIDE - CASE)
    if not questions:
        embed = return_sorted_leaderboard_msg(players)
        await interaction.channel.send(embed=embed)
        return  # So we dont continue with the rest of the code

    # Explain unpacking (tuples)
    question, choices, answer = questions.pop()

    formatted_choices = ", ".join(choices)
    # What it will look like - True, False

    message = f"**{question}**\n**Choices**: {formatted_choices}"

    embed = discord.Embed(
        title=f"**NEW QUESTION**", color=discord.Color.blue(), description=message
    )

    for player in players.keys():
        class_answer[player] = answer

    # We cannot do multiple interaction.response.send_message()
    await interaction.channel.send(embed=embed)
