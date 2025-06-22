import discord 
from discord.ext import commands
import settings as s
import database as db

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)

"""WORKINGS FOR FINANCE UPDATING"""

class AmountModal(discord.ui.Modal):
    def __init__(self, trasnactionSource, provider):
        super().__init__(title="Enter Transaction Amount", timeout=300)
        self.transactionSource = trasnactionSource
        self.provider = provider

        self.amount = discord.ui.TextInput(
                label="Amount",
                placeholder="Enter the transaction amount ...",
                style=discord.TextStyle.short,
                required=True
                )

        self.note = discord.ui.TextInput(
                label="Paid Company Name",
                placeholder="Add the name of the company you paid",
                style=discord.TextStyle.paragraph,
                required=True
                )

        self.add_item(self.amount)
        self.add_item(self.note)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = float(self.amount.value)
            response = (
                f"✅ Transaction Recorded!\n"
                f"**Source:** {self.transactionSource}\n"
                f"**Is Necessity:** {self.provider}\n"
                f"**Paid To:** {self.note.value}\n"
                f"**Amount:** {amount:.2f}\n"
            )
            
            await interaction.response.send_message(response, ephemeral=True)
            
            db.save_TransactionData(
                self.transactionSource,
                self.provider,
                amount,
                self.note.value
            )
            
        except ValueError:
            error_msg = "⚠️ Please enter a valid numeric amount (e.g., 100.00)"
            await interaction.response.send_message(error_msg, ephemeral=True)
        except Exception as e:
            error_msg = f"❌ An error occurred: {str(e)}"
            await interaction.response.send_message(error_msg, ephemeral=True)
            print(f"Modal submission error: {e}")

class FirstFinDropdown(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.select(
            placeholder="Choose the transaction source.",
            options=[
                discord.SelectOption(label=values, value=values)
                for _, values in enumerate(db.get_DiscordSources())
                ]
            )


    async def first_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.transactionSource = select.values[0]
        await interaction.response.send_message(
                "Now choose was this necessary?",
                view=SecondFinDropdown(self.transactionSource),
                ephemeral=True
                )

class SecondFinDropdown(discord.ui.View):
    def __init__(self, transactionSource):
        super().__init__()
        self.transactionSource = transactionSource

    @discord.ui.select(
            placeholder="Was this a necessity?",
            options=[
                discord.SelectOption(label="Yes, Necessity", value="1"),
                discord.SelectOption(label="No, Not Necessity", value="0")
                ]
            )

    async def second_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        provider = select.values[0]
        await interaction.response.send_modal(
                AmountModal(self.transactionSource, provider)
                )


class SavingsAmount(discord.ui.Modal):
    def __init__(self, savingscredited, isnecessity):
        super().__init__(title="Enter the Amount Transfered", timeout=300)
        self.savingscredited = savingscredited
        self.isnecessity = isnecessity

        self.amount = discord.ui.TextInput(
                label="Amount",
                placeholder="Enter the amount transfered ...",
                style=discord.TextStyle.short,
                required=True
                )

        self.add_item(self.amount)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            amount = float(self.amount.value)
            response = (
                f"✅ Transaction Recorded!\n"
                f"**Money IN or OUT:** {self.savingscredited}\n"
                f"**Is Necessity:** {self.isnecessity}\n"
                f"**Amount:** {amount:.2f}\n"
            )
            
            await interaction.response.send_message(response, ephemeral=True)

            isnecessity = int(self.isnecessity)
            savingscredited = int(self.savingscredited)
            db.save_SavingsData(
                    savingscredited,
                    isnecessity,
                    amount
                    )

        except ValueError:
            error_msg = ""
            await interaction.response.send_message(error_msg, ephemeral=True)
        except Exception as e:
            error_msg = ""
            await interaction.response.send_message(error_msg, ephemeral=True)
            print(f"Modal submission error: {e}")

class SavingsDropdown(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.select(
            placeholder="Transfer IN or OUT of savings?",
            options=[
                discord.SelectOption(label="OUT", value="0"),
                discord.SelectOption(label="IN", value="1")
                ]
            )

    async def first_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        savingscredited = select.values[0]
        await interaction.response.send_message(
                content="Was this a necessity?",
                view=SavingsNecessity(savingscredited),
                ephemeral=True
                )

class SavingsNecessity(discord.ui.View):
    def __init__(self, savingscredited):
        super().__init__()
        self.savingscredited = savingscredited

    @discord.ui.select(
            placeholder="Was this a necessity?",
            options=[
                discord.SelectOption(label="Yes, Necessity", value="1"),
                discord.SelectOption(label="No, Not Necessity", value="0")
                ]
            )

    async def second_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        isnecessity = select.values[0]
        await interaction.response.send_modal(
                SavingsAmount(self.savingscredited, isnecessity)
                )




"""WORKINGS FOR FINANCE STATUS CHECKING"""

#START HERE




"""WORKINGS FOR HABIT TRACKING"""

#START HERE




"""WORKINGS FOR HABIT STATUS CHECKING"""

#START HERE





@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready and waiting!")
    channel = bot.get_channel(s.GENERAL_ID)
    if channel:
        await channel.send("Hello")
    else:
        print("Cannot find the channel")

@bot.event 
async def on_message(message):
    if message.author == bot.user:
        return

    #channel_id = message.channel.id

    msg = message.content
    if msg[0] == "!": 
        await bot.process_commands(message)


@bot.command()
async def finance(ctx):
    view=FirstFinDropdown()
    await ctx.send("**FINANCE UPDATE IN PROGRESS!**", view=view)

@bot.command()
async def status(ctx):
    channel_id = ctx.channel.id
    finance_channel = s.FINANCE_ID

    if channel_id == finance_channel:
        #CHECK FINANCE STATUS IN FINANCE CHANNEL
        await ctx.send("This is the finance channel")

@bot.command()
async def savings(ctx):
    view=SavingsDropdown()
    await ctx.send("***SAVINGS UPDATE IN PROGRESS!**", view=view)

if __name__ == "__main__":
    token=s.DISCORD_BOT_TOKEN
    bot.run(str(token))
