import discord 
from discord.ext import commands
import settings as s
import database as db
import datetime 

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
            isnecessity = int(self.provider)
            response = (
                f"✅ Transaction Recorded!\n"
                f"**Source:** {self.transactionSource}\n"
                f"**Is Necessity:** {isnecessity}\n"
                f"**Paid To:** {self.note.value}\n"
                f"**Amount:** {amount:.2f}\n"
            )
            
            await interaction.response.send_message(response, ephemeral=True)
            
            db.save_TransactionData(
                self.transactionSource,
                isnecessity,
                self.note.value,
                amount
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

"""
Problem: Discord only allows up to 5 items per modal
Fix: Call additional modal after first 5 have been completed
"""
class TransactionSourceUpdate(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Please complete all the fields", timeout=300)

        self.TransactionName = discord.ui.TextInput(
                label="Transaction Name",
                placeholder="e.g. Card Payment",
                style=discord.TextStyle.short,
                required=True
                )
        self.InfoSource = discord.ui.TextInput(
                label="Where will the transaction information come from?",
                placeholder="e.g. Discord",
                style=discord.TextStyle.short,
                required=True
                )
        self.TransactionNature = discord.ui.TextInput(
                label="What is the nature of the transaction?",
                placeholder="e.g. Loan",
                style=discord.TextStyle.short,
                required=True
                )
        self.IsCreditor = discord.ui.Select(
                placeholder="Is loan repayment?",
                options=[
                    discord.SelectOption(label="True", value="1"),
                    discord.SelectOption(label="False", value="0")
                    ],
                max_values=1, min_values=1
                )
        self.CompanyName = discord.ui.TextInput(
                label="What is the name of the company you are paying?",
                placeholder="e.g. Sportsmans Warehouse",
                style=discord.TextStyle.short,
                required=True
                )
        self.InterestRate = discord.ui.TextInput(
                label="What is the interest rate on repayment?",
                placeholder="e.g. 0.1075 -> 10,75%",
                style=discord.TextStyle.short,
                required=False
                )
        self.DateInterestRateUpdated = datetime.datetime.now()
        self.ActualContractBalance = discord.ui.TextInput(
                label="What is the total value of the contract?",
                placeholder="e.g. Buying = R1000 ContractValue = R1000 + InterestOverTime",
                style=discord.TextStyle.short,
                required=False
                )
        self.CurrentMonthInstalment = discord.ui.TextInput(
                label="How much is the Current Month payment?",
                placeholder="e.g. 540",
                style=discord.TextStyle.short,
                required=False
                )
        self.ExpectedNextPayment = discord.ui.TextInput(
                label="How much is the Next Payment",
                placeholder="e.g. 450",
                style=discord.TextStyle.short,
                required=False
                )
        self.InterestAmount = discord.ui.TextInput(
                label="What is the total interest to repay?",
                placeholder="e.g. R1234",
                style=discord.TextStyle.short,
                required=False
                )
        self.DateAmountUpdated = datetime.datetime.now()
        self.RemainingInstalments = discord.ui.TextInput(
                label="How long do you still need to pay?",
                placeholder="e.g. 60 instalments",
                style=discord.TextStyle.short,
                required=False
                )
        self.IsCurrentlyPaying = discord.ui.Select(
                options=[
                    discord.SelectOption(label="True", value="1"),
                    discord.SelectOption(label="False", value="0")
                         ],
                max_values=1, min_values=0
                )
        self.DatePaymentsEnd = discord.ui.TextInput(
                label="When do you stop paying?",
                placeholder="2099-01-01",
                style=discord.TextStyle.short,
                required=False
                )


        self.add_item(self.TransactionName)
        self.add_item(self.InfoSource)
        self.add_item(self.TransactionNature)
        self.add_item(self.IsCreditor)
        self.add_item(self.CompanyName)
        self.add_item(self.InterestRate)
        self.add_item(self.ActualContractBalance)
        self.add_item(self.CurrentMonthInstalment)
        self.add_item(self.ExpectedNextPayment)
        self.add_item(self.InterestAmount)
        self.add_item(self.RemainingInstalments)
        self.add_item(self.IsCurrentlyPaying)
        self.add_item(self.DatePaymentsEnd)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            IsCreditor = int(self.IsCreditor.values[0]) if self.IsCreditor.values else 0
            InterestRate = float(self.InterestRate.value) if self.InterestRate.value else 0.0
            ActualContractBalance = float(self.ActualContractBalance.value) if self.ActualContractBalance.value else 0.0
            CurrentMonthInstalment = float(self.CurrentMonthInstalment.value) if self.CurrentMonthInstalment.value else 0.0
            ExpectedNextPayment = float(self.ExpectedNextPayment.value) if self.ExpectedNextPayment.value else 0.0
            InterestAmount = float(self.InterestAmount.value) if self.InterestAmount.value else 0.0
            RemainingInstalments = int(self.RemainingInstalments.value) if self.RemainingInstalments.value else 0
            IsCurrentlyPaying = int(self.IsCurrentlyPaying.values[0]) if self.IsCurrentlyPaying.values else 0
            DatePaymentsEnd = datetime.datetime.strptime(self.DatePaymentsEnd.value, '%Y-%m-%d') if self.DatePaymentsEnd.value else None
    
            response = (
                f"✅ Transaction Source Updated!\n"
                f"**Transaction Name:** {self.TransactionName.value}\n"
                f"**Info Source:** {self.InfoSource.value}\n"
                f"**Transaction Nature:** {self.TransactionNature.value}\n"
                f"**Is Creditor:** {'Yes' if IsCreditor else 'No'}\n"
                f"**Company Name:** {self.CompanyName.value}\n"
                f"**Interest Rate:** {InterestRate:.2%}\n"
                f"**Contract Balance:** R{ActualContractBalance:,.2f}\n"
                f"**Current Installment:** R{CurrentMonthInstalment:,.2f}\n"
                f"**Next Payment:** R{ExpectedNextPayment:,.2f}\n"
                f"**Total Interest:** R{InterestAmount:,.2f}\n"
                f"**Remaining Installments:** {RemainingInstalments}\n"
                f"**Currently Paying:** {'Yes' if IsCurrentlyPaying else 'No'}\n"
                f"**Payments End Date:** {DatePaymentsEnd.strftime('%Y-%m-%d') if DatePaymentsEnd else 'Not specified'}"
            )
            
            await interaction.response.send_message(response, ephemeral=True)
    
            db.update_TransactionSource(
                TransactionName=self.TransactionName.value,
                InfoSource=self.InfoSource.value,
                TransactionNature=self.TransactionNature.value,
                IsCreditor=IsCreditor,
                CompanyName=self.CompanyName.value,
                InterestRate=InterestRate,
                DateInterestRateUpdated=datetime.datetime.now(),
                ActualContractBalance=ActualContractBalance,
                CurrentMonthInstalment=CurrentMonthInstalment,
                ExpectedNextPayment=ExpectedNextPayment,
                InterestAmount=InterestAmount,
                DateAmountUpdated=datetime.datetime.now(),
                RemainingInstalments=RemainingInstalments,
                IsCurrentlyPaying=IsCurrentlyPaying,
                DatePaymentsEnd=DatePaymentsEnd
            )
    
        except ValueError as e:
            error_msg = f"⚠️ Invalid input format: {str(e)}"
            await interaction.response.send_message(error_msg, ephemeral=True)
        except Exception as e:
            error_msg = f"❌ An error occurred while saving: {str(e)}"
            await interaction.response.send_message(error_msg, ephemeral=True)
            print(f"Modal submission error: {e}")





"""WORKINGS FOR FINANCE STATUS CHECKING"""

#START HERE




"""WORKINGS FOR HABIT TRACKING"""

#START HERE




"""WORKINGS FOR HABIT STATUS CHECKING"""

#START HERE




"""ESKOM LOAD SHEDDING UPDATES"""

#START HERE




@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready and waiting!")
    channel = bot.get_channel(s.GIT_ID)
    dateTime = datetime.datetime.now()
    if channel:
        await channel.send(f"git pulled on {dateTime}")
    else:
        print("Cannot find the channel")

@bot.event 
async def on_message(message):
    if message.author == bot.user:
        return

    msg = message.content
    command_list = [
            "!transact",
            "!t",
            "!savings",
            "!save",
            "!status",
            "!s"
            ]
    command_trg = any(msg.startswith(command) for command in command_list)

    if command_trg:
        channel_id = message.channel.id
        finance_channel = s.FINANCE_ID
        if channel_id == finance_channel:
            await bot.process_commands(message)
        else:
            channel = message.channel
            channel_name = message.channel.name
            await channel.send(f"🚫 Oops! You're trying to run finance commands in **{channel_name}**. Please head over to the 💰 **#finance** channel to use finance commands.")



@bot.command(name="transact", aliases=["t"])
async def transact(ctx: commands.Context, args: str=None):
    if args and "--" in args:
        additional_command = args.split("--")[1].strip()

        if additional_command == "new":
            await ctx.send("Please give additional information e.g. update-ts -> update transaction sources")
        
        elif additional_command.startswith("new-ts"):
            class ModalButtonView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=120)
                
                @discord.ui.button(label="Open Transaction Form", 
                                 style=discord.ButtonStyle.primary, 
                                 emoji="📝",
                                 row=0)
                async def modal_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.send_modal(TransactionSourceUpdate())
            
            embed = discord.Embed(
                title="New Transaction Source",
                description="Click the button below to add a New Transaction Source:",
                color=discord.Color.blue()
            )
            view = ModalButtonView()
            await ctx.send(embed=embed, view=view)

        else:
            view=FirstFinDropdown()
            await ctx.send("**FINANCE UPDATE IN PROGRESS!**", view=view)
    else:
        view = FirstFinDropdown()
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
