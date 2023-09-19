import os
from typing import List, Dict
import discord
from dataclasses import dataclass


@dataclass
class Question:
    question: str
    choices: List[any]
    answer: str


class GameState:
    current_q_index = 0

    # Hold the players and the score as the value
    scores: Dict[str, int] = {}
    # Holds the question, choices, answer
    questions: List[Question] = []
    # If game is running
    is_running: bool = False

    def get_current_question(self) -> Question:
        return self.questions[self.current_q_index]


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


def restart(game_state: GameState):
    game_state.current_q_index = 0
    game_state.questions.clear()
    game_state.is_running = False


# change the game state to the next question and return the response embed
def ask_question(
    interaction: discord.Interaction,
    game_state: GameState,
    players,
) -> discord.Embed:
    # Do this at the end (SIDE - CASE)
    if game_state.current_q_index >= len(game_state.questions):
        restart(game_state)
        return return_sorted_leaderboard_msg(players)

    current_question = game_state.get_current_question()

    formatted_choices = ", ".join(current_question.choices)
    # What it will look like - True, False

    message = f"**{current_question.question}**\n**Choices**: {formatted_choices}"
    return discord.Embed(
        title=f"**NEW QUESTION**",
        color=discord.Color.blue(),
        description=message,
    )
