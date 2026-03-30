import discord
from discord import app_commands
from discord.ext import commands
import os
import random  # ✅ missing import
from dotenv import load_dotenv

load_dotenv()  # loads .env locally if you have it

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # make sure .env or Railway variable matches

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

scores = {}

# ---- Commands ----
@tree.command(name="roll", description="Roll a dice (1-6)")
async def roll(interaction: discord.Interaction):
    number = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 You rolled: {number}")

@tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 Result: {result}")

@tree.command(name="rps", description="Play Rock Paper Scissors")
@app_commands.describe(choice="rock, paper, or scissors")
async def rps(interaction: discord.Interaction, choice: str):
    bot_choice = random.choice(["rock", "paper", "scissors"])
    choice = choice.lower()

    if choice not in ["rock", "paper", "scissors"]:
        await interaction.response.send_message("❌ Choose rock, paper, or scissors!")
        return

    if choice == bot_choice:
        result = "It's a tie!"
    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "paper" and bot_choice == "rock") or \
         (choice == "scissors" and bot_choice == "paper"):
        result = "You win! 🎉"
    else:
        result = "You lose 😢"

    await interaction.response.send_message(
        f"You chose **{choice}**\nBot chose **{bot_choice}**\n👉 {result}"
    )

# Trivia
questions = [
    {"q": "What is the capital of India?", "a": "delhi"},
    {"q": "2 + 2 = ?", "a": "4"},
    {"q": "Which planet is known as the Red Planet?", "a": "mars"}
]

@tree.command(name="trivia", description="Answer a trivia question")
async def trivia(interaction: discord.Interaction):
    question = random.choice(questions)
    await interaction.response.send_message(f"❓ {question['q']}")

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        msg = await client.wait_for("message", timeout=15.0, check=check)
        user_answer = msg.content.lower().strip()
        correct_answer = question["a"].lower().strip()
        user_id = interaction.user.id

        if user_id not in scores:
            scores[user_id] = 0

        if user_answer == correct_answer:
            scores[user_id] += 1
            await interaction.followup.send(f"✅ Correct! 🎉\n🏆 Your score: {scores[user_id]}")
        else:
            await interaction.followup.send(f"❌ Wrong! Answer: {question['a']}\n🏆 Your score: {scores[user_id]}")

    except:
        await interaction.followup.send("⏰ Time's up!")

@tree.command(name="score", description="Check your score")
async def score(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id not in scores:
        scores[user_id] = 0
    await interaction.response.send_message(f"🏆 Your score: {scores[user_id]}")

# On ready
@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

# Run bot
client.run(TOKEN)
