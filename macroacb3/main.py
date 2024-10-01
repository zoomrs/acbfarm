from acbmodules import Mouse, Keyboard
from acbmodules import utils
from acbmodules.utils import Maps, getscreenpixelcolordiff, istemplatevisible, Regions, Templates,\
    acblog, LogColor
from PIL import ImageGrab
import asyncio as aio
from asyncio import sleep
from json import load as jsload
import numpy as np
from time import time as tick

# do not change
config = jsload(open("config.json"))
autochallenge = config["auto challenge"]
autoinfinite = config["auto infinite"]
antiafk = config["anti afk"]
challengecooldown = 60 *  config["verify challenge routine cooldown minutes"]


running = True
frame = np.array([])
inbattle = False
status = 1
lastchallengetick = 0
antiafktick = 0

#--------------
class StatusCode:
    idle = 1
    infinite = 2
    challenge = 3
#--------------
async def isteleportuienabled() -> bool:
    if (await istemplatevisible(frame, Templates.areastp, region=Regions.areatp))[0]:
        return True
    return False

async def ischallengeuienabled() -> bool:
    if await getscreenpixelcolordiff(frame, Maps.Indents.challengeui.coord, Maps.Indents.challengeui.color) < 2:
        return True
    return False

async def closemenus(): # WORKING GREAT
    for k, ui in Maps.closebuttons.items():
        if (await getscreenpixelcolordiff(frame, ui[0].coord, ui[0].color)) == 0:
            await Mouse.clickv2(ui[1])

async def takeabreakinfinite(): # WORKING GREAT
    global inbattle
    while inbattle:
        await Mouse.clickv2(Maps.Buttons.takeabreak)
        await sleep(0.1)

async def gotoarena():
    if await isteleportuienabled():
        await Mouse.clickv2(Maps.Buttons.teleporttoarena)
        await sleep(0.2)
    else:
        await closemenus()
        await sleep(0.2)
        await Mouse.clickv2(Maps.Buttons.teleport)
        await sleep(0.2)
        await Mouse.clickv2(Maps.Buttons.teleporttoarena)
        await sleep(0.2)
    #---------------------------------------------------------------
    gotgameplaypaused = False
    while (await istemplatevisible(frame, Templates.gameplaypaused, region=Regions.gameplaypaused))[0]:
        gotgameplaypaused = True
        await sleep(0.1)
    if not gotgameplaypaused:
        await sleep(0.5)
    else:
        await sleep(2)

async def startinfinite():
    while not inbattle:
        await gotoarena()
        await sleep(0.63)
        await Keyboard.presskey(Keyboard.Key.D, 1.7)
        await sleep(0.5)
        await Keyboard.presskey(Keyboard.Key.W, 2.4)
        await sleep(0.3)
        await Keyboard.presskey(Keyboard.Key.E, 0.1)
        await sleep(1.2)
        await Mouse.clickv2(Maps.Buttons.acceptdialog)
        await sleep(0.2)
        await sleep(4)


async def startchallenge(): # return false, None if all in cooldown
    await closemenus()
    await sleep(0.2)
    while not (await ischallengeuienabled()):
        await sleep(0.2)
        await gotoarena()
        await sleep(0.2)
        await Keyboard.presskey(Keyboard.Key.W, 1.2)
        await sleep(0.3)
        await Keyboard.presskey(Keyboard.Key.A, 1.5)
        await sleep(0.3)
        await Keyboard.presskey(Keyboard.Key.E, 0.1)
        await sleep(0.7)
        await Mouse.clickv2(Maps.Buttons.acceptdialog)
        await sleep(0.75)

    #-----challenges ui-----
    await Mouse.clickv2(Maps.Buttons.enablehardmode)
    await sleep(0.4)
    await Mouse.move(748, 582)
    await sleep(0.2)
    for i in range(0,5,2):
        await Mouse.scroll(i)
        await sleep(0.2)
        for challenge, position in Maps.challengesmap[i].items():
            await Mouse.clickv2(position)
            await sleep(0.6)
            if (await istemplatevisible(frame, Templates.enterchallenge, region=Regions.enterchallenge))[0]:
                 await Mouse.clickv2(Maps.Buttons.enterchallenge)
                 return True, challenge
    return False, None

#--------------
async def _looptemplate() -> bool:
    if not (await utils.isinroblox()):
        await sleep(0.01)
        return False
    await sleep(0.01)
    return True

async def frameupdateloop():
    global frame
    while running:
        if not await _looptemplate():
            continue
        frame = np.array(ImageGrab.grab())

async def inbattleupdateloop(): # 100% of precision
    global inbattle
    i = 0
    while running:
        if not await _looptemplate():
            continue
        if(await getscreenpixelcolordiff(frame, Maps.Indents.hidebattle.coord, Maps.Indents.hidebattle.color)) < 3:
            inbattle = True
            i = 0
            continue
        if i < 1:
            await sleep(4)
            i += 1
            continue
        else:
            inbattle = False

async def antiafkloop():
    global antiafktick
    while running:
        if not await _looptemplate():
            continue
        now = tick()
        if (now - antiafktick) > 60.0*5:
            await Keyboard.presskey(Keyboard.Key.J)
            await sleep(0.1)
            antiafktick = now

async def mainloop():
    global lastchallengetick, status, inbattle
    await sleep(1)

    while running:
        if not await _looptemplate():
            continue
        #-----------------------------------
        if status == StatusCode.infinite:
            await acblog("taking a break...", LogColor.yellow)
            await takeabreakinfinite()
            await sleep(0.5)
            await acblog("done", LogColor.green)

        await acblog("starting challenges...", LogColor.yellow)
        gotchallenge, challenge = await startchallenge()
        gotatleastachallenge = False
        while gotchallenge:
            status = StatusCode.challenge
            gotatleastachallenge = True
            await sleep(4)
            await acblog(f"in challenge: {challenge.name}", LogColor.yellow)
            while inbattle:
                await sleep(0.1)
            gotchallenge, challenge = await startchallenge()
        if gotatleastachallenge:
            await acblog("all challenges got done!", LogColor.green)
            lastchallengetick = tick()
        else:
            await acblog(f"challenges are in cooldown\ntrying again in {int(challengecooldown/60)} minute(s)",
                         LogColor.red)

        await acblog("starting infinite...", LogColor.yellow)
        await startinfinite()
        status = StatusCode.infinite
        now = tick()
        while tick() - now < challengecooldown:
            await sleep(0.1)


loop=aio.new_event_loop()
aio.set_event_loop(loop=loop)
aio.ensure_future(mainloop())
loop.create_task(frameupdateloop())
loop.create_task(inbattleupdateloop())
if antiafk:
    loop.create_task(antiafkloop())
loop.run_forever()