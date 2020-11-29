import discord
import asyncio
import urllib
import akinator
import random
import twemoji_parser
import requests
import typing
import io
import datetime
import aggdraw
import aiohttp
import os
import pykakasi
import json
import PIL

from discord.ext import commands, tasks
from discord import Spotify
from discord import Embed
from discord import File
from datetime import datetime
from typing import Optional
from humanfriendly import format_timespan

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from twemoji_parser import TwemojiParser
from colorthief import ColorThief

from urllib.parse import urlparse, quote
from akinator.async_aki import Akinator

akiObj = akinator.async_aki.Akinator()

kks = pykakasi.kakasi()

world_pfp = ("https://im-a-dev.xyz/EL35H6QC.png")

def add_corners(im, rad): # Thanks to Stackoverflow: https://stackoverflow.com/questions/11287402/how-to-round-corner-a-logo-without-white-backgroundtransparent-on-it-using-pi/11291419#11291419
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def round_corner_jpg(image, radius): # # Thanks to Stackoverflow: https://stackoverflow.com/questions/11287402/how-to-round-corner-a-logo-without-white-backgroundtransparent-on-it-using-pi/11291419#11291419
    mask = Image.new('L', image.size)
    draw = aggdraw.Draw(mask)
    brush = aggdraw.Brush('white')
    width, height = mask.size
    draw.pieslice((0,0,radius*2, radius*2), 90, 180, None, brush)
    draw.pieslice((width - radius*2, 0, width, radius*2), 0, 90, None, brush)
    draw.pieslice((0, height - radius * 2, radius*2, height),180, 270, None, brush)
    draw.pieslice((width - radius * 2, height - radius * 2, width, height), 270, 360, None, brush)
    draw.rectangle((radius, radius, width - radius, height - radius), brush)
    draw.rectangle((radius, 0, width - radius, radius), brush)
    draw.rectangle((0, radius, radius, height-radius), brush)
    draw.rectangle((radius, height-radius, width-radius, height), brush)
    draw.rectangle((width-radius, radius, width, height-radius), brush)
    draw.flush()
    image = image.convert('RGBA')
    image.putalpha(mask)
    return image

def relative_luminance(rgb_triplet):
    r, g, b = tuple(x / 255 for x in rgb_triplet)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

class FunCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gameCache = {}
        self.color = 0x2F3136

    @commands.command(help="World can make you laugh with his amazing jokes!")
    async def joke(self, ctx):
        headers = {"Accept": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com", headers=headers) as req:
                r = await req.json()
        embed = Embed(
            title="Epic joke!",
            description=r["joke"],
            color=self.color
            )
        await ctx.send(embed=embed)

    @commands.command(help="Ask Alister-A a question!")
    async def askali(self, ctx, *, question):
        responses = [
            "Ali A Kills Himself",
            "Ali A Ignores And Hits A 360 Noscope",
            "Ali A Approves",
            "Ali A Dosnt Approve"
        ]
        embed = Embed(title="Ask Alister-A", description=f"{ctx.author.mention} - {random.choice(responses)}", color=self.color)
        embed.add_field(name=f"**Question**", value=f'{question}', inline=False)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/710141167722824070/717777626877395004/aaaaa.png')
        await ctx.send(embed=embed)

    @askali.error
    async def askali_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Sorry {ctx.author.mention} Please Type `w/askali <question>`")


    @commands.command(name="f", help="Give respects.")
    async def f(self, ctx, *, text: commands.clean_content = None):
        sean = ['💔', '💝', '💚', '💙', '💜']
        reason = f"for **{text}** " if text else ""
        finchat = Embed(title = f"**{ctx.author.name}** has paid their respect {reason}{random.choice(sean)}", color=self.color)
        await ctx.send(embed=finchat)

    @commands.command(help="Shows a meme from random subreddits.")
    @commands.cooldown(rate=4, per=7, type=commands.BucketType.member)
    async def meme(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://memes.blademaker.tv/api?lang=en") as r:
                res = await r.json()
                title = res["title"]
                ups = res["ups"]
                subr = res["subreddit"]

                embed = Embed(title=f"Title: {title}\nSubreddit: r/{subr}", color=self.color)
                embed.set_image(url=res["image"])
                embed.set_footer(text=f"👍Ups:{ups}")
                await ctx.send(embed=embed)

    @meme.error
    async def meme_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            a = error.retry_after
            a = round(a)
            await ctx.send(f"Sorry {ctx.author.mention} This command in on cooldown, Try again in {a} seconds.")

    @commands.command(help="Enlarge a discord emoji!")
    async def enlarge(self, ctx, emoji: discord.PartialEmoji):
        if emoji.animated:
            embed = Embed(title="Enlarge", description=f"`{emoji.name}` was enlarged.", color=self.color)
            embed.set_image(url=emoji.url)
            await ctx.send(embed=embed)
        if not emoji.animated:
            embed = Embed(title="Enlarge", description=f"`{emoji.name}` was enlarged.", color=self.color)
            embed.set_image(url=emoji.url)
            await ctx.send(embed=embed)

    @enlarge.error
    async def enlarge_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Sorry {ctx.author.mention} Please Type `w/enlarge <emoji>`")
        if isinstance(error, commands.PartialEmojiConversionFailure):
            await ctx.send(f"Sorry {ctx.author.mention} that emoji was not found!")

    @commands.command(aliases=["pepe"], help="Shows users pp size.")
    async def pp(self, ctx, *, user: discord.Member = None):
        if user is None:
            user = ctx.author
        size = random.randint(1, 15)
        dong = ""
        for _i in range(0, size):
            dong += "="
        embed = Embed(title=f"{user}'s pepe size", description=f"8{dong}D", color=self.color)
        await ctx.send(embed=embed)

    @commands.command(help="Steal a users avatar.")
    async def avatar(self, ctx, *, user: discord.Member=None):
        format = "gif"
        user = user or ctx.author
        if user.is_avatar_animated() != True:
            format = "png"
        avatar = user.avatar_url_as(format = format if format != "gif" else None)
        async with aiohttp.ClientSession() as session:
            async with session.get(str(avatar)) as resp:
                image = await resp.read()
        with io.BytesIO(image) as file:
            await ctx.send(file=discord.File(file, f"Avatar.{format}"))

    @commands.command(help="Fake tweet text.")
    async def tweet(self, ctx, username: str, *, message: str):
        if len(message) >50:
            return await ctx.send(f"Sorry {ctx.author.mention} a limit of `50` chars please.")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(
                f"https://nekobot.xyz/api/imagegen?type=tweet&username={username}&text={message}"
            ) as r:
                res = await r.json()
                embed = Embed(color=self.color)
                embed.set_image(url=res["message"])
                await ctx.send(embed=embed)

    @tweet.error
    async def tweet_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Sorry {ctx.author.mention} Please Type `w/tweet <username> <message>`")

    @commands.command(help="Is that user gay?.")
    async def gay(self, ctx, *, user: discord.Member=None):
        user = user or (ctx.author)
        randomPercentage = random.randint(1, 100)
        embed = Embed(title="Gayrate!", color=self.color)
        embed.description = (f"**{user}** is {randomPercentage}% gay")
        embed.set_thumbnail(url=user.avatar_url)
        await ctx.send(embed=embed)

    @gay.error
    async def gay_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f':regional_indicator_x: Sorry {ctx.author.mention} Please Mention A User')

    @commands.command(aliases=["aki"], help="Can the akinator beat you?")
    async def akinator(self, ctx: commands.Context):
        if ctx.channel.id in self.gameCache.keys():
            return await ctx.send(
                "Sorry, {0[user]} is already playing akinator in <#{0[channel]}>, try again when they finish or move to another channel!"
                .format(self.gameCache[ctx.channel.id]))

        gameObj = await akiObj.start_game(child_mode=True)

        currentChannel = ctx.channel

        self.gameCache.update(
            {ctx.channel.id: {
                "user": ctx.author,
                "channel": ctx.channel.id
            }})

        while akiObj.progression <= 80:
            try:
                message1 = await ctx.send(
                    embed=Embed(title="Question", description=gameObj, color=self.color))
                resp = await ctx.bot.wait_for(
                    "message",
                    check=lambda message: message.author == ctx.author and
                    message.channel == ctx.channel and message.guild == ctx.
                    guild and message.content.lower(), timeout=15)
            except asyncio.TimeoutError:
                await ctx.send(embed=Embed(
                    title="Hurry next time!",
                    description=
                    f"{ctx.author.mention} took too long to respond so we ended the game\nCurrent timeout: `15` Seconds.", color=self.color))
                del self.gameCache[ctx.channel.id]
                return await message1.delete(delay=None)
            if resp.content == "b":
                try:
                    gameObj = await akiObj.back()
                except akinator.CantGoBackAnyFurther:
                    await ctx.send(embed=Embed(
                        title="Cannot go back any further :(",
                        description="Continue playing anyway", color=self.color))
            elif resp.content == "q" or resp.content == "quit":
                await ctx.send(embed=Embed(
                    title="Game over",
                    description=
                    "You have left the game.",
                    color=self.color
                    ))
                del self.gameCache[ctx.channel.id]
                break
            else:
                try:
                    gameObj = await akiObj.answer(resp.content)
                except:
                    del self.gameCache[ctx.channel.id]
                    return await ctx.send(embed=Embed(
                        title="Invalid Answer",
                        description=
                        "You typed a invalid answer the only answer options are:\n`y` OR `yes` for yes\n`n` OR `no` for no\n`i` OR `idk` for i dont know\n`p` OR `probably` for probably\n`pn` OR `probably not` for probably not\n`b` for back\n`q` or `quit` for stop the game",
                        color=self.color
                    ))

        await akiObj.win()

        embed = Embed(
            title="I have outsmarted your outsmarting",
            color=self.color
        ).add_field(
            name="I think...",
            value="it is {0.first_guess[name]} {0.first_guess[description]}?\n\nSorry if im wrong, Akinator has tried.".
            format(akiObj)).set_image(
                    url=akiObj.first_guess['absolute_picture_path']
                ).set_footer(text="Thanks to nomadiccode for helping!")

        del self.gameCache[ctx.channel.id]
        await ctx.send(embed=embed)


    @commands.command(aliases=["8ball"], help="The magical World 8ball.")
    async def _8ball(self, ctx, *, question):
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "World Says Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Dont count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "World Thinks Its Very doubtful.",
        ]
        embed = Embed(title=":8ball: The Almighty 8ball :8ball:", description=f"Question = `{question}`\n **Answer**: :8ball: {random.choice(responses)} :8ball:", color=self.color)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/717038947846455406/717784205249085470/aaaaaaaaaaaaaaaaaaa.png')
        await ctx.send(embed=embed)

    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Sorry {ctx.author.mention} Please Type `w/8ball <question>`")

    @commands.command(help="Turn text into emojis!.")
    async def emojify(self, ctx, *, stuff):
        if len(stuff) > 20:
            return await ctx.send(f"Sorry {ctx.author.mention} a limit of `20` chars please!")
        emj = ("".join([":regional_indicator_"+l+":"  if l in "abcdefghijklmnopqrstuvwyx" else [":zero:", ":one:", ":two:", ":three:", ":four:", ":five:", ":six:", ":seven:", ":eight:", ":nine:"][int(l)] if l.isdigit() else ":question:" if l == "?" else ":exclamation:" if l == "!" else l for l in f"{stuff}"]))
        embed = Embed(title='Emojify', description=f'{emj}', color=self.color)
        await ctx.send(embed=embed)

    @emojify.error
    async def emojify_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Sorry {ctx.author.mention} Please Type `w/emojify <text>`")

    @commands.command(help="Kill a user")
    async def kill(self, ctx, user: discord.Member):
        user = user or (ctx.author)
        kills = [
        "they stole money from your bank",
        "they ate your cookies",
        "they tried to steal your phone",
        "they smelled like poop",
        "they didn't like you",
        "they lied to you",
        "they didnt trust you"
        ]
        embed = Embed(
            title="Murder",
            description=f"{ctx.author.mention} you killed {user.mention} because {random.choice(kills)}",
            color=self.color
            )
        await ctx.send(embed=embed)

    @commands.command(help="Urban Dictionary")
    @commands.is_nsfw()
    async def urban(self, ctx, *name):
        if ctx.channel.is_nsfw():
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"http://api.urbandictionary.com/v0/define?term={'%20'.join(name)}") as r:
                    if r.status != 200:
                        return await ctx.send(f"Sorry {ctx.author.mention} Api has broken.")
                    json = await r.json()
                    list1 = json['list']
                    if len(list1) < 1:
                        return await ctx.send(f"Sorry {ctx.author.mention} This word was not found in Urban.")
                    res = list1[0]
                    embed = Embed(title=res['word'], color=self.color)
                    embed.description = res['definition']
                    embed.add_field(name="Example", value=res['example'])
                    embed.set_footer(text=f"👍 {res['thumbs_up']} | 👎{res['thumbs_down']}")
                    await ctx.send(embed=embed)

    @urban.error
    async def urban_error(self, ctx, error):
        if isinstance(error, commands.errors.NSFWChannelRequired):
            embed = Embed(title="NSFW", description=f"Sorry {ctx.author.mention} but this command is nsfw and this is not a nsfw channel.", color=self.color)
            embed.set_image(url="https://media.discordapp.net/attachments/265156286406983680/728328135942340699/nsfw.gif")
            return await ctx.send(embed=embed)


    @commands.command(name="activity")
    async def _activity(self, ctx: commands.Context, *, user: discord.Member = None):
        user = user or ctx.author
        if user.bot == True:
            embed = Embed(
                title="Activity",
                color=self.color,
                description=f"Sorry {ctx.author.mention} that's a bot, please mention a user!"
                )
            return await ctx.send(embed=embed)
        if user.activity == None:
            embed = Embed(
                title="Activity",
                color=self.color,
                description=f"Sorry {ctx.author.mention} that user does not have a status!"
                )
            return await ctx.send(embed=embed)
        for activity in user.activities:
            if activity.type is discord.ActivityType.playing:
                embed = Embed(
                   title=f"Activity",
                    color=self.color
                    ).add_field(
                    name=f"Playing {user.activity.name}",
                    value=f"{user.activity.state}"
                    ).set_thumbnail(
                    url=f"{user.activity.large_image_url}"
                    )
                await ctx.send(embed=embed)
            elif isinstance(activity, Spotify):
                embed = Embed(
                    title=f"Activity",
                    description=f"Listening to {user.activity.name}\n[`{user.activity.artist} - {user.activity.title}`](https://open.spotify.com/track/{user.activity.track_id})",
                    color=self.color
                    ).set_thumbnail(
                    url=activity.album_cover_url
                    )
                await ctx.send(embed=embed)
            elif activity.type is discord.ActivityType.streaming:
                embed = Embed(
                    title=f"Activity",
                    color=self.color,
                    description=f"Streaming {user.activity.name}\n[`Watch`]({user.activity.url})"
                    )
                await ctx.send(embed=embed)
            elif isinstance(activity, discord.CustomActivity):
                embed = Embed(
                    title="Activity",
                    color=self.color,
                    description=f"{user.activity.emoji} {user.activity.name}"
                    )
                await ctx.send(embed=embed)

    @_activity.error
    async def _activity_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(f'Sorry {ctx.author.mention} i could not find that user.')

    @commands.command(help="Advice from world.")
    async def advice(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://api.adviceslip.com/advice", headers={"Accept": "application/json"}) as r:
                res = await r.json(content_type="text/html")
                embed = Embed(
                    title="Advice",
                    description=f"{res['slip']['advice']}",
                    color=self.color
                    )
                await ctx.send(embed=embed)

    @commands.command(help="Generate qr code")
    async def qr(self, ctx, *, text):
        embed = Embed(
            title="Qr code",
            description=f"Generated `{text}`",
            color=self.color
            ).set_image(
            url=f"http://api.qrserver.com/v1/create-qr-code/?data={quote(text)}&margin=25"
            )
        await ctx.send(embed=embed)

    @qr.error
    async def qr_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Sorry {ctx.author.mention} Please Type `w/qr <text>`")

    @commands.command(help="This command will show you a cute duck", aliases=['quack', 'duk'])
    async def duck(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://random-d.uk/api/v2/random') as r:
                res = await r.json()
                duckimg = res['url']
        embed = Embed(
            title='Quack!',
             color=self.color
             ).set_image(
             url=duckimg
             )
        await ctx.send(embed=embed)

    @commands.command(help="Flip a users avatar!", aliases=["flipav", "avflip"])
    async def flip(self, ctx, user: discord.Member=None):
        user = user or ctx.author

        pfp = user.avatar_url_as(format='png')

        buffer_avatar = io.BytesIO()
        await pfp.save(buffer_avatar)
        buffer_avatar.seek(0)

        av_img = Image.open(buffer_avatar)

        done = av_img.rotate(180)

        buffer = io.BytesIO()

        done.save(buffer, format='PNG')

        buffer.seek(0)

        file = discord.File(buffer, "flippedimg.png")
        embed = discord.Embed(title="Flip!", description=f"{user}'s avatar flipped", color=0x2F3136)
        embed.set_image(url="attachment://flippedimg.png")
        await ctx.send(embed=embed, file=file)


    @commands.command(help="Blur a users avatar!")
    async def blur(self, ctx, user: discord.Member=None):
        user = user or ctx.author
        pfp = user.avatar_url_as(format='png')
        buffer_avatar = io.BytesIO()

        await pfp.save(buffer_avatar)

        buffer_avatar.seek(0)

        av_img = Image.open(buffer_avatar)
        done = av_img.filter(PIL.ImageFilter.GaussianBlur(radius=8))

        buffer = io.BytesIO()
        done.save(buffer, format='PNG')
        buffer.seek(0)

        file = discord.File(buffer, "blurimg.png")
        embed = discord.Embed(title="blur!", description=f"{user}'s avatar blurred", color=0x2F3136)
        embed.set_image(url="attachment://blurimg.png")
        await ctx.send(embed=embed, file=file)

    @commands.command(hlep="Generate a fake discord message!", aliases=["fq", "fakeq", "fakemessage", "fakemsg"])
    async def fakequote(self, ctx, user: Optional[discord.Member], *, message) -> None:
        if len(message) > 50:
            return await ctx.send(f"Sorry {ctx.author.mention} there is a limit of `50` chars.")
        now = datetime.now()
        user = user or ctx.author
        pfp = user.avatar_url_as(format='png')
        buffer_avatar = io.BytesIO()

        await pfp.save(buffer_avatar)

        buffer_avatar.seek(0)
        font = ImageFont.truetype("fonts/Whitney-Medium.ttf", 22, encoding="unic")
        fontsmall = ImageFont.truetype("fonts/Whitney-Medium.ttf", 16, encoding="unic")
        fontnormal = ImageFont.truetype("fonts/Whitney-Medium.ttf", 20, encoding="unic")

        userchar = font.getsize(user.name)[0]

        av_img = Image.open(buffer_avatar)
        image = Image.open("images/fake.png")
        parser = TwemojiParser(image)
        parser.draw_text((73, 65), user.name, fill='white', font=font)
        parser.draw_text((73 + userchar + 8, 69), str(now.strftime("Today at %H:%M")), fill='grey', font=fontsmall)
        parser.draw_text((74, 95), message, fill='white', font=fontnormal)

        resized = av_img.resize((45, 45));
        bigger = (resized.size[0] * 3, resized.size[1] * 3)
        maskimage = Image.new('L', bigger, 0)
        draw = ImageDraw.Draw(maskimage)
        draw.ellipse((0, 0) + bigger, fill=255)
        maskimage = maskimage.resize(resized.size, Image.ANTIALIAS)
        resized.putalpha(maskimage)

        output = ImageOps.fit(resized, maskimage.size, centering=(0.5, 0.5))
        output.putalpha(maskimage)
        image.paste(resized, (19, 69), resized)
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        file = discord.File(buffer, "fakequote.png")
        embed = discord.Embed(color=0x2F3136)
        embed.set_image(url="attachment://fakequote.png")
        await ctx.send(embed=embed, file=file)

    @fakequote.error
    async def fakequote_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Sorry {ctx.author.mention} Please Type `w/fakequote <user> <text>`")

    @commands.command(help="Write a top.gg Review", aliases=["tgg", "topggreview", "topggbotreview", "botreview"])
    async def topgg(self, ctx, user: Optional[discord.Member], *, message):
        user = user or ctx.author
        if len(message) > 30:
            return await ctx.send(f"Sorry {ctx.author.mention} there is a limit of `30` chars.")

        ran_days = random.randint(2, 30)
        picture = user.avatar_url_as(format='png')
        buf_avatar = io.BytesIO()

        await picture.save(buf_avatar)
        buf_avatar.seek(0)

        font = ImageFont.truetype("fonts/karla1.ttf", 19, encoding="unic")
        fontsmall = ImageFont.truetype("fonts/karla1.ttf", 15, encoding="unic")
        fontnormal = ImageFont.truetype("fonts/karla1.ttf", 18, encoding="unic")

        userchars = font.getsize(user.name)[0]

        mainimage = Image.open("images/tgg.png")
        parser = TwemojiParser(mainimage)
        parser.draw_text((126, 43), user.name, fill='black', font=font)
        parser.draw_text((132 + userchars + 2, 47.8), f"{ran_days} days ago", fill='grey', font=fontsmall)
        parser.draw_text((129, 84), message, fill='black', font=font)

        user_picture = Image.open(buf_avatar)

        resize = user_picture.resize((41, 41));
        size_bigger = (resize.size[0] * 3, resize.size[1] * 3)
        maskimage = Image.new('L', size_bigger, 0)
        draw = ImageDraw.Draw(maskimage)
        draw.ellipse((0, 0) + size_bigger, fill=255)
        maskimage = maskimage.resize(resize.size, Image.ANTIALIAS)
        resize.putalpha(maskimage)

        output = ImageOps.fit(resize, maskimage.size, centering=(0.5, 0.5))
        output.putalpha(maskimage)
        mainimage.paste(resize, (62, 46), resize)

        buffer = io.BytesIO()
        mainimage.save(buffer, format='PNG')
        buffer.seek(0)

        file = discord.File(buffer, "topggreview.png")
        embed = discord.Embed(color=0x2F3136)
        embed.set_image(url="attachment://topggreview.png")
        await ctx.send(embed=embed, file=file)

    @topgg.error
    async def topgg_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Sorry {ctx.author.mention} Please Type `w/topgg <user> <text>`")

    @commands.command(help="Widen a discord avatar!", aliases=["widen", "putin", "wideputin"])
    async def wide(self, ctx, user: discord.Member=None):
        user = user or ctx.author

        pfp = user.avatar_url_as(format='png')

        buffer_avatar = io.BytesIO()
        await pfp.save(buffer_avatar)
        buffer_avatar.seek(0)

        av_img = Image.open(buffer_avatar)

        done = av_img.resize((350, 180))

        buffer = io.BytesIO()

        done.save(buffer, format='PNG')

        buffer.seek(0)

        file = discord.File(buffer, "stretch.png")
        embed = discord.Embed(title="Wide!", description=f"{user}'s avatar widened", color=0x2F3136)
        embed.set_image(url="attachment://stretch.png")
        await ctx.send(embed=embed, file=file)

    @commands.command(help="Get spotify information on a discord user!", aliases=["sp"])
    async def spotify(self, ctx, user: Optional[discord.Member]):
        user = user or ctx.author
        spotify_activity = next(
            (activity for activity in user.activities if isinstance(activity, Spotify)),
            None
            )
        if spotify_activity is None:
            return await ctx.send(f"Sorry {ctx.author.mention} {user.name} is not currently listening to Spotify.")

        async with aiohttp.ClientSession() as cs:
            async with cs.get(str(spotify_activity.album_cover_url)) as r:
                res = io.BytesIO(await r.read())

            color_thief = ColorThief(res)
            dominant_color = color_thief.get_color(quality=40)

            font = ImageFont.truetype("fonts/spotify.ttf", 42, encoding="unic")
            fontbold = ImageFont.truetype("fonts/spotify-bold.ttf", 53, encoding="unic")

            title = kks.convert(spotify_activity.title)
            album = kks.convert(spotify_activity.album)
            artists = kks.convert(spotify_activity.artists)

            title_new = ''.join(item['hepburn'] for item in title)
            album_new = ''.join(item['hepburn'] for item in album)
            transliterated_artists = [kks.convert(artist) for artist in spotify_activity.artists]
            artists_new = ', '.join(''.join(item['hepburn'] for item in artist) for artist in transliterated_artists)

            abridged = album_new if len(album_new) <= 20 else f'{album_new[0:17]}...'

            cbridged = title_new if len(title_new) <= 30 else f'{title_new[0:27]}...'

            dbridged = artists_new if len(artists_new) <= 30 else f'{artists_new[0:27]}...'

            duration = format_timespan(spotify_activity.duration)

            luminance = relative_luminance(dominant_color)

            text_colour = 'black' if luminance > 0.5 else 'white'

            img = Image.new('RGB', (999, 395), color=dominant_color)

            album = Image.open(res)
            resized_album = album.resize((245, 245))
            img.paste(resized_album, (41, 76))

            parser = TwemojiParser(img)

            parser.draw_text((300, 90), abridged, fill=text_colour, font=fontbold)
            parser.draw_text((303, 170), cbridged, fill=text_colour, font=font)
            parser.draw_text((303, 228), dbridged, fill=text_colour, font=font)

            final = add_corners(img, 55)

            buffer = io.BytesIO()
            final.save(buffer, format='PNG')
            buffer.seek(0)

            file = discord.File(buffer, "spotify.png")
            embed = discord.Embed(color=0x2F3136)
            embed.set_image(url="attachment://spotify.png")
            await ctx.send(embed=embed, file=file)

def setup(bot):
    bot.add_cog(FunCog(bot))
