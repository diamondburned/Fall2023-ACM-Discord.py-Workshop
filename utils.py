import os
from typing import List, Dict
import discord
from dataclasses import dataclass


@dataclass
class Question:
    question: str
    choices: List[str]
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

    def is_ended(self) -> bool:
        return len(self.questions) > 0 and self.current_q_index >= len(self.questions)


# Track one game state per channel
game_channels: dict[int, GameState] = {}


def must_get_game(
    interaction: discord.Interaction,
    create=False,
    accept_ended=False,
) -> GameState | None:
    assert interaction.channel_id is not None  # make discord.py happy :)

    game_state = game_channels.get(interaction.channel_id)
    if game_state is None:
        if create:
            game_state = GameState()
            game_channels[interaction.channel_id] = game_state
        else:
            return None

    if not accept_ended and game_state.is_ended():
        return None

    return game_state


# cool little embed for when game is not found
def game_not_found_embed():
    return discord.Embed(
        title="**No game is currently running!**",
        color=discord.Color.red(),
    )


def get_token() -> str:
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


# change the game state to the next question and return the response embed
def get_question_embed(
    interaction: discord.Interaction,
    game_state: GameState,
) -> discord.Embed:
    # Do this at the end (SIDE - CASE)
    if game_state.is_ended():
        return return_sorted_leaderboard_msg(game_state.scores)

    current_question = game_state.get_current_question()

    formatted_choices = ", ".join(current_question.choices)
    # What it will look like - True, False

    message = f"**{current_question.question}**\n**Choices**: {formatted_choices}"
    return discord.Embed(
        title=f"**NEW QUESTION**",
        color=discord.Color.blue(),
        description=message,
    )
