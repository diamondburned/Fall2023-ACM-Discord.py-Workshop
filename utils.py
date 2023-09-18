import os

def is_env_set() -> str:
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN is None:
        raise EnvironmentError("'DISCORD_TOKEN' is not set!")
    
    return TOKEN



async def ask_question(channel, question, choices, discord):

    # First put choices on its own before doing .join (CHOICES)
    formatted_choices = ", ".join(choices)

    message = f"**{question}**\n**Choices**: {formatted_choices}"
    embed = discord.Embed(title=f"**NEW QUESTION**", color=discord.Color.blue(), description=message)
    
    await channel.send(embed=embed)
   
