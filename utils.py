import os
from typing import List, Dict
import discord
import game
from dataclasses import dataclass


# cool little embed for when game is not found
def game_not_found_embed():
    return discord.Embed(
        title="**No game is currently running!**",
        color=discord.Color.red(),
    )


def return_sorted_leaderboard_msg(game_state: game.GameState) -> discord.Embed:
    message_description = ""
    for player, score in game_state.leaderboard():
        message_description += f"{player} - {score}\n"

    return discord.Embed(
        title=f"**LEADERBOARD**",
        color=discord.Color.purple(),
        description=message_description,
    )


# change the game state to the next question and return the response embed
def get_question_embed(
    interaction: discord.Interaction,
    game_state: game.GameState,
) -> discord.Embed:
    # Do this at the end (SIDE - CASE)
    if game_state.is_ended():
        return return_sorted_leaderboard_msg(game_state)

    current_question = game_state.get_current_question()
    formatted_choices = ", ".join(current_question.choices)
    # What it will look like - True, False

    message = f"**{current_question.question}**\n**Choices**: {formatted_choices}"
    return discord.Embed(
        title=f"**NEW QUESTION**",
        color=discord.Color.blue(),
        description=message,
    )
