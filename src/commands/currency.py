from discord import User, Forbidden, Message
from discord.ext import commands
from discord.ext.commands import Context

from database import db
from database.repository import profile_repository


class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pay(self, context: Context, user: User, amount: int):
        author_money = profile_repository.get_money(context.author)
        user_money = profile_repository.get_money(user)

        if amount < 1:
            return await context.channel.send("No stealing!")

        if author_money.balance < amount:
            return await context.channel.send("You don't have enough money.")

        # Update balance
        user_money.balance += amount
        author_money.balance -= amount

        session = db.session()
        session.commit()

        await context.channel.send("Transferred money successfully. New balance: %d" % author_money.balance)

    @commands.command()
    async def balance(self, context: Context, user: User = None):
        if not user:
            money = profile_repository.get_money(context.author)
        else:
            money = profile_repository.get_money(user)

        await context.channel.send("Current balance: %d" % money.balance)

    @commands.command()
    async def namechange(self, context: Context, user: User):
        """
        Pay 10 to change somebody's nickname to whatever you want.
        """
        cost = 10

        message: Message = context.message
        name = message.content.split(" ", 2)[2]

        money = profile_repository.get_money(context.author)

        if money.balance < cost:
            return await context.channel.send("Changing someones name costs 500.")

        try:
            await context.guild.get_member(user.id).edit(nick=name)
        except Forbidden as e:
            return await context.channel.send("You cannot change this user's name.")

        money.balance -= cost
        db.session().commit()
