# Made By Lolpro (LolproDoesStuff on GitHub)

import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import os

TOKEN = "(your bot token)"

GUILD_ID = "(your guild id)"
CHANNEL_ID = "(your channel id)"
ROLE_ID = "(your role id)"
PASSCODE = "(your passcode)"

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
        print(f"Button clicked by {interaction.user} (ID: {interaction.user.id})")

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
                    print(f"Failed to assign role to {interaction.user} - Member not found in guild.")
                    return

                await member.add_roles(self.role)
                await dm_channel.send("✅ Passcode correct, have a good stay in the server.")
                print(f"✅ {interaction.user} successfully verified and assigned the role.")
            else:
                await dm_channel.send("❌ Incorrect passcode. Restart the verification process.")
                print(f"❌ {interaction.user} failed verification with incorrect passcode.")
        except Exception as e:
            print(f"Error processing verification for {interaction.user}: {e}")
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
        print(f"❌ Unauthorized setup attempt by {ctx.author} in guild {ctx.guild.id}, channel {ctx.channel.id}")
        return

    guild = ctx.guild
    role = guild.get_role(ROLE_ID)

    if not role:
        await ctx.send("❌ Internal Error, contact the server admin. (Role not found)")
        print(f"❌ Role with ID {ROLE_ID} not found in guild {ctx.guild.id}")
        return

    view = PersistentView(role)

    embed = discord.Embed(
        title="Verification",
        description="Click the button below to begin the verification process.",
        color=discord.Color.red(),
    )

    await ctx.send(embed=embed, view=view)
    print("✅ Verification setup message sent successfully.")


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
    print(f"Bot is ready and listening in Guild ID: {GUILD_ID}, Channel ID: {CHANNEL_ID}")


bot.run(TOKEN)
