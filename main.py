# Made By Lolpro (LolproDoesStuff on GitHub)

import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import os

TOKEN = "(your bot token)"

GUILD_ID = (your guild's ID)
CHANNEL_ID = (your channel's ID)
ROLE_ID = (your role's ID)
PASSCODE = "(passcode)"

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


class PasscodeButton(Button):
    def __init__(self, role):
        super().__init__(label="Start Verification", style=discord.ButtonStyle.primary, custom_id="passcode_button")
        self.role = role

    async def callback(self, interaction: discord.Interaction):
        try:
            dm_channel = await interaction.user.create_dm()
            await dm_channel.send("Please enter the passcode:")

            def check(msg):
                return msg.author == interaction.user and isinstance(msg.channel, discord.DMChannel)

            response = await bot.wait_for("message", check=check, timeout=60.0)

            if response.content == PASSCODE:
                guild = interaction.guild
                member = guild.get_member(interaction.user.id)
                if not member:
                    await dm_channel.send("❌ Could not find your member information in the server.")
                    return
                await member.add_roles(self.role)
                await dm_channel.send("✅ Passcode correct, have a good stay in the server.")
            else:
                await dm_channel.send("❌ Incorrect passcode. Restart the verification process.")
        except Exception as e:
            print(f"Error: {e}")
            await interaction.response.send_message(
                "❌ There was an error sending the DM. Please make sure that your DMs are open.",
                ephemeral=True,
            )


class PersistentView(View):
    def __init__(self, role):
        super().__init__(timeout=None)
        self.add_item(PasscodeButton(role))


@bot.command()
async def setup(ctx):
    print(f"Command used by: {ctx.author}")
    print(f"Guild: {ctx.guild.id if ctx.guild else None}")
    print(f"Channel: {ctx.channel.id if ctx.channel else None}")

    if ctx.guild.id != GUILD_ID or ctx.channel.id != CHANNEL_ID:
        await ctx.send("nice try hehe.")
        return

    guild = ctx.guild
    role = guild.get_role(ROLE_ID)

    if not role:
        await ctx.send("❌ Internal Error, contact the server admin. (Role not found)")
        return

    view = PersistentView(role)

    embed = discord.Embed(
        title="Verification",
        description="Click the button below to begin the verification process.",
        color=discord.Color.red(),
    )

    await ctx.send(embed=embed, view=view)
    print("Message sent successfully")


@bot.event
async def on_message(message):
    if message.guild and message.guild.id == GUILD_ID and message.channel.id == CHANNEL_ID:
        await bot.process_commands(message)


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    guild = bot.get_guild(GUILD_ID)
    if guild:
        role = guild.get_role(ROLE_ID)
        if role:
            bot.add_view(PersistentView(role))


bot.run(TOKEN)
