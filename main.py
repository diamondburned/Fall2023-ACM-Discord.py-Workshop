import discord
from discord.ext import commands

from dotenv import load_dotenv
from utils import is_env_set, ask_question, return_sorted_leaderboard_msg, restart

from pyopentdb import OpenTDBClient, Category, QuestionType, Difficulty

from utils import GameState, Question

load_dotenv()

TOKEN = is_env_set()


bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
# intents.all() enables your Discord bot to receive all available types of events from Discord

game_state = GameState()


@bot.event
async def on_ready():
    # Explain what a bot.tree is, why do we need to do that?
    # Syncs all the slash commands into one big tree
    await bot.tree.sync()

    # When starting a new game we need to clear players all the time
    restart(game_state)

    embed = discord.Embed(
        title="Trivia Game Started!",
        color=discord.Color.brand_green(),
        description="Join using **/join** to play!",
    )

    channel = bot.get_channel(1109275176807432202)

    await channel.send(embed=embed)


# ------------------------------
# Baseline code (blueprint for slash commands first before logic)
# ------------------------------


@bot.tree.command(name="join")
async def join(interaction: discord.Interaction):
    # game.is_running is determined by modifying to True in /start
    if game_state.is_running:
        embed = discord.Embed(
            title=f"{interaction.user.name}, the game has already started...",
            color=discord.Color.red(),
        )
    elif interaction.user.name not in game_state.scores:
        # Create new user with their score if 0
        game_state.scores.clear()

        game_state.scores[interaction.user.name] = 0
        embed = discord.Embed(
            title=f"{interaction.user.name}, you have joined!",
            color=discord.Color.blue(),
            description=f"**{len(game_state.scores)}** players waiting in line... \nIf **all players** are ready, please type **/start** to begin.",
        )
    else:
        # User has already joined!
        embed = discord.Embed(
            title=f"{interaction.user.name}, you have already joined!",
            color=discord.Color.red(),
            description=f"**{len(game_state.scores)}** players waiting in line... \nIf **all players** are ready, please type **/start** to begin.",
        )

    await interaction.response.send_message(embed=embed)


# ------------------------------
# Here explain argument types and how to make them optional!
# ------------------------------


@bot.tree.command(name="start")
@discord.app_commands.describe(amount="Amount of questions (DEFAULT - 5)")
@discord.app_commands.choices(
    difficulty=[
        discord.app_commands.Choice(name="Easy", value=Difficulty.EASY.name),
        discord.app_commands.Choice(name="Medium", value=Difficulty.MEDIUM.name),
        discord.app_commands.Choice(name="Hard", value=Difficulty.HARD.name),
    ]
)
@discord.app_commands.choices(
    category=[
        discord.app_commands.Choice(
            name="General Knowledge", value=Category.GENERAL_KNOWLEDGE.name
        ),
        discord.app_commands.Choice(
            name="Computer Science", value=Category.SCIENCE_COMPUTERS.name
        ),
    ]
)
async def start(
    interaction: discord.Interaction,
    amount: str = "5",
    # Discuss placing default values in param types
    difficulty: str = Difficulty.EASY.name,
    # Explain to look at the documentation
    category: str = Category.SCIENCE_COMPUTERS.name,
):
    # Enable is_running to True! We've started the game!!!
    game_state.is_running = True

    client = OpenTDBClient()
    questions = client.get_questions(
        amount=int(amount),
        category=Category[category],
        difficulty=Difficulty[difficulty],
        question_type=QuestionType.TRUE_FALSE,
    )

    """
    [question='The Sun rises from the North.', choices=['False', 'True'],
    answer='False', answer_index=0) ......., 
    """

    game_state.questions = [
        (Question(question.question, question.choices, question.answer))
        for question in questions
    ]
    print(game_state.questions)

    # game.questions = [("QUESTION 1", ["True", "False"], "ANSWER1"), ("QUESTION 2", ["True", "False"], "ANSWER2")...]

    await ask_question(interaction, game_state, game_state.scores)


@bot.tree.command(name="answer")
@discord.app_commands.choices(
    answer=[
        discord.app_commands.Choice(name="T", value="True"),
        discord.app_commands.Choice(name="F", value="False"),
    ]
)
async def answer(
    interaction: discord.Interaction,
    answer: discord.app_commands.Choice[str],
):
    # DICUSS AT THE END
    if interaction.user.name not in game_state.scores:
        embed = discord.Embed(
            title=f"**{interaction.user.name} you're not in the game! Wait till next round!**",
            color=discord.Color.red(),
        )

        await interaction.response.send_message(
            content=f"<@{interaction.user.id}>", embed=embed
        )

        return

    is_answer_correct = False

    if answer.value == game_state.get_current_question().answer:
        game_state.scores[interaction.user.name] += 1
        embed = discord.Embed(
            title=f"**{interaction.user.name} GOT THE QUESTION!**",
            color=discord.Color.green(),
        )

        is_answer_correct = True

        game_state.current_q_index += 1

    else:
        embed = discord.Embed(title="**NOPE!**", color=discord.Color.red())

    await interaction.response.send_message(
        content=f"<@{interaction.user.id}>", embed=embed
    )

    if is_answer_correct:
        await ask_question(interaction, game_state, game_state.scores)


# ------------------------------
# Explain here about sorting dictionaries and how it works
# ------------------------------
@bot.tree.command(name="leaderboard")
async def leaderboard(interaction: discord.Interaction):
    embed = return_sorted_leaderboard_msg(game_state.scores)

    await interaction.response.send_message(embed=embed)


# ------------------------------
# Please don't forget this
# ------------------------------
bot.run(TOKEN)
