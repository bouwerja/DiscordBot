import discord 
from discord.ext import commands
import settings as s
import database as db
import datetime
from database_management import StatusInsert, RestartErrorCheck

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
            
            sources_name = self.transactionSource
            sources_id = 0
            for key, value in db.get_DiscordSources().items():
                if value == sources_name:
                    sources_id = int(key)

            db.save_TransactionData(
                sources_id,
                sources_name,
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
                for _, values in db.get_DiscordSources().items()
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

"""NEW TRANSACTION SOURCE [[BROKEN]]"""
transaction_data = {}

class TransactionSourceUpdateFirst(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Complete All", timeout=300)

        self.TransactionName = discord.ui.TextInput(
                label="Transaction Name",
                placeholder="e.g. Card Payment",
                style=discord.TextStyle.short,
                required=True
                )
        self.InfoSource = discord.ui.TextInput(
                label="Transaction Info Source",
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
        self.IsCreditor = discord.ui.TextInput(
                label="Is this a Loan Repayment",
                placeholder="True or False",
                style=discord.TextStyle.short,
                required=True
                )
        self.CompanyName = discord.ui.TextInput(
                label="Crediting Company Name",
                placeholder="e.g. Sportsmans Warehouse",
                style=discord.TextStyle.short,
                required=True
                )


        self.add_item(self.TransactionName)
        self.add_item(self.InfoSource)
        self.add_item(self.TransactionNature)
        self.add_item(self.IsCreditor)
        self.add_item(self.CompanyName)

    async def on_submit(self, interaction: discord.Interaction):
        is_creditor = 1 if str(self.IsCreditor.value).lower() == "true" else 0
        transaction_data.update({
            'TransactionName' : str(self.TransactionName.value),
            'InfoSource' : str(self.InfoSource.value), 
            'TransactionNature' : str(self.TransactionNature.value),
            'IsCreditor' : is_creditor,
            'CompanyName' : str(self.CompanyName.value)
        })
        await interaction.response.send_message("✅ Basic details saved!", ephemeral=True)

class TransactionSourceUpdateSecond(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Complete All", timeout=300)

        self.InterestRate = discord.ui.TextInput(
                label="What is the interest rate on repayment?",
                placeholder="e.g. 0.1075 -> 10,75%",
                style=discord.TextStyle.short,
                required=False
                )
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

        self.add_item(self.InterestRate)
        self.add_item(self.ActualContractBalance)
        self.add_item(self.CurrentMonthInstalment)
        self.add_item(self.ExpectedNextPayment)
        self.add_item(self.InterestAmount)

        async def on_submit(self, interaction: discord.Interaction):
            transaction_data.update({
                'InterestRate' : float(self.InterestRate.value),
                'ActualContractBalance' : float(self.ActualContractBalance.value),
                'CurrentMonthInstalment' : int(self.CurrentMonthInstalment.value),
                'ExpectedNextPayment' : float(self.ExpectedNextPayment.value),
                'InterestAmount' : float(self.InterestAmount.value)
            })
            
            await interaction.response.send_message("📊 Payment Details saved!", ephemeral=True)
            
class TransactionSourceUpdateThird(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Complete All", timeout=300)

        self.RemainingInstalments = discord.ui.TextInput(
                label="How long do you still need to pay?",
                placeholder="e.g. 60 instalments",
                style=discord.TextStyle.short,
                required=False
                )
        self.IsCurrentlyPaying = discord.ui.TextInput(
                label="Is this a current reacurring payment?",
                placeholder="True or False",
                style=discord.TextStyle.short,
                required=True
                )
        self.DatePaymentsEnd = discord.ui.TextInput(
                label="When do you stop paying?",
                placeholder="2099-01-01",
                style=discord.TextStyle.short,
                required=False
                )
        self.add_item(self.RemainingInstalments)
        self.add_item(self.IsCurrentlyPaying)
        self.add_item(self.DatePaymentsEnd)

        async def on_submit(self, interaction: discord.Interaction):
            transaction_data.update({
                'RemainingInstalments': int(self.RemainingInstalments.value),
                'IsCurrentlyPaying' : int(self.IsCurrentlyPaying.value),
                'DatePaymentsEnd' : datetime.datetime.strftime(self.DatePaymentsEnd.value, "%Y/%m/%d")
            })

            response = (
                f"✅ Transaction Source Updated!\n"
                f"**Transaction Name:** {transaction_data['TransactionName']}\n"
                f"**Info Source:** {transaction_data['InfoSource']}\n"
                f"**Transaction Nature:** {transaction_data['TransactionNature']}\n"
                f"**Is Creditor:** {transaction_data['IsCreditor']}\n"
                f"**Company Name:** {transaction_data['CompanyName']}\n"
                f"**Interest Rate:** {transaction_data['InterestRate']:.2%}\n"
                f"**Contract Balance:** R{transaction_data['ActualContractBalance']:,.2f}\n"
                f"**Current Installment:** R{transaction_data['CurrentMonthInstalment']:,.2f}\n"
                f"**Next Payment:** R{transaction_data['ExpectedNextPayment']:,.2f}\n"
                f"**Total Interest:** R{transaction_data['InterestAmount']:,.2f}\n"
                f"**Remaining Installments:** {transaction_data['RemainingInstalments']}\n"
                f"**Currently Paying:** {transaction_data['IsCurrentlyPaying']}\n"
                f"**Payments End Date:** {transaction_data['DatePaymentEnd']}"
            )
            
            await interaction.response.send_message(response, ephemeral=True)

class WriteTransactionSource(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        
    
    async def handle_submit(self, interaction: discord.Interaction):
        try:
            IsCreditor = int(transaction_data.get('IsCreditor', 0))
            InterestRate = float(transaction_data.get('InterestRate', 0.0))
            ActualContractBalance = float(transaction_data.get('ActualContractBalance', 0.0))
            CurrentMonthInstalment = float(transaction_data.get('CurrentMonthInstalment', 0.0))
            ExpectedNextPayment = float(transaction_data.get('ExpectedNextPayment', 0.0))
            InterestAmount = float(transaction_data.get('InterestAmount', 0.0))
            RemainingInstalments = int(transaction_data.get('RemainingInstalments', 0))
            IsCurrentlyPaying = int(transaction_data.get('IsCurrentlyPaying', 0))
            DatePaymentsEnd = transaction_data.get('DatePaymentsEnd')
            
            db.update_TransactionSource(
                TransactionName=transaction_data['TransactionName'],
                InfoSource=transaction_data['InfoSource'],
                TransactionNature=transaction_data['TransactionNature'],
                IsCreditor=IsCreditor,
                CompanyName=transaction_data['CompanyName'],
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
            
            await interaction.response.send_message("💸 New Transaction Source Created", ephemeral=True)
            transaction_data.clear()
            
        except KeyError as e:
            await interaction.response.send_message(
                f"❌ Missing data: {str(e)}",
                ephemeral=True
            )
        except ValueError as e:
            await interaction.response.send_message(
                f"❌ Invalid data format: {str(e)}", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Database error: {str(e)}",
                ephemeral=True
            )

"""WORKINGS FOR FINANCE STATUS CHECKING"""

#START HERE




"""WORKINGS FOR HABIT TRACKING"""

#START HERE




"""WORKINGS FOR HABIT STATUS CHECKING"""

#START HERE




"""ESKOM LOAD SHEDDING UPDATES"""

#START HERE




"""GYM TRACKER"""

#START HERE




"""RASPBERRYPI INFORMAION VIEW"""

#START HERE




"""REMINDER FUNCTION"""

#START HERE




"""REPORT FUNCTION"""

#START HERE
#   OPTION FOR FINANCIAL REPORT
#   OPTION FOR HABIT REPORT
#   OPTION FOR GENERAL REPORT COMBINING ALL




@bot.event
async def on_ready():
    status_channel = bot.get_channel(s.STATUS_ID)
    restart_time, err = RestartErrorCheck()    #Check previous status log
    if err:
        await status_channel.send(f"Bot failed to restart\nLast restart time {restart_time}")
    else:
        await status_channel.send(f"Bot restarted on {restart_time}")
    StatusInsert()    #INSERT current status log

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
            
            embed = discord.Embed(
                title="New Transaction Source",
                description="Click the button below to add a New Transaction Source:",
                color=discord.Color.blue()
            )

            class TransactionUpdateView(discord.ui.View):
                def __init__(self):
                    super().__init__(timeout=300)

                @discord.ui.button(label="General Information", style=discord.ButtonStyle.primary, emoji="📃", row=0)
                async def first_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    await interaction.response.send_modal(TransactionSourceUpdateFirst())

                @discord.ui.button(label="Payment Information", style=discord.ButtonStyle.primary, emoji="💱", row=0)
                async def second_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if not transaction_data:
                        return await interaction.response.send_message(
                            "⚠️ Please complete General Information first!",
                            ephemeral=True
                        )
                    await interaction.response.send_modal(TransactionSourceUpdateSecond())

                @discord.ui.button(label="Additional Information", style=discord.ButtonStyle.primary, emoji="➕", row=1)
                async def third_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if not transaction_data.get('InterestRate'):
                        return await interaction.response.send_message(
                            "⚠️ Please complete Payment Information first!",
                            ephemeral=True
                        )
                    await interaction.response.send_modal(TransactionSourceUpdateThird())

                @discord.ui.button(label="SUBMIT", style=discord.ButtonStyle.green, emoji="✅", row=1)
                async def submit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if not transaction_data.get('RemainingInstalments'):
                        return await interaction.response.send_message(
                            "⚠️ Please complete all information sections first!",
                            ephemeral=True
                        )

                    submit_view = WriteTransactionSource()
                    await submit_view.handle_submit(interaction)
                    self.stop()

            await ctx.send(embed=embed, view=TransactionUpdateView())

        else:
            view=FirstFinDropdown()
            await ctx.send("**FINANCE UPDATE IN PROGRESS!**", view=view)
    else:
        view = FirstFinDropdown()
        await ctx.send("**FINANCE UPDATE IN PROGRESS!**", view=view)

@bot.command(name="status", alias=["st"])
async def status(ctx):
    channel_id = ctx.channel.id
    finance_channel = s.FINANCE_ID

    if channel_id == finance_channel:
        #CHECK FINANCE STATUS IN FINANCE CHANNEL
        await ctx.send("This is the finance channel")

@bot.command(name="save", alias=["s"])
async def savings(ctx):
    view=SavingsDropdown()
    await ctx.send("***SAVINGS UPDATE IN PROGRESS!**", view=view)

if __name__ == "__main__":
    token=s.DISCORD_BOT_TOKEN
    bot.run(str(token))
