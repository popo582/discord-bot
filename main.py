import discord
from discord import app_commands
import random
import json
import os

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# =========================
# 💾 SCORE SYSTEM (SAVED)
# =========================
SCORE_FILE = "scores.json"

def load_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_scores(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f)

scores = load_scores()

# =========================
# 🎲 DICE
# =========================
@tree.command(name="roll", description="Roll a dice (1-6)")
async def roll(interaction: discord.Interaction):
    number = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 You rolled: {number}")

# =========================
# 🪙 COIN
# =========================
@tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 Result: {result}")

# =========================
# ✊ RPS
# =========================
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

# =========================
# ❓ TRIVIA
# =========================
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

        user_id = str(interaction.user.id)
        if user_id not in scores:
            scores[user_id] = 0

        if user_answer == correct_answer:
            scores[user_id] += 1
            save_scores(scores)
            await interaction.followup.send(
                f"✅ Correct! 🎉\n🏆 Your score: {scores[user_id]}"
            )
        else:
            await interaction.followup.send(
                f"❌ Wrong! Answer: {question['a']}\n🏆 Your score: {scores[user_id]}"
            )

    except:
        await interaction.followup.send("⏰ Time's up!")

# =========================
# 🏆 SCORE
# =========================
@tree.command(name="score", description="Check your score")
async def score(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id not in scores:
        scores[user_id] = 0

    await interaction.response.send_message(f"🏆 Your score: {scores[user_id]}")

# =========================
# 🏆 LEADERBOARD
# =========================
@tree.command(name="leaderboard", description="Top players")
async def leaderboard(interaction: discord.Interaction):
    if not scores:
        await interaction.response.send_message("No scores yet!")
        return

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    text = "🏆 Leaderboard:\n"
    for i, (user_id, score) in enumerate(sorted_scores[:5], start=1):
        text += f"{i}. <@{user_id}> - {score}\n"

    await interaction.response.send_message(text)

# =========================
# 🎯 GUESS GAME
# =========================
@tree.command(name="guess", description="Guess a number (1-10)")
async def guess(interaction: discord.Interaction):
    number = random.randint(1, 10)

    await interaction.response.send_message("🎯 Guess a number between 1 and 10!")

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        msg = await client.wait_for("message", timeout=10.0, check=check)
        guess = int(msg.content)

        user_id = str(interaction.user.id)
        if user_id not in scores:
            scores[user_id] = 0

        if guess == number:
            scores[user_id] += 1
            save_scores(scores)
            await interaction.followup.send(f"🎉 Correct! Number was {number}")
        else:
            await interaction.followup.send(f"❌ Wrong! It was {number}")

    except:
        await interaction.followup.send("⏰ Time’s up!")

# =========================
# 🧠 MATH GAME
# =========================
@tree.command(name="math", description="Solve a math question")
async def math(interaction: discord.Interaction):
    a = random.randint(1, 10)
    b = random.randint(1, 10)

    await interaction.response.send_message(f"🧠 What is {a} + {b}?")

    def check(m):
        return m.author == interaction.user and m.channel == interaction.channel

    try:
        msg = await client.wait_for("message", timeout=10.0, check=check)
        answer = int(msg.content)

        user_id = str(interaction.user.id)
        if user_id not in scores:
            scores[user_id] = 0

        if answer == a + b:
            scores[user_id] += 1
            save_scores(scores)
            await interaction.followup.send("✅ Correct!")
        else:
            await interaction.followup.send(f"❌ Wrong! Answer was {a + b}")

    except:
        await interaction.followup.send("⏰ Time’s up!")

# =========================
# 🤖 ASK COMMAND
# =========================
@tree.command(name="ask", description="Ask the bot something")
@app_commands.describe(question="Your question")
async def ask(interaction: discord.Interaction, question: str):
    responses = [
        "Hmm... interesting 🤔",
        "I think yes!",
        "Probably not 😅",
        "Ask again later...",
        "That’s a tough one!"
    ]

    await interaction.response.send_message(random.choice(responses))

# =========================
# 🚀 READY
# =========================
@client.event
async def on_ready():
    guild = discord.Object(id=1439948972411326607)
    await tree.sync(guild=guild)
    print(f"Synced commands to {guild.id}")
    print(f"Logged in as {client.user}")

client.run(TOKEN)
