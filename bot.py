import game
import discord
from discord.ext import commands
from pyopentdb import OpenTDBClient, Category, QuestionType, Difficulty
from utils import game_not_found_embed, get_question_embed


bot = commands.Bot(command_prefix="/", intents=discord.Intents.none())


@bot.event
async def on_ready():
    # Explain what a bot.tree is, why do we need to do that?
    # Syncs all the slash commands into one big tree
    await bot.tree.sync()


# ------------------------------
# Baseline code (blueprint for slash commands first before logic)
# ------------------------------


@bot.tree.command(name="join")
async def join(interaction: discord.Interaction):
    game_state = game.create_game(interaction.channel_id)

    # game.is_running is determined by modifying to True in /start
    if interaction.user.name not in game_state.scores:
        # Create new user with their score if 0
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
    # Make sure to use discord.app_commands.Range to ensure minimum one question
    amount: discord.app_commands.Range[int, 1, 100] = 5,
    # Discuss placing default values in param types
    difficulty: str = Difficulty.EASY.name,
    # Explain to look at the documentation
    category: str = Category.SCIENCE_COMPUTERS.name,
):
    game_state = game.must_get_game(interaction.channel_id)

    # If you start a game in another channel without joining first
    if game_state is None:
        await interaction.response.send_message(embed=game_not_found_embed())
        return

    # In case we call /start twice, we don't want to start the game twice!
    if game_state.is_running:
        embed = discord.Embed(
            title=f"{interaction.user.name}, the game has already started...",
            color=discord.Color.red(),
        )
        await interaction.response.send_message(embed=embed)
        return

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
        (game.Question(question.question, question.choices, question.answer))
        for question in questions
    ]

    # game.questions = [("QUESTION 1", ["True", "False"], "ANSWER1"), ("QUESTION 2", ["True", "False"], "ANSWER2")...]

    embed = get_question_embed(interaction, game_state)
    await interaction.response.send_message(embed=embed)


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
    game_state = game.must_get_game(interaction.channel_id)
    if game_state is None:
        await interaction.response.send_message(embed=game_not_found_embed())
        return

    embeds = []  # we're sending multiple embeds

    if answer.value == game_state.get_current_question().answer:
        game_state.current_q_index += 1

        game_state.scores[interaction.user.name] += 1
        embeds = [
            discord.Embed(
                title=f"**{interaction.user.name} GOT THE QUESTION!**",
                color=discord.Color.green(),
            ),
            # correct answer embed
            get_question_embed(interaction, game_state),
        ]
    else:
        embeds = [discord.Embed(title="**NOPE!**", color=discord.Color.red())]

    await interaction.response.send_message(
        content=f"<@{interaction.user.id}>",
        embeds=embeds,
    )
