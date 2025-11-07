import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Verification types
VERIFICATION_TYPES = {
    "one_click": "One-Click Verification",
    "captcha": "Captcha Verification", 
    "math": "Math Verification",
    "reaction": "Reaction Verification"
}

# Default settings
verification_settings = {
    "enabled": True,
    "type": "one_click",
    "title": "Verification Required",
    "description": "Please verify yourself to access the server",
    "send_method": "dm"  # or "channel"
}

def load_settings():
    """Load settings from environment variables"""
    global verification_settings
    verification_settings["enabled"] = os.getenv("VERIFICATION_ENABLED", "true").lower() == "true"
    verification_settings["type"] = os.getenv("VERIFICATION_TYPE", "one_click")
    verification_settings["title"] = os.getenv("VERIFICATION_TITLE", "Verification Required")
    verification_settings["description"] = os.getenv("VERIFICATION_DESCRIPTION", "Please verify yourself to access the server")
    verification_settings["send_method"] = os.getenv("VERIFICATION_SEND_METHOD", "dm")

@bot.event
async def on_ready():
    print("✅ Verification bot online and running")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="verification", description="Setup verification for the server")
async def verification_setup(interaction: discord.Interaction):
    # Only allow administrators to use this command
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
    
    # Create embed for verification setup
    embed = discord.Embed(
        title="Verification Setup",
        description="Configure verification settings for your server",
        color=0x00ff00
    )
    
    # Add current settings to embed
    embed.add_field(name="Enabled", value="Yes" if verification_settings["enabled"] else "No", inline=False)
    embed.add_field(name="Type", value=VERIFICATION_TYPES.get(verification_settings["type"], "Unknown"), inline=False)
    embed.add_field(name="Title", value=verification_settings["title"], inline=False)
    embed.add_field(name="Description", value=verification_settings["description"], inline=False)
    embed.add_field(name="Send Method", value=verification_settings["send_method"].upper(), inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_member_join(member):
    """Handle new member joins"""
    if not verification_settings["enabled"]:
        return
    
    try:
        if verification_settings["send_method"] == "dm":
            # Send verification via DM
            await send_verification_dm(member)
        else:
            # Send verification to channel
            channel = discord.utils.get(member.guild.channels, name="verification")
            if channel:
                await send_verification_channel(channel, member)
    except Exception as e:
        print(f"Error sending verification: {e}")

async def send_verification_dm(member):
    """Send verification message via DM"""
    try:
        embed = discord.Embed(
            title=verification_settings["title"],
            description=verification_settings["description"],
            color=0x00ff00
        )
        
        if verification_settings["type"] == "one_click":
            view = OneClickVerification(member)
        elif verification_settings["type"] == "captcha":
            view = CaptchaVerification(member)
        elif verification_settings["type"] == "math":
            view = MathVerification(member)
        elif verification_settings["type"] == "reaction":
            view = ReactionVerification(member)
        else:
            view = OneClickVerification(member)
            
        await member.send(embed=embed, view=view)
    except Exception as e:
        print(f"Error sending DM to {member.name}: {e}")

async def send_verification_channel(channel, member):
    """Send verification message to channel"""
    try:
        embed = discord.Embed(
            title=verification_settings["title"],
            description=verification_settings["description"],
            color=0x00ff00
        )
        
        if verification_settings["type"] == "one_click":
            view = OneClickVerification(member)
        elif verification_settings["type"] == "captcha":
            view = CaptchaVerification(member)
        elif verification_settings["type"] == "math":
            view = MathVerification(member)
        elif verification_settings["type"] == "reaction":
            view = ReactionVerification(member)
        else:
            view = OneClickVerification(member)
            
        await channel.send(embed=embed, view=view)
    except Exception as e:
        print(f"Error sending message to channel: {e}")

# Verification Views
class OneClickVerification(discord.ui.View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success)
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Add verified role
        role = discord.utils.get(interaction.guild.roles, name="Verified")
        if not role:
            try:
                role = await interaction.guild.create_role(name="Verified")
            except Exception as e:
                await interaction.response.send_message("Error creating Verified role. Please contact an administrator.", ephemeral=True)
                return
        
        try:
            await self.member.add_roles(role)
            await interaction.response.send_message("✅ You have been verified!", ephemeral=True)
            # Disable the button after verification
            button.disabled = True
            await interaction.message.edit(view=self)
        except Exception as e:
            await interaction.response.send_message("Error assigning role. Please contact an administrator.", ephemeral=True)

class CaptchaVerification(discord.ui.View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member
        self.captcha = "A1B2"
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.primary)
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Modal for captcha input
        modal = CaptchaModal(self.member, self.captcha)
        await interaction.response.send_modal(modal)

class CaptchaModal(discord.ui.Modal, title="Captcha Verification"):
    def __init__(self, member, captcha):
        super().__init__()
        self.member = member
        self.captcha = captcha
    
    captcha_input = discord.ui.TextInput(
        label="Enter Captcha",
        placeholder="Enter the captcha code...",
        required=True,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.captcha_input.value.upper() == self.captcha:
            # Add verified role
            role = discord.utils.get(interaction.guild.roles, name="Verified")
            if not role:
                try:
                    role = await interaction.guild.create_role(name="Verified")
                except Exception as e:
                    await interaction.response.send_message("Error creating Verified role. Please contact an administrator.", ephemeral=True)
                    return
            
            try:
                await self.member.add_roles(role)
                await interaction.response.send_message("✅ You have been verified!", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message("Error assigning role. Please contact an administrator.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Incorrect captcha. Please try again.", ephemeral=True)

class MathVerification(discord.ui.View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member
        self.answer = 15  # 10 + 5
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.primary)
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Modal for math input
        modal = MathModal(self.member, self.answer)
        await interaction.response.send_modal(modal)

class MathModal(discord.ui.Modal, title="Math Verification"):
    def __init__(self, member, answer):
        super().__init__()
        self.member = member
        self.answer = answer
    
    math_input = discord.ui.TextInput(
        label="Solve: 10 + 5 = ?",
        placeholder="Enter the answer...",
        required=True,
        max_length=5
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            if int(self.math_input.value) == self.answer:
                # Add verified role
                role = discord.utils.get(interaction.guild.roles, name="Verified")
                if not role:
                    try:
                        role = await interaction.guild.create_role(name="Verified")
                    except Exception as e:
                        await interaction.response.send_message("Error creating Verified role. Please contact an administrator.", ephemeral=True)
                        return
                
                try:
                    await self.member.add_roles(role)
                    await interaction.response.send_message("✅ You have been verified!", ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message("Error assigning role. Please contact an administrator.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Incorrect answer. Please try again.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Please enter a valid number.", ephemeral=True)

class ReactionVerification(discord.ui.View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member
    
    @discord.ui.button(label="React to Verify", style=discord.ButtonStyle.primary, emoji="✅")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Add verified role
        role = discord.utils.get(interaction.guild.roles, name="Verified")
        if not role:
            try:
                role = await interaction.guild.create_role(name="Verified")
            except Exception as e:
                await interaction.response.send_message("Error creating Verified role. Please contact an administrator.", ephemeral=True)
                return
        
        try:
            await self.member.add_roles(role)
            await interaction.response.send_message("✅ You have been verified!", ephemeral=True)
            # Disable the button after verification
            button.disabled = True
            await interaction.message.edit(view=self)
        except Exception as e:
            await interaction.response.send_message("Error assigning role. Please contact an administrator.", ephemeral=True)

# Load settings on startup
load_settings()

# Run the bot
if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("ERROR: DISCORD_TOKEN not found in environment variables")
    else:
        bot.run(token)