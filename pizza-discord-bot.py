#!/usr/bin/env python3
"""Discord bot for $PIZZA token community."""
import os
import discord
from discord.ext import commands, tasks
from discord_slash import SlashCommand, SlashContext
#from discord_slash.utils.manage_components import create_button, create_actionrow
#from discord_slash.model import ButtonStyle
from dotenv import load_dotenv
from hiveengine.market import Market
from hiveengine.tokenobject import Token
import random
from pycoingecko import CoinGeckoAPI
import hiveengine
from hiveengine.wallet import Wallet
import json
from hiveengine.api import Api
import beem
from beem.witness import Witness, WitnessesRankedByVote
import datetime
import requests
import traceback
import sys
from datetime import datetime, timedelta
import dateutil.parser
from operator import itemgetter

# Hive-Engine defines
hive = beem.Hive(node=['https://api.hive.blog'])
beem.instance.set_shared_blockchain_instance(hive)
hiveengine_api = Api()
market = Market(api=hiveengine_api, blockchain_instance=hive)


DEFAULT_TOKEN_NAME = 'PIZZA'
DEFAULT_DIESEL_POOL = 'PIZZA:STARBITS'
DEFAULT_GIF_CATEGORY = 'PIZZA'
ACCOUNT_FILTER_LIST = ['thebeardflex', 'pizzaexpress', 'datbeardguy',
                       'pizzabot', 'null', 'vftlab', 'pizza-rewards']

CONFIG_FILE = 'config.json'

# Miscellaneous defines
MARKET_HISTORY_URL = 'https://history.hive-engine.com/marketHistory?symbol=%s&volumetoken'

PIZZA_GIFS = ['https://tenor.com/bOpfE.gif', 'https://tenor.com/bOphp.gif', 'https://tenor.com/bOpms.gif', 'https://tenor.com/bLZrj.gif']
PIZZA_GIFS += ['https://files.peakd.com/file/peakd-hive/pizzabot/24243uENGsh6uW4qKCGujxK4BvoMKN5RcN7sfaEJ5NKJtep8rt9afWsVtg3Kvjtq1pDjS.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23zGqBEBBrndd2a4j4sFd7pfokJbPP78MUeXbhTF7tpkm68TDPNKpyEQx6SyXfw2TvxCc.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xouo4FKcHyERYKyiEm4x425LXY5UZsLSbwPtftnNGdqpGPpP9TwJ6k3WfLGw7dRi8ix.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23wqthb5pRQCesbcTuqXfTcNtjLsRRRTpEUfTaMAqm1h8jVmEgYikZjf2edLHrRcoDriQ.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23yd8DEejLwG8jbK6yiHPUqaQqC2rWNvVjANJcC5J5LQM3NKz9SHZZqCy9Lzg1YsnoR5W.gif','https://files.peakd.com/file/peakd-hive/pizzabot/242DXLG4DJojrUAscw229UnyJkGma6C1QoCQjngcVG2LFbkaTdN4oJw9WgLLxV3N2oWLc.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23sdt4qbqaFxwbYhkYuviGR8kBeGLTYeaveqjXiwGSRUbxyV5J5rusMoXD1AGk2JhpDsi.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23wX5M8YHK92Kzmr8gAE1mZRePnsG96StjiPPnDYGcdq6BD3BkmMb7jLrCiPVrGRKsbBi.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xL35bVpiQbPTwnuBMMPsEpSbApf598uVE9fMXq8SKj5Hzh2ik4CnHYWcRNBriXkk5gQ.gif','https://files.peakd.com/file/peakd-hive/pizzabot/242DQXTLyKebw5oUNSqsNPvoqPDXCgPKafnoB2zE7bBqyfCAKxKL44r4SarskWCmYY4Lc.gif','https://files.peakd.com/file/peakd-hive/pizzabot/242s64cMzwVBDgMuApdLgtJrj4G4Qt3dTjJuKWFb4MXCvwiXAorV25iTUMFjU4gPm1azQ.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23y92ccQqXL7ixb1AYUg8T6yHRAEiLptBYhuoahFeh8uU8FXt1WFhJBwLysktbFdC46Gc.gif','https://files.peakd.com/file/peakd-hive/pizzabot/242Nt1WKYcjivqc1FPyfqwQ6vkTs7sznxWKYagPhc7TQ4v8VSYNA46NEswjkZeiSxuRAC.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xKxeFC2EKESp2cQ3MrPHcAHEaFtvf2mekStgrqqSxYS5rL7PnfmNwoWVQbdJwJS6zQt.gif','https://files.peakd.com/file/peakd-hive/pizzabot/242hfEv5oigYcb19z6ZDEPANTmAn1rWub84KKSJqdbtenEWhPxK2H1tqwanWzTrXZC3LQ.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xerFt4yJKoK1hhVdzVEYpKMKbGUHaW9SR3g7os8UmqAZLsnhs5QgWGeD9NNk72FNGxC.gif','https://files.peakd.com/file/peakd-hive/pizzabot/243Bpw3x8jfheRpNACEc9fjrrLvn2Qtw8KQwhwscRjLc8BNfhxktPjuLDvnjTv7wCeLVi.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xAcRA5z5PG8aNLzq3jcDrSwP6eVYAagSSooGTzWQ4TZHPvNH8Ccc16zwtP6y3fkgX1e.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23zGkxUGqyXMTN7rVm2EPkLr6dsnk4T4nFyrEBejS9WB2VbKpJ3P356EcQjcrMF6gRTbz.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23x17QUuztsLf64Mav8m59nuRF4B9k3RAV6QGrtpvmc3hA9bxSJ2URkW7fuYSfaRLKAq2.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23wC5ZpMMfnFCsLS4MLF3N6XZ2aMQ1Fjnw6QGrZtpJqQmiH4xtsUEgjjCD5VU3ccjoRet.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xpKDUUZXfKhB9t5HqVEyqqd9ryYUkwTE2fgfZR6wAyzkPrjUY9rMpSP6zkrmXTUtBCQ.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23wr1XodaTgJAVzDu9sEV7q5r6RV3QppV2Nvxty4vD6BwYdHQLKGhgsynnz4fFC2GYyZW.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23wr1BUi29btm7eRvcRbqee2e52DCmH5x5HWLVrrQ7GqLc5UQMYawfsHTAsgCLghj5Kwa.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23z7SiUwzPi3WQ1nS8Lk4qBUqKtmgZRRTuQZP54mRiDpi8A22pk1ScoFgVa8CyhqQsAuS.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xpJztdYA9RpUnMRWDyYsWyixmqFMRSpix52vvx1vuxJSZHJL45YWmb9rUsswymZaSFE.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xyhemVn25gUt2p6JCHQ3hBjJyaz7d8hvmNusti9GNbjj8jToVFL4FaouPhkVoRYNnng.gif','https://files.peakd.com/file/peakd-hive/pizzabot/Ep1ZrmXNXjF4ZEYpXjJAVNThmFrQT3m4Q6jfxreCg1w7z81af8DHHZzeKk9QKy1Got8.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23wqwJUY56PuyQS3doAHbLfsjnNTcqLUry1cSmoSyGmRc49BswoxTGYhySmrXuevYWCJg.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23yTqi8V4mqNvq5nfFNt69AC2tMc5ou3FZ6r9AzfxuPEyQbrX8CBDEMXcjNNmTMTCMnXv.gif','https://files.peakd.com/file/peakd-hive/pizzabot/242DhzmX9cZCijjJpD1qwqvcRdJMHPsxvsfesBYkQUVpXpn5s3g9SewPCeiJ1ne4zUC7N.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xpKbgbo6LSPutm7ntaeVDiVJfdaxiJGhs8N4sve1MNdENuRAKw37uJbutCNBqj2M7vU.gif','https://files.peakd.com/file/peakd-hive/pizzabot/EopwGAarumCksxjQEeMsTXTDeMw16kD35cciBsiJFWbbBV8nGVyGAXtn4tScHTWQmvC.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23wgeYo6ULhiwyKEtKNpNfyU3oEn9zWJpKbSU2Hj5u11rn2YQr2wNoUUVrv1bBvMHgifn.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23xyfe5dT4xLHwJbamNCJUXpQuuV9kLucPMPXJsi74VoLq5bHBTrdkhVjyagno78r3F1n.gif','https://files.peakd.com/file/peakd-hive/pizzabot/23wMihvfhNfs4b1MKhb9bNdhEbeZoXTDkud331QCbL64zaxG6p9GuAbydjEUVczCDd49i.gif']
PINEAPPLE_GIFS = ['https://media.giphy.com/media/0gYYWq5dHfhnYVrYtI/giphy.gif', 'https://media.giphy.com/media/7gXkay4o8FnFzT7uJo/giphy.gif', 'https://media.giphy.com/media/pz4hZwrBZn4EGxpMlG/giphy.gif', 'https://media.giphy.com/media/ZDgaXZjeKWnzuf5RRF/giphy.gif', 'https://media.giphy.com/media/vxyDfIe3iRXhsJ7z5r/giphy.gif', 'https://media.giphy.com/media/Ganp5Ne5MdzkdupCRF/giphy.gif', 'https://media.giphy.com/media/tIxf5oMxG1PWUYJEcL/giphy.gif', 'https://media.giphy.com/media/JG2ziQmGrc0MrHzGuj/giphy.gif', 'https://media.giphy.com/media/uVW9moVaAR47Vgj7D0/giphy.gif', 'https://media.giphy.com/media/rHLj0lWywWuaeGiSTF/giphy.gif', 'https://media.giphy.com/media/XCvm5Oo6wEVJmxRx7V/giphy.gif', 'https://media.giphy.com/media/7b6sSJEEBqWatW2MYn/giphy.gif', 'https://media.giphy.com/media/18odCx2irVLDrvO3fY/giphy.gif', 'https://media.giphy.com/media/3g23LxFceQW8poMpTs/giphy.gif', 'https://media.giphy.com/media/N1ZxRLeX5wIz9Tvs8X/giphy.gif', 'https://media.giphy.com/media/ZwPHgEzoTcyKtaIlId/giphy.gif', 'https://media.giphy.com/media/9FmzQEdSbuSXcsPXCT/giphy.gif', 'https://media.giphy.com/media/WFdZOAE8OYcq5tSXee/giphy.gif', 'https://media.giphy.com/media/Bns85ZwsExoGgsKMmK/giphy.gif', 'https://media.giphy.com/media/Caoow9v9MRNIqmoFJJ/giphy.gif', 'https://media.giphy.com/media/3rTPQ1jH5osS4aBX8D/giphy.gif', 'https://media.giphy.com/media/FAqmU08XQKcGzzTpwO/giphy.gif', 'https://media.giphy.com/media/mQnBlO24UTPN723dpe/giphy.gif', 'https://media.giphy.com/media/RGV125iyT97ONLweyx/giphy.gif', 'https://media.giphy.com/media/vH5awikXqtANyuob7T/giphy.gif']
BRO_GIFS = ['https://media.giphy.com/media/Q7dRGcu38WqGnb7nnI/giphy.gif', 'https://media.giphy.com/media/V9RSXFgeldCNKLCydK/giphy.gif', 'https://media.giphy.com/media/jSKXXzMxL55JUN93Q6/giphy.gif', 'https://media.giphy.com/media/XKXP9qdvV14N445Im4/giphy.gif', 'https://media.giphy.com/media/GaySGYuvjk2u2ql7XU/giphy.gif', 'https://media.giphy.com/media/tUgNHh1rupdbZ30mrP/giphy.gif', 'https://media.giphy.com/media/41bHp9qHeO9G2RKKFs/giphy.gif', 'https://media.giphy.com/media/PVRn0PcZ1las7eow4J/giphy.gif', 'https://media.giphy.com/media/7gZ7c3LJZ9Z8l85EtY/giphy.gif', 'https://media.giphy.com/media/v8jgENvvlegjuxLOmc/giphy.gif', 'https://media.giphy.com/media/tbYfDQ8fX8siY80sBN/giphy.gif', 'https://media.giphy.com/media/WFHauwzA2gcVhXxMuH/giphy.gif', 'https://media.giphy.com/media/65yRhgpIYVcB8SICtF/giphy.gif', 'https://media.giphy.com/media/mkN81kU4YqteLCqPvU/giphy.gif', 'https://media.giphy.com/media/o6Dfmyj2p4S5a3oxz6/giphy.gif', 'https://media.giphy.com/media/A66FeQBsflVqikTe3m/giphy.gif', 'https://media.giphy.com/media/EDCIaFhFaAYsdkbwgd/giphy.gif', 'https://media.giphy.com/media/rGh7YlCLOkqlyOFpq9/giphy.gif', 'https://media.giphy.com/media/v32eWRX8XE8Vh2l44h/giphy.gif', 'https://media.giphy.com/media/6nVXn29SXPMHiPKgXi/giphy.gif', 'https://media.giphy.com/media/w67kdyKjyNr2Xeb3fM/giphy.gif', 'https://media.giphy.com/media/piNBUyg9b7yAFSexql/giphy.gif', 'https://media.giphy.com/media/umiHQSmGsF5EiVSAv6/giphy.gif', 'https://media.giphy.com/media/CyKE41GQ2srFBIHTiL/giphy.gif', 'https://media.giphy.com/media/9fnjcqc49X3uqjlZra/giphy.gif']
RISINGSTAR_GIFS = ['https://media.giphy.com/media/4fKFmbMTl2guk1n6y2/giphy.gif', 'https://media.giphy.com/media/T9QH5wAUPT8o2trbjD/giphy.gif', 'https://media.giphy.com/media/gL8iKEDRWzCdl6nk5G/giphy.gif', 'https://media.giphy.com/media/NchY6QQ2hzQisINQjA/giphy.gif', 'https://media.giphy.com/media/EkVBC57QI4U9IQfkY2/giphy.gif', 'https://media.giphy.com/media/IVYphXkTnL7EXn0gs3/giphy.gif', 'https://media.giphy.com/media/zj2H8HhLVtWnuGYqhx/giphy.gif', 'https://media.giphy.com/media/LDQqkkB1nhIr1kFsu7/giphy.gif', 'https://media.giphy.com/media/yHc7yfgyXRhLa5Q0qJ/giphy.gif', 'https://media.giphy.com/media/uYxnx1eiuhW97JvOAi/giphy.gif', 'https://media.giphy.com/media/jTTZ6zIsbcuRLisxLb/giphy.gif', 'https://media.giphy.com/media/Um2rquzMWZKQUbpT0I/giphy.gif', 'https://media.giphy.com/media/iH7FY0ukmmetUZHT0K/giphy.gif', 'https://media.giphy.com/media/rJ6tKAaV0IkvjH0ys4/giphy.gif', 'https://media.giphy.com/media/LUKMkHzmJkaCkpvHVg/giphy.gif', 'https://media.giphy.com/media/6YFeS3ejyheLd96ibx/giphy.gif', 'https://media.giphy.com/media/9zjksORdGKFecNYjUk/giphy.gif', 'https://media.giphy.com/media/Gk1Ch0WHuqknkBjLIn/giphy.gif', 'https://media.giphy.com/media/MjOvM7AdJDtKBKckJT/giphy.gif', 'https://media.giphy.com/media/i5XGW0zW6prU3L0WRM/giphy.gif', 'https://media.giphy.com/media/uYX7r0u449s49oWFLY/giphy.gif', 'https://media.giphy.com/media/QU0uxCUe6qVmwoLErs/giphy.gif', 'https://media.giphy.com/media/DSwdsnBw1qbLfL4NaB/giphy.gif', 'https://media.giphy.com/media/BY2W5iI5TrqVbC3eYo/giphy.gif', 'https://media.giphy.com/media/6kzDBcHoWzcwTbSSU8/giphy.gif']
POB_GIFS = ['https://media.giphy.com/media/btd5gT1uEKVUrMTM5F/giphy.gif', 'https://media.giphy.com/media/EPNH2hv2BTNm0c0i40/giphy.gif', 'https://media.giphy.com/media/t05mKJb8YiLlgckcC3/giphy.gif', 'https://media.giphy.com/media/q8K77RTBUmaSaWFgrE/giphy.gif', 'https://media.giphy.com/media/L6jEwgKyftQmSTJevb/giphy.gif', 'https://media.giphy.com/media/IioSnIxFIFed93The1/giphy.gif', 'https://media.giphy.com/media/VdQgGCxoc4gF3L4zY3/giphy.gif', 'https://media.giphy.com/media/Dou0bMmL4pxFem0zH0/giphy.gif', 'https://media.giphy.com/media/PmtcPpxG7o5PqM7YX4/giphy.gif', 'https://media.giphy.com/media/7Vqr9VKanN29Q1rbgr/giphy.gif', 'https://media.giphy.com/media/KZXlJ4K6Lr9INnvkUQ/giphy.gif', 'https://media.giphy.com/media/DGto0zMPaXIRkkHtMn/giphy.gif', 'https://media.giphy.com/media/9RulVBzWtHwz8AYmHw/giphy.gif', 'https://media.giphy.com/media/HHzLyXlf1HDhB2FAK6/giphy.gif', 'https://media.giphy.com/media/HD1cOJ7vltQtPoOyJM/giphy.gif', 'https://media.giphy.com/media/wiGC2mE3nM3hD8kinf/giphy.gif', 'https://media.giphy.com/media/BqoMcPD1vfDc55bUtK/giphy.gif']
PROFOUND_GIFS = ['https://media.giphy.com/media/SQ5M4nABcnPsRv4Sux/giphy.gif', 'https://media.giphy.com/media/6ar045QB2RuxeZfb6U/giphy.gif', 'https://media.giphy.com/media/L6xgc2dWJHb3eks3xa/giphy.gif', 'https://media.giphy.com/media/f2edaKKz4SWW6b60v2/giphy.gif', 'https://media.giphy.com/media/LNSWLRhRnjGX0d4Xqc/giphy.gif', 'https://media.giphy.com/media/QUpkbYcHGqxsKuGv5D/giphy.gif', 'https://media.giphy.com/media/XJmwDVhGnkjrmonuny/giphy.gif', 'https://media.giphy.com/media/NGNW6ZR2bV3C66LvnM/giphy.gif', 'https://media.giphy.com/media/zutsNVWa5PnmWLLORT/giphy.gif', 'https://media.giphy.com/media/2P4Ov6WtnxU4iFPx0C/giphy.gif', 'https://media.giphy.com/media/i6Qepo5EKDuruePSvV/giphy.gif', 'https://media.giphy.com/media/nDMbce12xS59Fh0oN2/giphy.gif', 'https://media.giphy.com/media/8G6N3UPP2FNLh3zJB9/giphy.gif', 'https://media.giphy.com/media/bIAm0uWiz2jZANh9at/giphy.gif', 'https://media.giphy.com/media/EYkkdDgnir7EcV61CJ/giphy.gif', 'https://media.giphy.com/media/nFkyu4FFGIlFZrt5n8/giphy.gif', 'https://media.giphy.com/media/0UkEoh2xT59QDTTF70/giphy.gif', 'https://media.giphy.com/media/7jGdJCHDBffOOSyxlf/giphy.gif', 'https://media.giphy.com/media/f64GgzL3cnF3WhuPjb/giphy.gif', 'https://media.giphy.com/media/RzUct7rduOf4976qjP/giphy.gif', 'https://media.giphy.com/media/yvQiEvCmDsjQe0BFJi/giphy.gif', 'https://media.giphy.com/media/3Nmzke5aDoj23Cu1AL/giphy.gif', 'https://media.giphy.com/media/dln8uROMLJylGIaHnZ/giphy.gif', 'https://media.giphy.com/media/19HdKao5FdOXwLowu5/giphy.gif', 'https://media.giphy.com/media/bNk3MLtmKaSSgGvqUe/giphy.gif']
BATTLEAXE_GIFS = ['https://media.giphy.com/media/8Oup5mUGVs2dZWNhCw/giphy.gif', 'https://media.giphy.com/media/twrPnIhjarlfVqhTvt/giphy.gif', 'https://media.giphy.com/media/aGaoKokoF4F7rFhb3a/giphy.gif', 'https://media.giphy.com/media/oDtC2KVOy9HNcG4y8s/giphy.gif', 'https://media.giphy.com/media/7U115amErU5M7Zuk6k/giphy.gif', 'https://media.giphy.com/media/aW2x62TDaNcwzLFT3L/giphy.gif', 'https://media.giphy.com/media/CRg4wEkzJRQ8ljNbUK/giphy.gif', 'https://media.giphy.com/media/AobPC1jh48luCFEREk/giphy.gif', 'https://media.giphy.com/media/p8hrL9PQq6S3JS6Z9w/giphy.gif', 'https://media.giphy.com/media/AJ82ifdfuN7D9OVDOv/giphy.gif', 'https://media.giphy.com/media/HbiFp4eWszvZdt2nr0/giphy.gif', 'https://media.giphy.com/media/jWAgAxHUxkeXxD4l4H/giphy.gif', 'https://media.giphy.com/media/33QVGxmaiL87VpNQJg/giphy.gif']
ENGLAND_GIFS = ['https://media.giphy.com/media/u9a7I1NjCRwDJvgQBe/giphy.gif', 'https://media.giphy.com/media/QCAwYlATLHAJZYyjId/giphy.gif', 'https://media.giphy.com/media/f71WnctzJj20XpXwrq/giphy.gif', 'https://media.giphy.com/media/5X7JrKbLgyYAIGcJrv/giphy.gif', 'https://media.giphy.com/media/hA88d22fB2ik0OoYsk/giphy.gif', 'https://media.giphy.com/media/VdcUMBoJBIxWNCjZFH/giphy.gif', 'https://media.giphy.com/media/VGXIQEXKWRNtmwR3ar/giphy.gif', 'https://media.giphy.com/media/H6b0VeNQLKaeziLOZ5/giphy.gif', 'https://media.giphy.com/media/5qwy92o8UyRm1p1KFe/giphy.gif', 'https://media.giphy.com/media/QhcLXkIxm8I0cgANr0/giphy.gif']
HUZZAH_GIFS = ['https://media.giphy.com/media/NK7s1mf7kyqvdhpPda/giphy.gif', 'https://media.giphy.com/media/cutDOWJ6TFOcPGNzbh/giphy.gif', 'https://media.giphy.com/media/qnGXaSWrBAu2z81Izt/giphy.gif', 'https://media.giphy.com/media/UGo7mKoHRPf1QB4TjE/giphy.gif', 'https://media.giphy.com/media/BbqkuiiJRbXGrbB3ia/giphy.gif', 'https://media.giphy.com/media/PxpcFRl7xzgaBsKauK/giphy.gif', 'https://media.giphy.com/media/WTYXq0mkUdzKBsoMhO/giphy.gif', 'https://media.giphy.com/media/GjQvNDr1Q5BaKQLxjY/giphy.gif', 'https://media.giphy.com/media/NeCZITVgP6C7xSCGql/giphy.gif', 'https://media.giphy.com/media/eEcRLf42mV9NalRqoU/giphy.gif', 'https://media.giphy.com/media/YpJyG2HsU5wZfZ6il0/giphy.gif', 'https://media.giphy.com/media/Gz8XfN6Uf7p4ISuhyk/giphy.gif', 'https://media.giphy.com/media/anBYsqSFAVKK7nbVFT/giphy.gif', 'https://media.giphy.com/media/XOnavX6DuHgVAxcszH/giphy.gif', 'https://media.giphy.com/media/JHbGALEbQFGMpAje0F/giphy.gif', 'https://media.giphy.com/media/pUxGNcUp2UipqVUxcZ/giphy.gif', 'https://media.giphy.com/media/x7ILoVXOJ2VM8UBBR5/giphy.gif']
BEARD_GIFS = ['https://media.giphy.com/media/GDGgyNaADzlfgFxsQ8/giphy.gif', 'https://media.giphy.com/media/vGNnl2zd7bWGhtux3l/giphy.gif', 'https://media.giphy.com/media/7eTqcO2RRq74IHHwub/giphy.gif', 'https://media.giphy.com/media/K40oW5YgCjBD4GnTAX/giphy.gif', 'https://media.giphy.com/media/hpQ8rTRaN84jTaKQIV/giphy.gif', 'https://media.giphy.com/media/y6uXquI7zySNQaguo7/giphy.gif', 'https://media.giphy.com/media/kW7SpyVapoeolLhHaV/giphy.gif', 'https://media.giphy.com/media/rLnsxjSUvArSrOfRDO/giphy.gif', 'https://media.giphy.com/media/iSsOEvgcXsBgJ0Tvt6/giphy.gif', 'https://media.giphy.com/media/UCLddjtFovvUzAsOYM/giphy.gif', 'https://media.giphy.com/media/j54tWqI1SyLlbkFB8v/giphy.gif', 'https://media.giphy.com/media/lWNCmxhRAtgDGDG80t/giphy.gif', 'https://media.giphy.com/media/hiZyT60Y6DcpNIu2IG/giphy.gif', 'https://media.giphy.com/media/YGxkIWgTeoMO2a8gVL/giphy.gif', 'https://media.giphy.com/media/UdvdbCu1efca3ZjbYZ/giphy.gif', 'https://media.giphy.com/media/J1bWno6ecjcenHEYoh/giphy.gif', 'https://media.giphy.com/media/tjFdjyJvH7jhW1b3Fr/giphy.gif', 'https://media.giphy.com/media/DsXgYmws370VALFG24/giphy.gif', 'https://media.giphy.com/media/R6sF4SGktcZkirUeMP/giphy.gif', 'https://media.giphy.com/media/LRZOlgqsKZuufctGJQ/giphy.gif']
LEGO_GIFS = ['https://media.giphy.com/media/G4kwvrvmlt8ciKjXP9/giphy.gif', 'https://media.giphy.com/media/h0tq5gDYnlOIJqvIfF/giphy.gif', 'https://media.giphy.com/media/mxjWb3yvsHUL4GMTst/giphy.gif', 'https://media.giphy.com/media/ImgQcjJ03oLToYZJWn/giphy.gif', 'https://media.giphy.com/media/EU1IkLvFtXXvx5qAVw/giphy.gif', 'https://media.giphy.com/media/uxMzxj8lK1FjruVaYo/giphy.gif', 'https://media.giphy.com/media/zgsuashHk2AH3kT0rj/giphy.gif', 'https://media.giphy.com/media/Pf9LofhYG1LTOHlziK/giphy.gif', 'https://media.giphy.com/media/FYCT2NgFyiZFzOHg8Y/giphy.gif', 'https://media.giphy.com/media/Z6RiM5gsJhlM91gybi/giphy.gif', 'https://media.giphy.com/media/Wj01dlce8lonswtCT3/giphy.gif', 'https://media.giphy.com/media/pbXQYjv9PaPUqil4MW/giphy.gif', 'https://media.giphy.com/media/B4wi6kDqDlZrv8NxTU/giphy.gif', 'https://media.giphy.com/media/El1P68jATWuZY6EYlQ/giphy.gif', 'https://media.giphy.com/media/DbYb1CUpnPNuZJVaNN/giphy.gif', 'https://media.giphy.com/media/dPpWDZk0XVRToXdZLy/giphy.gif', 'https://media.giphy.com/media/7FYC9A7LuEYf9e30na/giphy.gif', 'https://media.giphy.com/media/FhRwcmMEH9PkgjpllS/giphy.gif', 'https://media.giphy.com/media/H6rOWKlATmWnybS9mq/giphy.gif', 'https://media.giphy.com/media/NVktVqdCuzQ8dIVaVa/giphy.gif', 'https://media.giphy.com/media/CkOlg6FupoHZww9tIk/giphy.gif']
BLURT_GIFS = ['https://media.giphy.com/media/NDiXQBhcBe3i9pdsiw/giphy.gif', 'https://media.giphy.com/media/Sda1O3NXrO3s5pKtHw/giphy.gif', 'https://media.giphy.com/media/rWRW4322Cfru0Z5eEf/giphy.gif', 'https://media.giphy.com/media/geqRxwm5vx1QB0DWCR/giphy.gif', 'https://media.giphy.com/media/jytuKu4PXw6KYmcdc8/giphy.gif', 'https://media.giphy.com/media/RQ5qYz9BGWJbPXO8H4/giphy.gif', 'https://media.giphy.com/media/RV4cxcOAG45gX7KOix/giphy.gif', 'https://media.giphy.com/media/YM5Gw9xULBqF2qumB3/giphy.gif', 'https://media.giphy.com/media/QzIeA2TVcgCUIw2E8w/giphy.gif', 'https://media.giphy.com/media/p76jXuNFEVMOk59IAo/giphy.gif', 'https://media.giphy.com/media/fwZoVhxb3sVxoYDbep/giphy.gif', 'https://media.giphy.com/media/So8RwXWYlRKIZDlBqC/giphy.gif', 'https://media.giphy.com/media/d8PqnnR3AD7yCyfuhA/giphy.gif', 'https://media.giphy.com/media/rhyFAc2RcmEtxGiARK/giphy.gif', 'https://media.giphy.com/media/JB7YYqDDQxzdJtwF9Q/giphy.gif', 'https://media.giphy.com/media/BOUIxbEFm4CWtW72EK/giphy.gif', 'https://media.giphy.com/media/Pt9Qe5vR0dCRDQh7H4/giphy.gif', 'https://media.giphy.com/media/ffdprDwi9tVotD7m38/giphy.gif', 'https://media.giphy.com/media/3kGxK0wO8M8BlIDCBZ/giphy.gif', 'https://media.giphy.com/media/Q41Dxo5RGLtfDCXSmV/giphy.gif', 'https://media.giphy.com/media/FsfS2UQOZKjSa8w10I/giphy.gif']
FOXON_GIFS = ['https://media.giphy.com/media/DhKudYKoGOyJFHKA1r/giphy.gif', 'https://media.giphy.com/media/9ZNogzYmzRLHYXDtcR/giphy.gif', 'https://media.giphy.com/media/t3q7z5EcDmmPMwBd0i/giphy.gif', 'https://media.giphy.com/media/8imbHuhI8ZhMUQ8p0r/giphy.gif', 'https://media.giphy.com/media/BlMaitisfAtUEzKQLS/giphy.gif']
STICKUP_GIFS = ['https://media.giphy.com/media/XjjTY8qh3fZoQq5Tdu/giphy.gif', 'https://media.giphy.com/media/RrY68snArrNqERTCgc/giphy.gif', 'https://media.giphy.com/media/GNo3xnUtqNi5OIMhsu/giphy.gif', 'https://media.giphy.com/media/E5mi11dBhuiW4fOC2c/giphy.gif', 'https://media.giphy.com/media/Mm1wJNenpnBj76BlJJ/giphy.gif', 'https://media.giphy.com/media/utx5mlMfovTsUs5F69/giphy.gif', 'https://media.giphy.com/media/VchyhdU86WbsUjVNP7/giphy.gif', 'https://media.giphy.com/media/Fd6NEw3kR6ZaMnn5sX/giphy.gif', 'https://media.giphy.com/media/JFOdcPiOiaOwXhIz4q/giphy.gif', 'https://media.giphy.com/media/DqB8cqbWW0g6GfSBwu/giphy.gif', 'https://media.giphy.com/media/79K306oJupprCsf8DU/giphy.gif', 'https://media.giphy.com/media/lEqhVHS94PIlzoZCxP/giphy.gif', 'https://media.giphy.com/media/fLHHHzwYx61oHKBFT9/giphy.gif', 'https://media.giphy.com/media/npsHLArWNwR9kBp9Hz/giphy.gif', 'https://media.giphy.com/media/1s8xWlUv6pwE1LacIN/giphy.gif', 'https://media.giphy.com/media/qx8ydGluxIZctEpN7x/giphy.gif', 'https://media.giphy.com/media/LTTnOl7BDBQfeyGB0B/giphy.gif', 'https://media.giphy.com/media/2pcDVqocJ7uaZHYiFI/giphy.gif', 'https://media.giphy.com/media/p8BTBEsZrtG59Dni6t/giphy.gif', 'https://media.giphy.com/media/eVBNtrAXJu3mZ7bXGF/giphy.gif', 'https://media.giphy.com/media/FSIP4YFjm2fmaiRLk9/giphy.gif', 'https://media.giphy.com/media/MywBmUQxpNEJrNEwhz/giphy.gif', 'https://media.giphy.com/media/uVjVmXIPgwIoHYHsto/giphy.gif', 'https://media.giphy.com/media/1AhvGqvRafICfhu62z/giphy.gif', 'https://media.giphy.com/media/NGadEwb2motzfaoBV7/giphy.gif']
CINE_GIFS = ['https://media.giphy.com/media/FIyurUoMubWnaeXDbc/giphy.gif', 'https://media.giphy.com/media/6w4JmLoxAU0PCXe2xm/giphy.gif', 'https://media.giphy.com/media/CsklEOU26Chulc5Udg/giphy.gif', 'https://media.giphy.com/media/iIwLGWvsdrKInCU6pY/giphy.gif', 'https://media.giphy.com/media/YLMY3IFdMmqquCnbDw/giphy.gif', 'https://media.giphy.com/media/EIPgvGf26GHXqS34ms/giphy.gif', 'https://media.giphy.com/media/PMrgmU0eMbUbhwArsE/giphy.gif', 'https://media.giphy.com/media/l3LTdvgaMsg6hIbNQQ/giphy.gif', 'https://media.giphy.com/media/N7lrDrPZ2d6Ad1oHsV/giphy.gif', 'https://media.giphy.com/media/ersmVWkUPttGKVSstD/giphy.gif', 'https://media.giphy.com/media/wZJxb1ZGXlD6cdbNen/giphy.gif', 'https://media.giphy.com/media/qqmOLhVRrDgBS0M2rT/giphy.gif', 'https://media.giphy.com/media/3kgq6266FccZ2Jd2R6/giphy.gif', 'https://media.giphy.com/media/8jMIg3s65D4FpFmWZu/giphy.gif', 'https://media.giphy.com/media/7Idr5i34o3t8edcRCO/giphy.gif', 'https://media.giphy.com/media/ttWgnjl1WOIinoukq6/giphy.gif', 'https://media.giphy.com/media/hUBWNDBoBQTAXvsCQ6/giphy.gif', 'https://media.giphy.com/media/9GRzz5tUZiaJzy6rWO/giphy.gif', 'https://media.giphy.com/media/lQn6yyxsJgwhmQ0vdf/giphy.gif', 'https://media.giphy.com/media/O8qK5rGtDRDqHNC8Ec/giphy.gif', 'https://media.giphy.com/media/FHhOi6Moto68gNyafW/giphy.gif', 'https://media.giphy.com/media/Qf0udrUFdPRcgyTpp0/giphy.gif', 'https://media.giphy.com/media/RTxUucAqSFMT8xtK0Q/giphy.gif', 'https://media.giphy.com/media/FQL3zfy80vCe7OFnE2/giphy.gif', 'https://media.giphy.com/media/MuRcAxHKqeiTzEuHpC/giphy.gif']
DIBBLERS_GIFS = ['https://media.giphy.com/media/ETDRQrFfcPKo1gvkSx/giphy.gif', 'https://media.giphy.com/media/pwTCAu1w6izTIZsqVD/giphy.gif', 'https://media.giphy.com/media/PlpMSapjUC96ywP4HI/giphy.gif', 'https://media.giphy.com/media/wMPFGSSEB170mttNAJ/giphy.gif', 'https://media.giphy.com/media/3armSt6Qqwul8HwmIJ/giphy.gif', 'https://media.giphy.com/media/Ww3o6lZgrjldYKoHYb/giphy.gif']
ONEUP_GIFS = ['https://media.giphy.com/media/nNXcXGX65D5rXkpiJd/giphy.gif', 'https://media.giphy.com/media/492eHSGThgIDx0quLA/giphy.gif', 'https://media.giphy.com/media/vYHQeUQKiEKtjFmVVu/giphy.gif', 'https://media.giphy.com/media/r27ezJNGnlIN7eonmn/giphy.gif', 'https://media.giphy.com/media/p0DOA7vgjZIrofqP1K/giphy.gif', 'https://media.giphy.com/media/k9INvJjWU636EnqZv5/giphy.gif', 'https://media.giphy.com/media/bixPdyQVlFCOxWY5Gu/giphy.gif', 'https://media.giphy.com/media/9HhNfrAsBWoG0HpOSa/giphy.gif', 'https://media.giphy.com/media/7nRpNHtUBaw8Go5AwD/giphy.gif', 'https://media.giphy.com/media/zJcxfUcjEnHFeEJA3T/giphy.gif', 'https://media.giphy.com/media/PnFQRzb9JQUug3eqvE/giphy.gif', 'https://media.giphy.com/media/ikbRAXLsu6JfnRgSXX/giphy.gif', 'https://media.giphy.com/media/hwTPcbxWMtyc25CGyV/giphy.gif', 'https://media.giphy.com/media/KbdQyDNsPfSjG7kSVM/giphy.gif', 'https://media.giphy.com/media/dkluEGUKdIU1FX8Mlh/giphy.gif', 'https://media.giphy.com/media/0BZZjFyuoDIAR2sHvL/giphy.gif', 'https://media.giphy.com/media/4d2RQZH2tNni28rww9/giphy.gif', 'https://media.giphy.com/media/QXwknhHN7o04AeXcy9/giphy.gif', 'https://media.giphy.com/media/6UwssqVDmfSTAEYhjT/giphy.gif']


def read_config_file():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as configfile:
            configs = json.load(configfile)
            custom_prefixes = configs['custom_prefixes']

            return custom_prefixes
    else:
        return {}


def write_config_file(custom_prefixes):
    with open(CONFIG_FILE, 'w') as configfile:
        configfile.write(json.dumps({'custom_prefixes': custom_prefixes}))


async def determine_prefix(bot, message):

    guild = message.guild
    #Only allow custom prefixes in guild
    if guild:
        return custom_prefixes.get(str(guild.id), default_prefix)
    else:
        return default_prefix


def determine_native_token(ctx):
    guild = str(ctx.message.guild)

    if not guild:
        return DEFAULT_TOKEN_NAME

    if guild == 'Hive Pizza':
        return DEFAULT_TOKEN_NAME
    elif guild == 'Rising Star Game':
        return 'STARBITS'
    elif guild == 'The Man Cave':
        return 'BRO'
    elif guild == 'CTP Talk':
        return 'CTP'
    elif guild == 'HiveLIST':
        return 'LIST'
    elif guild == 'HiveHustlers':
        return 'COM'
    else:
        return DEFAULT_TOKEN_NAME


def get_market_history(symbol):

    order_count = 1000
    orders = []
    while order_count == 1000:
        response = market.get_trades_history(symbol, limit=1000, offset=len(orders))
        order_count = len(response)
        orders += response

    return orders


def get_token_holders(symbol):

    holder_count = 1000
    token_holders = []
    while holder_count == 1000:
        response = Token(symbol, api=hiveengine_api).get_holder(offset=len(token_holders))
        holder_count = len(response)
        token_holders += response

    return token_holders


def get_token_price_he_cg(coin):
    coin = coin.lower()

    if coin == 'eth':
        coin = 'ethereum'
    elif coin == 'btc':
        coin = 'bitcoin'
    elif coin == 'cro':
        coin = 'crypto-com-chain'
    elif coin == 'polygon' or coin == 'matic':
        coin = 'matic-network'
    elif coin == 'hbd':
        coin = 'hive_dollar'

    found_in_hiveengine = False
    try:
        Token(coin, api=hiveengine_api)
        found_in_hiveengine = True
        hive_usd = get_coin_price()[0]

        last_price = 0.0
        lowest_asking_price = 0.0
        highest_bidding_price = 0.0

        trade_history = get_market_history(symbol=coin)
        if trade_history:
            last_price = float(trade_history[-1]['price'])
        last_usd = last_price * hive_usd

        sell_book = market.get_sell_book(symbol=coin, limit=1000)
        sell_book = sorted(sell_book, key=lambda a: float(a['price']), reverse=False)
        if sell_book:
            lowest_asking_price = float(sell_book[0]['price'])
        ask_usd = lowest_asking_price * hive_usd

        buy_book = market.get_buy_book(symbol=coin, limit=1000)
        buy_book = sorted(buy_book, key=lambda a: float(a['price']), reverse=True)
        if buy_book:
            highest_bidding_price = float(buy_book[0]['price'])
        bid_usd = highest_bidding_price * hive_usd

        volume_data = requests.get(MARKET_HISTORY_URL % coin.upper()).json()
        volume_str = '%s %s | %s HIVE\n' % (volume_data[0]['volumeToken'], volume_data[0]['symbol'], volume_data[0]['volumeHive'])

        embed = discord.Embed(title='Hive-Engine market info for $%s' % coin.upper(), last_usd='', color=0xf3722c)
        embed.add_field(name='Last', value='%.5f HIVE | $%.5f USD' % (last_price, last_usd), inline=False)
        embed.add_field(name='Ask', value='%.5f HIVE | $%.5f USD' % (lowest_asking_price, ask_usd), inline=False)
        embed.add_field(name='Bid', value='%.5f HIVE | $%.5f USD' % (highest_bidding_price, bid_usd), inline=False)
        embed.add_field(name='Today Volume', value=volume_str, inline=False)
        return embed

    except hiveengine.exceptions.TokenDoesNotExists:
        print('Token not found in HE, trying CoinGeckoAPI')

    if not found_in_hiveengine:
        price, daily_change, daily_volume = get_coin_price(coin)

        if int(price) == -1:
            message = 'Failed to find coin or token called $%s' % coin
        else:
            message = '''```fix
market price: $%.5f USD
24 hour change: %.3f%%
24 hour volume: $%s USD
```''' % (price, daily_change, "{:,.2f}".format(daily_volume))

        embed = discord.Embed(title='CoinGecko market info for $%s' % coin.upper(), description=message, color=0xf3722c)
        return embed


def get_coin_price(coin='hive'):
    ''' Call into coingeck to get USD price of coins i.e. $HIVE '''
    coingecko = CoinGeckoAPI()
    response = coingecko.get_price(ids=coin, vs_currencies='usd', include_24hr_change='true', include_24hr_vol='true')

    if coin not in response.keys():
        print('Error calling CoinGeckoAPI for %s price' % coin)
        return -1

    subresponse = response[coin]
    if 'usd' not in subresponse.keys():
        print('Error 2 calling CoinGeckoAPI for %s price' % coin)
        return -1

    return float(subresponse['usd']), float(subresponse['usd_24h_change']),  float(subresponse['usd_24h_vol'])


async def update_bot_user_status(bot):
    """Update the bot's status."""
    last_price = float(get_market_history(symbol=DEFAULT_TOKEN_NAME)[-1]['price'])
    last_price_usd = round(get_coin_price()[0] * last_price, 3)
    if bot:
        await bot.change_presence(activity=discord.Game('PIZZA ~ $%.3f USD' % last_price_usd))


custom_prefixes = read_config_file()
default_prefix = '!'
bot = commands.Bot(command_prefix=determine_prefix, intents=discord.Intents.default())
slash = SlashCommand(bot)


@bot.event
async def on_ready():
    """Event handler for bot comnnection."""
    print(f'{bot.user} has connected to Discord!')
    await update_bot_user_status(bot)


class PizzaCog(commands.Cog):
    """This is a cog to peridiocally update the TOKEN price in bot status."""

    def __init__(self, bot):
        """Constructor."""
        self.price_check.start()
        self.bot = bot

    def cog_unload(self):
        """Stop the task loop on shutdown."""
        self.price_check.cancel()

    @tasks.loop(minutes=1.0)
    async def price_check(self):
        """Task to run every N execution."""
        if self.bot.user:
            await update_bot_user_status(self.bot)

cog = PizzaCog(bot)

# Bot commands


@bot.command()
@commands.guild_only()
async def prefix(ctx, arg=''):
    """<prefix> : Admin-only - print and change bot's command prefix."""
    # get current prefix

    if arg == '':
        prefix = await determine_prefix(bot, ctx.message)
        guild = ctx.message.guild

        await ctx.send('Current prefix is: %s for guild: %s' % (prefix,guild))

    else:
        guild = ctx.message.guild
        if not ctx.message.author.guild_permissions.administrator:
            await ctx.send('You must be an admin to change my command prefix for guild: %s' % (guild))
            return

        custom_prefixes[str(guild.id)] = arg
        await ctx.send('Changed prefix to: %s for guild: %s' % (arg,guild))
        write_config_file(custom_prefixes)


def get_hive_power_delegations(wallet):
    """Get a total of incoming HP delegation to wallet."""
    acc = beem.account.Account(wallet, blockchain_instance=hive)

    incoming_delegations_total = 0

    delegations = acc.get_vesting_delegations()

    for delegation in delegations:
        hive_power = hive.vests_to_token_power(delegation['vesting_shares']['amount']) / 10 ** delegation['vesting_shares']['precision']
        incoming_delegations_total += hive_power

    return incoming_delegations_total


@bot.command()
async def bal(ctx, wallet, symbol=''):
    """<wallet> <symbol> : Print Hive-Engine wallet balances."""
    if not symbol:
        symbol = determine_native_token(ctx)

    symbol = symbol.upper()
    wallet = wallet.lower()

    if symbol.lower() == 'hive':
        acc = beem.account.Account(wallet)
        balance = acc.available_balances[0]
        staked = acc.get_token_power(only_own_vests=True)
        delegation_out = get_hive_power_delegations(wallet)
        delegation_in = acc.get_token_power() + delegation_out - staked

    else:
        # hive engine token
        wallet_token_info = Wallet(wallet, blockchain_instance=hive, api=hiveengine_api).get_token(symbol)

        if not wallet_token_info:
            balance = 0
            staked = 0
            delegation_in = 0
            delegation_out = 0
        else:
            balance = float(wallet_token_info['balance'])
            staked = float(wallet_token_info['stake'])
            delegation_in = float(wallet_token_info['delegationsIn'])
            delegation_out = float(wallet_token_info['delegationsOut'])

    embed = discord.Embed(title='Balances for @%s' % wallet, description='$%s' % symbol, color=0x336EFF)
    embed.add_field(name='Liquid', value='%0.3f' % (balance), inline=False)
    embed.add_field(name='Staked', value='%0.3f' % (staked), inline=False)

    if delegation_in > 0:
        embed.add_field(name='Incoming Delegation', value='%0.3f' % (delegation_in), inline=False)
    if delegation_out > 0:
        embed.add_field(name='Outgoing Delegation', value='%0.3f' % (delegation_out), inline=False)

    total = balance + staked + delegation_in - delegation_out
    embed.add_field(name='Total', value='%0.3f' % (total), inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def bals(ctx, wallet):
    """<wallet>: Print Hive-Engine wallet balances."""
    # hive engine token
    wallet = wallet.lower()
    wallet_token_info = Wallet(wallet, blockchain_instance=hive, api=hiveengine_api)

    # sort by stake then balance
    wallet_token_info.sort(key=lambda elem: float(elem['stake']) + float(elem['balance']), reverse=True)

    longest_symbol_len = 0
    for token in wallet_token_info:
        if len(token['symbol']) > longest_symbol_len:
            longest_symbol_len = len(token['symbol'])

    message_body = '```'
    message_body += 'SYMBOL'.ljust(longest_symbol_len, ' ') + ' |  LIQUID  |  STAKED  | INCOMING | OUTGOING\n'

    rows = []

    for token in wallet_token_info:
        symbol = token['symbol']
        balance = float(token['balance'])
        staked = float(token['stake'])
        delegation_in = float(token['delegationsIn'])
        delegation_out = float(token['delegationsOut'])

        if balance + staked + delegation_in + delegation_out == 0.0:
            continue

        padded_symbol = symbol.ljust(longest_symbol_len, ' ')
        rows.append('%s |%10.3f|%10.3f|%10.3f|%9.3f\n' % (padded_symbol, balance, staked, delegation_in, delegation_out))

    for row in rows[0:10]:
        message_body += row

    message_body += '```'

    embed = discord.Embed(title='First 10 balances for @%s' % wallet, description=message_body, color=0x90be6d)
    await ctx.send(embed=embed)


@bot.command()
async def price(ctx, symbol=''):
    """<symbol> : Print Hive-Engine / CoinGecko market price info."""
    if not symbol:
        symbol = determine_native_token(ctx)

    embed = get_token_price_he_cg(symbol)
    await ctx.send(embed=embed)


@slash.slash(name="gif")
async def gif(ctx, category=''):
    """ Drop a random GIF! Categories: pizza, bro, risingstar, pob, profound, battleaxe, englang, huzzah, beard, lego, blurt."""
    gif_set = PIZZA_GIFS

    if not category:
        guild = str(ctx.author.guild.name)
        if guild == 'Hive Pizza':
            gif_set = PIZZA_GIFS
        elif guild == 'Rising Star Game':
            gif_set = RISINGSTAR_GIFS
        else:
            gif_set = PIZZA_GIFS
    elif category.lower() == 'pizza':
        gif_set = PIZZA_GIFS
    elif category.lower() == 'bro':
        gif_set = BRO_GIFS
    elif category.lower() == 'risingstar':
        gif_set = RISINGSTAR_GIFS
    elif category.lower() == 'pob':
        gif_set = POB_GIFS
    elif category.lower() == 'profound':
        gif_set = PROFOUND_GIFS
    elif category.lower() == 'battleaxe':
        gif_set = BATTLEAXE_GIFS
    elif category.lower() == 'england':
        gif_set = ENGLAND_GIFS
    elif category.lower() == 'huzzah':
        gif_set = HUZZAH_GIFS
    elif category.lower() == 'beard':
        gif_set = BEARD_GIFS
    elif category.lower() == 'lego':
        gif_set = LEGO_GIFS
    elif category.lower() == 'blurt':
        gif_set = BLURT_GIFS
    elif category.lower() == 'foxon':
        gif_set = FOXON_GIFS
    elif category.lower() == 'stickup':
        gif_set = STICKUP_GIFS
    elif category.lower() == 'pineapple':
        gif_set = PINEAPPLE_GIFS
    elif category.lower() == 'dibblers':
        gif_set = DIBBLERS_GIFS
    elif category.lower() == 'cine':
        gif_set = CINE_GIFS
    elif category.lower() == '1up':
        gif_set = ONEUP_GIFS
    else:
        gif_set = PIZZA_GIFS

    gif_url = random.choice(gif_set)

    #embed = discord.Embed(title='.', color=0x43aa8b)
    #embed.set_image(url=gif_url)
    #await ctx.send(embed=embed)
    await ctx.send(gif_url)

@bot.command()
async def info(ctx):
    """ Print Hive.Pizza project link """
    response = '''Learn more about $PIZZA @ https://hive.pizza'''
    await ctx.send(response)


@bot.command()
async def tokenomics(ctx, symbol=''):
    """<symbol> : Print Hive-Engine token distribution info"""

    if not symbol:
        symbol = determine_native_token(ctx)
    symbol = symbol.upper()

    wallets = [x for x in get_token_holders(symbol) if x['account'] not in ACCOUNT_FILTER_LIST]

    total_wallets = len([x for x in wallets if float(x['balance']) + float(x['stake']) > 0])

    # count wallets with at least 1 token
    wallets_1plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 1])

    # count wallets with at least 20 tokens
    wallets_20plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 20])

    # count wallets with at least 200 tokens
    wallets_200plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 200])

    # count wallets with at least 1,000 tokens
    wallets_1000plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 1000])

    # count wallets with at least 10,000 tokens
    wallets_10000plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 10000])

    # count wallets with at least 100,000 tokens
    wallets_100000plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 100000])

    # count wallets with at least 1,000,000 tokens
    wallets_1000000plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 1000000])

    # count wallets with at least 10,000,000 tokens
    wallets_10000000plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 10000000])

        # count wallets with at least 100,000,000 tokens
    wallets_100000000plus = len([x for x in wallets if float(x['balance']) + float(x['stake']) >= 100000000])



    message = '''```
%.4d wallets hold >            0 $%s
%.4d wallets hold >=          20 $%s
%.4d wallets hold >=         200 $%s
%.4d wallets hold >=       1,000 $%s
%.4d wallets hold >=      10,000 $%s
%.4d wallets hold >=     100,000 $%s
%.4d wallets hold >=   1,000,000 $%s
%.4d wallets hold >=  10,000,000 $%s
%.4d wallets hold >= 100,000,000 $%s
```''' % (total_wallets, symbol, wallets_20plus, symbol, wallets_200plus, symbol, wallets_1000plus, symbol, wallets_10000plus, symbol, wallets_100000plus, symbol, wallets_1000000plus, symbol, wallets_10000000plus, symbol, wallets_100000000plus, symbol)

    embed = discord.Embed(title='$%s Token Distribution' % symbol, description=message, color=0x43aa8b)
    await ctx.send(embed=embed)

@bot.command()
async def top10(ctx, symbol=''):
    """<symbol> : Print Hive-Engine token rich list top 10"""

    if not symbol:
        symbol = determine_native_token(ctx)

    accounts = [x for x in get_token_holders(symbol) if x['account'] not in ACCOUNT_FILTER_LIST]

    # identify the top 10 token holders
    symbol = symbol.upper()

    embed = discord.Embed(title='Top 10 $%s Holders' % symbol, description='', color=0xf8961e)

    accounts_stake = sorted(accounts, key=lambda a: float(a['stake']), reverse=True)
    top10stake = [(x['account'], float(x['stake'])) for x in accounts_stake[0:10]]
    count = 0
    stake_string = ''
    for account, stake in top10stake:
        count += 1
        stake_string += '%d. %s - %0.3f\n' % (count, account, stake)
    embed.add_field(name='Top 10 $%s Staked' % symbol, value=stake_string, inline=True)

    accounts_liquid = sorted(accounts, key=lambda a: float(a['balance']), reverse=True)
    top10liquid = [(x['account'], float(x['balance'])) for x in accounts_liquid[0:10]]
    count = 0
    liquid_string = ''
    for account, liquid in top10liquid:
        count += 1
        liquid_string += '%d. %s - %0.3f\n' % (count, account, liquid)
    embed.add_field(name='Top 10 $%s Liquid' % symbol, value=liquid_string, inline=True)

    accounts_total = sorted(accounts, key=lambda a: float(a['stake']) + float(a['balance']), reverse=True)
    top10total = [(x['account'], float(x['stake']) + float(x['balance'])) for x in accounts_total[0:10]]
    count = 0
    total_string = ''
    for account, total in top10total:
        count += 1
        total_string += '%d. %s - %0.3f\n' % (count, account, total)
    embed.add_field(name='Top 10 $%s Total' % symbol, value=total_string, inline=True)


    await ctx.send(embed=embed)


@bot.command()
async def history(ctx, symbol=''):
    """<symbol> : Print recent Hive-Engine token trade history"""
    if symbol == '':
        symbol = determine_native_token(ctx)

    message = '''```fix
'''

    for tx in get_market_history(symbol)[::-1][0:10]:
        message += '%0.4f @ %0.4f HIVE: %s -> %s\n' % (float(tx['quantity']), float(tx['price']), tx['seller'], tx['buyer'])

    message += '```'


    embed = discord.Embed(title='Latest 10 $%s Hive-Engine Transactions' % symbol, description=message, color=0x277da1)
    await ctx.send(embed=embed)


@bot.command()
async def blog(ctx, name):
    """<name> : Link to last post from blog"""

    from beem.discussions import Query, Discussions_by_blog
    q = Query(limit=10, tag=name)
    latest_blog = Discussions_by_blog(q)[0]

    reply_identifier = '@%s/%s' % (latest_blog['author'], latest_blog['permlink'])

    response = 'Latest post from @%s: https://peakd.com/%s' % (name, reply_identifier)

    await ctx.send(response)


@bot.command()
async def witness(ctx, name='pizza.witness'):
    """<witness name>: Print Hive Witness Info"""
    name = name.lower()
    message_body = '```\n'

    hive = beem.Hive()
    witness = Witness(name, blockchain_instance=hive)

    witness_json = witness.json()
    witness_schedule = hive.get_witness_schedule()
    config = hive.get_config()
    if "VIRTUAL_SCHEDULE_LAP_LENGTH2" in config:
        lap_length = int(config["VIRTUAL_SCHEDULE_LAP_LENGTH2"])
    elif "HIVE_VIRTUAL_SCHEDULE_LAP_LENGTH2" in config:
        lap_length = int(config["HIVE_VIRTUAL_SCHEDULE_LAP_LENGTH2"])
    else:
        lap_length = int(config["STEEM_VIRTUAL_SCHEDULE_LAP_LENGTH2"])
    rank = 0
    active_rank = 0
    found = False
    witnesses = WitnessesRankedByVote(limit=101, blockchain_instance=hive)
    vote_sum = witnesses.get_votes_sum()
    for w in witnesses:
        rank += 1
        if w.is_active:
            active_rank += 1
        if w["owner"] == witness["owner"]:
            found = True
            break
    virtual_time_to_block_num = int(witness_schedule["num_scheduled_witnesses"]) / (lap_length / (vote_sum + 1))

    virtual_diff = int(witness_json["virtual_scheduled_time"]) - int(witness_schedule['current_virtual_time'])
    block_diff_est = virtual_diff * virtual_time_to_block_num
    est_time_to_next_block = ''
    if active_rank > 20:
        next_block_s = int(block_diff_est) * 3
        next_block_min = next_block_s / 60
        next_block_h = next_block_min / 60
        next_block_d = next_block_h / 24
        time_diff_est = ""
        if next_block_d > 1:
            time_diff_est = "%.2f days" % next_block_d
        elif next_block_h > 1:
            time_diff_est = "%.2f hours" % next_block_h
        elif next_block_min > 1:
            time_diff_est = "%.2f minutes" % next_block_min
        else:
            time_diff_est = "%.2f seconds" % next_block_s
        est_time_to_next_block = time_diff_est

    embed = discord.Embed(title='Hive Witness info for @%s' % name, description='', color=0xf3722c)
    embed.add_field(name='Running Version', value=witness_json['running_version'], inline=False)
    embed.add_field(name='Missed Blocks', value=witness_json['total_missed'], inline=False)

    if est_time_to_next_block:
        embed.add_field(name='Estimate time to next block', value=est_time_to_next_block, inline=False)

    if found:
        embed.add_field(name='Rank', value='%d' % rank, inline=False)
        embed.add_field(name='Active Rank', value='%d' % active_rank, inline=False)


    await ctx.send(embed=embed)


@bot.command()
async def hewitness(ctx, name='pizza-engine'):
    """<witness name>: Print Hive-Engine Witness Info"""

    results = hiveengine_api.find('witnesses', 'witnesses', query={"account":{"$in":["%s" % name]}})

    embed = discord.Embed(title='Hive-Engine Witness info for @%s' % name, description='', color=0xf3722c)
    
    if len(results) == 0:
        embed.add_field(name='Hive-Engine Witness %s' % name, value='Not Found')
    else:
        result = results[0]
        for key in result.keys():
            if key not in ['_id','signingKey','IP','RPCPort','P2PPort','approvalWeight']:
                embed.add_field(name=key, value=result[key], inline=True)


    await ctx.send(embed=embed)


@bot.command()
async def pools(ctx, wallet):
    """<wallet>: Check Hive-Engine DIESEL Pool Balances for Wallet"""

    results = hiveengine_api.find('marketpools', 'liquidityPositions', query={"account":"%s" % wallet})
    embed = discord.Embed(title='DIESEL Pool info for @%s' % wallet, description='', color=0xf3722c)

    for result in results:
        embed.add_field(name=result['tokenPair'], value='%0.3f shares' % float(result['shares']), inline=True)

    await ctx.send(embed=embed)


@bot.command()
async def pool(ctx, pool=DEFAULT_DIESEL_POOL):
    """<pool>: Check Hive-Engine DIESEL Pool Info"""
    pool = pool.upper()

    results = hiveengine_api.find('marketpools', 'pools', query={"tokenPair":{"$in":["%s" % pool]}})

    embed = discord.Embed(title='DIESEL Pool info for %s' % pool, description='', color=0xf3722c)

    if len(results) == 0:
        embed.add_field(name='DIESEL Pool %s' % pool, value='Not Found')
    else:
        result = results[0]
        for key in result.keys():
            if key not in ['_id','precision','creator']:
                embed.add_field(name=key, value=result[key], inline=True)


        results = hiveengine_api.find('marketpools', 'liquidityPositions', query={"tokenPair":{"$in":["%s" % pool]}})
        results = sorted(results, key= lambda a: float(a['shares']), reverse=True)[0:13]
        for result in results:
            embed.add_field(name='LP: %s' % result['account'], value='%0.3f shares' % float(result['shares']), inline=True)
        embed.add_field(name='LP: ...', value='... shares', inline=True)

    await ctx.send(embed=embed)


@bot.command()
async def poolrewards(ctx, pool=DEFAULT_DIESEL_POOL):
    """<pool>: Check Hive-Engine DIESEL Pool Rewards Info"""
    pool = pool.upper()

    query = {
        "tokenPair": {
            "$in": ["%s" % pool]
        }
    }

    results = hiveengine_api.find('distribution', 'batches', query=query)

    embed = discord.Embed(title='DIESEL Pool Rewards for %s' % pool, description='', color=0xf3722c)

    if len(results) == 0:
        embed.add_field(name='DIESEL Pool %s' % pool, value='Not Found')
    else:
        result = results[0]

        embed.add_field(name='Payouts', value=result['numTicks'], inline=True)
        embed.add_field(name='Payouts Remaining', value=result['numTicksLeft'], inline=True)

        embed.add_field(name='Last Payout Time', value='%s' % datetime.datetime.fromtimestamp(result['lastTickTime'] / 1000))

        tokens = result['tokenBalances']
        for token in tokens:
            embed.add_field(name=token['symbol'], value='%0.3f' % float(token['quantity']), inline=True)

    await ctx.send(embed=embed)


@bot.command()
async def buybook(ctx, symbol=''):
    """<symbol>: Check Hive-Engine buy book for token"""
    if not symbol:
        symbol = determine_native_token(ctx)

    buy_book = market.get_buy_book(symbol=symbol, limit=1000)
    buy_book = sorted(buy_book, key= lambda a: float(a['price']), reverse=True)
    buy_book = buy_book[0:10]

    embed = discord.Embed(title='Buy Book for $%s (first 10 orders)' % symbol.upper(), description='', color=0xf3722c)

    for row in buy_book:
        embed.add_field(value=row['account'], name='%0.3f @ %0.3f HIVE' % (float(row['quantity']),float(row['price'])), inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def sellbook(ctx, symbol=''):
    """<symbol>: Check Hive-Engine sell book for token"""

    if not symbol:
        symbol = determine_native_token(ctx)

    sell_book = market.get_sell_book(symbol=symbol, limit=1000)
    sell_book = sorted(sell_book, key= lambda a: float(a['price']), reverse=False)
    sell_book = sell_book[0:10]

    embed = discord.Embed(title='Sell Book for $%s (first 10 orders)' % symbol.upper(), description='', color=0xf3722c)

    for row in sell_book:
        embed.add_field(value=row['account'], name='%0.3f @ %0.3f HIVE' % (float(row['quantity']),float(row['price'])), inline=False)

    await ctx.send(embed=embed)


@bot.command()
async def dluxnodes(ctx):
    """Check DLUX Nodes Status"""
    coinapi = 'http://dlux-token.herokuapp.com'
    runners = requests.get('%s/runners' % coinapi).json()['runners']
    queue = requests.get('%s/queue' % coinapi).json()['queue']

    embed = discord.Embed(title='DLUX Nodes in Consensus:', description='', color=0x336EFF)

    for account in queue:
        icon = ':eye:'
        if account in runners.keys():
            icon = ':closed_lock_with_key:'
        embed.add_field(name=account, value=icon, inline=True)

    await ctx.send(embed=embed)


# Splinterlands related helper functions and commands

def get_sl_guild_member_list():
    """Get a list of Splinterlands guild members."""
    GUILD_IDS = ['d258d4e976c88fe47ca89f987f52efaf305b2ccf',
                 '00fbd7938f9a652883e9b50f1a93c324b3646f0e',
                 'e498ee4a940b47b396ca9b8470f9d8d8d9301f06']
    __url__ = 'https://api2.splinterlands.com/'

    member_list = []

    for guild_id in GUILD_IDS:

        response = None
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            query = __url__ + "guilds/members?guild_id=" + guild_id

            try:
                response = requests.get(query)
            except:
                response = 'ERROR'

            if str(response) != '<Response [200]>':
                sleep(1)
            cnt2 += 1

        member_list += [row['player'] for row in response.json() if row['status'] == 'active']

    return member_list


def get_sl_guild_donations():
    """Get a list of DEC guild donations."""
    GUILD_IDS = ['d258d4e976c88fe47ca89f987f52efaf305b2ccf',
                 '00fbd7938f9a652883e9b50f1a93c324b3646f0e',
                 'e498ee4a940b47b396ca9b8470f9d8d8d9301f06']
    __url__ = 'https://api2.splinterlands.com/'

    contributions = {}

    for guild_id in GUILD_IDS:

        response = None
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            query = __url__ + "guilds/members?guild_id=" + guild_id

            try:
                response = requests.get(query)
            except:
                response = 'ERROR'

            if str(response) != '<Response [200]>':
                sleep(1)
            cnt2 += 1

        guild_info = response.json()

        for row in guild_info:
            if row['status'] != 'active':
                continue
            contributions[row['player']] = json.loads(row['data'])['contributions']

    return contributions


def get_sl_card_collection(player):
    """Git a list of cards in a players Splinterlands collection."""
    cards = requests.get('https://api2.splinterlands.com/cards/collection/%s' % player).json()['cards']
    return cards


@bot.command()
async def sl(ctx, subcommand, arg):
    """player <player>: Check Splinterlands Player Stats.
       guildteamwork: Only available in HivePizza discord."""
    GUILD_IDS = ['d258d4e976c88fe47ca89f987f52efaf305b2ccf',
                 '00fbd7938f9a652883e9b50f1a93c324b3646f0e',
                 'e498ee4a940b47b396ca9b8470f9d8d8d9301f06']

    if subcommand == 'player':
        player = arg
        api = 'https://api2.splinterlands.com/players/details?name=%s' % player

        profile = requests.get(api).json()

        embed = discord.Embed(title='Splinterlands profile for %s:' % player, description='', color=0x336EFF)

        for k in profile.keys():
            if k not in ['guild', 'display_name', 'season_details', 'adv_msg_sent']:
                prettyname = k.replace('_',' ').title()
                embed.add_field(name=prettyname, value=profile[k], inline=True)

        await ctx.send(embed=embed)

    elif subcommand == 'guild' and arg == 'teamwork':
        if str(ctx.message.guild) != 'Hive Pizza':
            await ctx.send('Command only available in Hive Pizza discord')
            return

        delegations = {}

        guild_member_list = get_sl_guild_member_list()
        guild_member_list_ext = [('cryptoniusrex', 'cryptoniusraptor')]

        delegations_string = ''
        for member in guild_member_list:
            delegations[member] = 0

            for card in get_sl_card_collection(member):
                if card['player'] == member and 'delegated_to' in card.keys() and card['delegated_to'] in guild_member_list:
                    delegations[member] += 1

        for ext_name, int_name in guild_member_list_ext:
            for card in get_sl_card_collection(ext_name):
                if card['player'] == ext_name and 'delegated_to' in card.keys() and card['delegated_to'] in guild_member_list:
                    if card['delegated_to'] != int_name:
                        delegations[int_name] += 1

        list_delegations = list(delegations.items())
        list_delegations.sort(key=lambda tup: tup[1], reverse=True)
        for delegation in list_delegations:
            if delegation[1] > 0:
                delegations_string += '%s - %d cards\n' % (delegation[0],delegation[1])

        # Fetch DEC donations info
        donations = get_sl_guild_donations()

        donations_string = ''

        list_donations = []
        for member in donations.keys():
            if donations[member]:
                cur_donation = donations[member]
                total_dec_donated = 0
                for key in ['barracks','arena','guild_shop']:
                    if key in donations[member].keys() and 'DEC' in donations[member][key].keys():
                        total_dec_donated += donations[member][key]['DEC']

                for key in ['guild_hall']:
                    if key in donations[member].keys():
                        total_dec_donated += donations[member][key]

                list_donations.append((member,total_dec_donated))

        list_donations.sort(key=lambda tup: tup[1], reverse=True)
        for donation in list_donations:
            if donation[1] > 0:
                donations_string += '%s - %d DEC\n' % (donation[0], donation[1])

        embed = discord.Embed(title='Teamwork Leaderboard for PIZZA Guilds', description='', color=0x336EFF)
        embed.add_field(name='Card delegations to Guildmates', value=delegations_string, inline=True)
        embed.add_field(name='DEC donations', value=donations_string, inline=True)
        await ctx.send(embed=embed)

    elif subcommand == 'brawl' and arg == 'timer':
        embed = discord.Embed(title='Brawl Timers for PIZZA Guilds', description='', color=0x336EFF)
        for guild_id in GUILD_IDS:
            # get brawl ID
            api = 'https://api2.splinterlands.com/guilds/find?id=%s&ext=brawl' % guild_id
            guild_info = requests.get(api).json()
            guild_name = guild_info['name']
            brawl_id = guild_info['tournament_id']
            tournament_status = guild_info['tournament_status']

            # get brawl start time
            api = 'https://api2.splinterlands.com/tournaments/find_brawl?id=%s&guild_id=%s' % (brawl_id, guild_id)
            brawl_start_time = requests.get(api).json()['start_date']
            combat_start_time = dateutil.parser.isoparse(brawl_start_time).replace(tzinfo=None)
            combat_end_time = combat_start_time + timedelta(hours=48)
            now = datetime.utcnow()

            if now < combat_start_time:
                time_remaining = combat_start_time - now
                embed.add_field(name=guild_name, value='Combat starts in: %s' % time_remaining, inline=False)
            elif tournament_status == 2:
                embed.add_field(name=guild_name, value='Waiting for next brawl', inline=False)
            else:
                time_remaining = combat_end_time - now
                embed.add_field(name=guild_name, value='Combat ends in: %s' % time_remaining, inline=False)

        await ctx.send(embed=embed)

    elif subcommand == 'brawl' and arg == 'status':
        if str(ctx.message.guild) != 'Hive Pizza':
            await ctx.send('Command only available in Hive Pizza discord')
            return
        embed = discord.Embed(title='Brawl Status for PIZZA Guilds', description='', color=0x336EFF)
        for guild_id in GUILD_IDS:
            # get brawl ID
            api = 'https://api2.splinterlands.com/guilds/find?id=%s&ext=brawl' % guild_id
            guild_info = requests.get(api).json()
            brawl_id = guild_info['tournament_id']

            # get brawl start time
            api = 'https://api2.splinterlands.com/tournaments/find_brawl?id=%s&guild_id=%s' % (brawl_id, guild_id)
            brawl_info = requests.get(api).json()

            pizza_guild_index = list(map(itemgetter('id'), brawl_info['guilds'])).index(guild_id)
            pizza_guild = brawl_info['guilds'][pizza_guild_index]

            embed.add_field(name='%s - %s' % (guild_info['name'], '#%d' % (pizza_guild_index + 1)),
                            value='Remaining Battles: %d' % (pizza_guild['total_battles'] - pizza_guild['completed_battles']),
                            inline=False)
            embed.add_field(name='Wins',
                            value='%d' % pizza_guild['wins'],
                            inline=True)
            embed.add_field(name='Losses',
                            value='%d' % pizza_guild['losses'],
                            inline=True)
            embed.add_field(name='Draws',
                            value='%d' % pizza_guild['draws'],
                            inline=True)
        await ctx.send(embed=embed)

    elif subcommand == 'guild' and arg == 'power':
        if str(ctx.message.guild) != 'Hive Pizza':
            await ctx.send('Command only available in Hive Pizza discord')
            return
        guild_members = get_sl_guild_member_list()

        api = 'https://api2.splinterlands.com/settings'
        games_settings = requests.get(api).json()
        leagues = games_settings['leagues']

        embed = discord.Embed(title='Collection Power Check for PIZZA Guilds', description='', color=0x336EFF)

        for member in guild_members:
            api = 'https://api2.splinterlands.com/players/details?name=%s' % member
            member_info = requests.get(api).json()
            member_rating = member_info['rating']
            member_power = member_info['collection_power']

            for league in leagues[::-1]:
                if member_rating > league['min_rating'] and member_power < league['min_power']:
                    missing_power = int(league['min_power']) - int(member_power)
                    message = '%s can advance to %s league but needs %d more power.' % (member.title(), league['name'], missing_power)
                    embed.add_field(name=member.title(),
                                    value=message,
                                    inline=False)
                    break

        await ctx.send(embed=embed)

# Exode related commands

@bot.command()
async def exodecards(ctx, player):
    """<player>: Get a player's Exode card collection info."""
    api = 'https://digitalself.io/api_feed/exode/my_delivery_api.php?account=%s&filter=singleCards' % player
    cards = requests.get(api).json()['elements']
    market_prices = [card['market_price'] for card in cards]

    elite_cards = [card for card in cards if card['is_elite']]

    packsapi = 'https://digitalself.io/api_feed/exode/my_delivery_api.php?account=%s&filter=packs' % player
    packs = requests.get(packsapi).json()['elements']
    pack_market_prices = [pack['market_price'] for pack in packs]

    embed = discord.Embed(title='Exode cards for %s:' % player, description='', color=0x336EFF)
    embed.add_field(name='Card count', value=len(cards), inline=True)
    embed.add_field(name='Elite card count', value=len(elite_cards), inline=True)
    embed.add_field(name='Packs count', value=len(packs), inline=True)
    embed.add_field(name='Total market value', value='$%0.3f' % (sum(market_prices)+sum(pack_market_prices)), inline=True)


    await ctx.send(embed=embed)


# Rising Star related commands

@bot.command()
async def rsplayer(ctx, player):
    """<player>: Check Rising Star Player Stats."""
    api = 'https://www.risingstargame.com/playerstats.asp?player=%s' % player

    profile = requests.get(api).json()[0]

    embed = discord.Embed(title='Rising Star Profile for @%s' % player, description='', color=0xf3722c)

    for k in profile.keys():
        if k not in ['name']:
            prettyname = k.title()
            if prettyname == 'Missionego':
                prettyname = 'Mission Ego'
            elif prettyname == 'Lessonskill':
                prettyname = 'Lesson Skill'
            elif prettyname == 'Totalnfts':
                prettyname = 'Total NFTs'
            elif prettyname == 'Cardsfans':
                prettyname = 'Cards Fans'
            elif prettyname == 'Cardskill':
                prettyname = 'Cards Skill'
            elif prettyname == 'Cardsluck':
                prettyname = 'Cards Luck'
            elif prettyname == 'Cardsim':
                prettyname = 'Cards Income'

            embed.add_field(name=prettyname, value=profile[k], inline=True)

    await ctx.send(embed=embed)


## Hash Kings commands
@slash.slash(name='hkplayer')
async def hkplayer(ctx, player):
    """Fetch HashKings player info."""

    api = 'https://hashkings.xyz/userdata/%s' % player
    profile = requests.get(api).json()

    embed = discord.Embed(title='Hash Kings Profile for @%s' % player, description='', color=0xf3722c)

    message = 'Hash Kings profile for %s\n' % player
    for key in ['plotCount', 'seedCount', 'xp', 'lvl']:
        prettyname = key
        if prettyname == 'plotCount':
            prettyname = 'Plot Count'
        elif prettyname == 'seedCount':
            prettyname = 'Seed Count'
        elif prettyname == 'xp':
            prettyname = 'XP'
        elif prettyname == 'lvl':
            prettyname = 'Level'

        embed.add_field(name=prettyname, value=profile[key], inline=True)

    embed.add_field(name='Buds', value=profile['tokens']['buds']['balance'], inline=True)
    embed.add_field(name='Mota', value=profile['tokens']['mota']['balance'], inline=True)
    embed.add_field(name='Mota (staked)', value=profile['tokens']['mota']['stake'], inline=True)
    embed.add_field(name='HKWater', value=profile['tokens']['hkwater']['balance'], inline=True)

    await ctx.send(embed=embed)


@bot.command()
async def apr(ctx, delegation_amount, pool_size=350):
    """<delegation amount>: Calculate approx. APR for HP delegation."""

    reward_pool_size = float(pool_size)

    # get incoming delegation to hive.pizza
    wallet = 'hive.pizza'
    acc = beem.account.Account(wallet, blockchain_instance=hive)
    balance = acc.available_balances[0]
    staked = acc.get_token_power(only_own_vests=True)
    delegation_out = get_hive_power_delegations(wallet)
    delegation_in = acc.get_token_power() + delegation_out - staked

    shares = float(delegation_amount) / delegation_in

    approx_payout = round(reward_pool_size * shares, 2)

    # get current TOKEN price
    last_price = float(get_market_history(symbol=DEFAULT_TOKEN_NAME)[-1]['price'])
    last_price_usd = round(get_coin_price()[0] * last_price, 3)

    est_payout_value_hive = approx_payout * last_price

    annualized_payout = 365 * est_payout_value_hive

    annualized_pct = round(annualized_payout / float(delegation_amount), 3)

    await ctx.send('Approx. daily payout: %0.2f $PIZZA | Market value: %0.3f HIVE | APR: %0.3f%%' % (approx_payout, est_payout_value_hive, annualized_pct * 100))


@bot.command()
async def PIZZA(ctx):
    """Discord tips aren't supported. Use @tip.cc instead."""
    await ctx.send('Sorry, the !PIZZA tipping command only works in Hive comments. Use @tip.cc if you want to send a tip in Discord!')


@bot.command()
async def links(ctx):
    """Use these links to support Hive.Pizza."""
    embed = discord.Embed(title='Hive.Pizza links', description='Please consider supporting Hive.Pizza by using these referral links.', color=0xf3722c)
    embed.add_field(name='Hive Signup (1)', value='https://hive.pizza/hiveonboard', inline=False)
    embed.add_field(name='Hive Signup (2)', value='https://hive.pizza/ecency', inline=False)
    embed.add_field(name='Splinterlands', value='https://hive.pizza/splinterlands', inline=False)
    embed.add_field(name='Exode', value='https://hive.pizza/exode', inline=False)
    embed.add_field(name='Rising Star', value='https://hive.pizza/risingstar', inline=False)
    embed.add_field(name='NFTShowroom', value='https://hive.pizza/nftshowroom', inline=False)
    embed.add_field(name='top.gg (Vote for our Discord server to become awesome)', value='https://hive.pizza/vote', inline=False)

    await ctx.send(embed=embed)


@slash.slash(name="rc")
async def rc(ctx, wallet):
    """Print Hive resource credits info for wallet."""
    rc = beem.rc.RC(hive_instance=hive)
    comment_cost = rc.comment()
    vote_cost = rc.vote()
    json_cost = rc.custom_json()
    account_cost = rc.claim_account()

    acc = beem.account.Account(wallet, blockchain_instance=hive)
    mana = acc.get_rc_manabar()['current_mana']

    possible_jsons = int(mana / json_cost)
    possible_votes = int(mana / vote_cost)
    possible_comments = int(mana / comment_cost)
    possible_accounts = int(mana / account_cost)

    current_pct = float(acc.get_rc_manabar()['current_pct'])
    embed = discord.Embed(title='Hive Resource Credits for @%s' % wallet, description='RC manabar is at %0.3f%%' % current_pct, color=0xf3722c)
    embed.add_field(name='Account Claims ', value='~ %d' % possible_accounts, inline=True)
    embed.add_field(name='Comments/Posts', value='~ %d' % possible_comments, inline=True)
    embed.add_field(name='Votes', value='~ %d' % possible_votes, inline=True)
    embed.add_field(name='CustomJSONs', value='~ %d' % possible_jsons , inline=True)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Return a nice error message for unrecognized commands."""
    if isinstance(error, commands.CommandNotFound):
        prefix = await determine_prefix(bot, ctx.message)
        await ctx.send('I don\'t recognize the command. Try %shelp to see a list of commands' % prefix)
    else:
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


# Discord initialization
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
