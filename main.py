import discord
from discord.ext import commands


from dotenv import load_dotenv
from utils import is_env_set, ask_question



from pyopentdb import OpenTDBClient, Category, QuestionType, Difficulty
from typing import Optional


import time

load_dotenv()

TOKEN = is_env_set()

bot = commands.Bot(command_prefix="", intents=discord.Intents.all())

players = {}

@bot.event
async def on_ready():
    # Explain what a bot.tree is, why do we need to do that?
    # Syncs all the slash commands into one big tree
    await bot.tree.sync()

    # When starting a new game we need to clear players all the time
    players.clear()

    embed = discord.Embed(title="Trivia Game Started!", color=discord.Color.brand_green(), description="Join using **/join** to play!")

    channel = bot.get_channel(1109275176807432202)

    await channel.send(embed=embed)

# ------------------------------
# Baseline code (blueprint for slash commands first before logic)
# ------------------------------

@bot.tree.command(name="join")
async def join(interaction: discord.Interaction):

    if interaction.user.name not in players:
        players[interaction.user.name] = 0
        embed = discord.Embed(title=f"{interaction.user.name}, you have joined!", color=discord.Color.blue(), description=f"**{len(players)}** players waiting in line... \nIf **all players** are ready, please type **/start** to begin.")
    else:
        embed = discord.Embed(title=f"{interaction.user.name}, you have already joined!", color=discord.Color.red(), description=f"**{len(players)}** players waiting in line... \nIf **all players** are ready, please type **/start** to begin.")

    await interaction.response.send_message(embed=embed)



# ------------------------------
# Here explain argument types and how to make them optional!
# ------------------------------

@bot.tree.command(name="start")
@discord.app_commands.describe(amount="Amount of questions (DEFAULT - 5)")
@discord.app_commands.choices(difficulty=[
    discord.app_commands.Choice(name="Easy", value=Difficulty.EASY.name),
    discord.app_commands.Choice(name="Medium", value=Difficulty.MEDIUM.name),
    discord.app_commands.Choice(name="Hard", value=Difficulty.HARD.name),
])
@discord.app_commands.describe(timer="Time per question (DEFAULT - 30s)")
@discord.app_commands.choices(category=[
    discord.app_commands.Choice(name="General Knowledge", value=Category.GENERAL_KNOWLEDGE.name),
    discord.app_commands.Choice(name="Computer Science", value=Category.SCIENCE_COMPUTERS.name),
])
async def start(
    interaction: discord.Interaction,
    difficulty: Optional[str] = Difficulty.EASY.name, # Discuss placing default values in param types
    category: Optional[str] = Category.GENERAL_KNOWLEDGE.name, # Dicuss what .name is and why we need to use that (print statements)
    amount: str = "5", 
    timer: str = "15"
): 
    
    # print("Without 'name':", Difficulty.EASY)
    # print("With 'name':", Difficulty.EASY.name, "   --    Difficulty type:", Difficulty[category])

    client=OpenTDBClient()
    questions = client.get_questions(
        amount=int(amount),
        category=Category[category],
        difficulty=Difficulty[difficulty],
        question_type=QuestionType.TRUE_FALSE
    )
    
    # Show what the questions returns!
    """
    [Question(category=<Category.GENERAL_KNOWLEDGE: CategoryItem(id=9, name='General Knowledge', emoji='🧠', aria='brain')>, 
    question_type=<QuestionType.TRUE_FALSE: 'boolean'>, difficulty=<Difficulty.EASY: 'easy'>, 
    question='The Sun rises from the North.', choices=['False', 'True'], answer='False', answer_index=0), 
    Question(category=<Category.GENERAL_KNOWLEDGE: CategoryItem(id=9, name='General Knowledge', emoji='🧠', aria='brain')>....
    """
    print(questions)

    # Explain why we need to send it to a specific channel rather than sending multiple replies
    # Error thrown if we keep doing interaction.response.send_message()
    # discord.app_commands.errors.CommandInvokeError: Command 'start' raised an exception: InteractionResponded: This interaction has already been responded to before
    channel = bot.get_channel(1109275176807432202)
    
    for question in questions:
        await ask_question(channel, question.question, question.choices, discord)

        # What is time.sleep()? What does it do? - Explain that
        # Sleep waits 30 seconds before sending the next question to the channel
        time.sleep(int(timer))


# TODO 
@bot.tree.command(name="answer")
@discord.app_commands.choices(answer=[
    discord.app_commands.Choice(name="T", value="True"),
    discord.app_commands.Choice(name="F", value="False"),
])
async def answer(interaction: discord.Interaction, answer: discord.app_commands.Choice[str]):
    correct_answer = "True"  # Replace with the correct answer if needed
    print(answer.value)
    if answer.value == correct_answer:
        players[interaction.user.name] += 1
        # Sending an ephemeral embed message to the user
        embed = discord.Embed(title="**YOU GOT THE ANSWER RIGHT!**", color=discord.Color.green())
    else:
        # Sending an ephemeral message for incorrect answers
        embed = discord.Embed(title="**YOU GOT THE ANSWER RIGHT!**", color=discord.Color.green())
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
    


# ------------------------------
# Explain here about sorting dictionaries and how it works
# ------------------------------
@bot.tree.command(name="leaderboard")
async def leaderboard(interaction: discord.Interaction):
    
    message_description = ""

    # Briefly explain sorting dictionaries!
    sorted_players = dict(sorted(players.items(), key=lambda x: x[1], reverse=True))

    for player, score in sorted_players.items():
        message_description += f"{player} - {score}\n"

    embed = discord.Embed(title=f"**LEADERBOARD**", color=discord.Color.blue(), description=message_description)

    await interaction.response.send_message(embed=embed)


# ------------------------------
# Please don't forget this
# ------------------------------
bot.run(TOKEN)
