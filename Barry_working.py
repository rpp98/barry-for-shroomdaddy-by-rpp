#RSI and OBV Divergence Indicator Bot created by rpp

import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import numpy
import aiohttp
import os

#Bot Command Prefix
bot = commands.Bot(command_prefix='$')

#Launching Barry Statement
@bot.event
async def on_ready():
    print('Ready to analyze')
    bot.loop.create_task(background_running_analysis())

#Result updater background task
async def background_running_analysis():
    #Run indefinitely
    results_dict = {}
    bot.results_dict = results_dict
    while True:
        #coin_failures are to keep track of which coins dont work (aka not enough data)
        coin_failures = ['DENTBTC', 'MFTBTC', 'KEYBTC', 'NASBTC', 'NPXSBTC', 'VENUSDT', 'DATABTC', 'NXSBTC', 'SCBTC', 'ETCUSDT', 'ICXUSDT', 'ONTUSDT', 'TUSDBTC','TRXUSDT', 'AGIBTC', 'QKCBTC']
        coin_list1 = ['NAVBTC'] #pour testing
        coin_list = ['ADABTC', 'ADXBTC', 'AEBTC', 'AIONBTC', 'AMBBTC', 'APPCBTC', 'ARKBTC', 'ARNBTC', 'ASTBTC', 'BATBTC', 'BCCBTC', 'BCDBTC', 'BCNBTC','BCPTBTC', 'BLZBTC', 'BNBBTC', 'BNTBTC', 'BQXBTC', 'BRDBTC', 'BTGBTC', 'BTSBTC', 'CDTBTC', 'CHATBTC', 'CLOAKBTC', 'CMTBTC', 'CNDBTC', 'DASHBTC', 'DGDBTC', 'DLTBTC', 'DNTBTC', 'EDOBTC', 'ELFBTC', 'ENGBTC', 'ENJBTC', 'EOSBTC', 'ETCBTC', 'ETHBTC', 'EVXBTC', 'FUELBTC', 'FUNBTC', 'GASBTC', 'GNTBTC','GRSBTC', 'GTOBTC', 'GVTBTC', 'GXSBTC', 'HSRBTC', 'ICNBTC', 'ICXBTC', 'INSBTC', 'IOSTBTC', 'IOTABTC', 'IOTXBTC', 'KMDBTC', 'KNCBTC', 'LENDBTC', 'LINKBTC', 'LOOMBTC', 'LRCBTC', 'LSKBTC', 'LTCBTC', 'LUNBTC', 'MANABTC', 'MCOBTC', 'MDABTC', 'MODBTC', 'MTHBTC', 'MTLBTC', 'NANOBTC', 'NAVBTC', 'NCASHBTC', 'NEBLBTC', 'NEOBTC', 'NULSBTC', 'OAXBTC', 'OMGBTC', 'ONTBTC', 'OSTBTC', 'PIVXBTC', 'POABTC', 'POEBTC', 'POWRBTC', 'PPTBTC', 'QLCBTC', 'QSPBTC', 'QTUMBTC', 'RCNBTC', 'RDNBTC', 'REPBTC','REQBTC', 'RLCBTC', 'RPXBTC', 'SALTBTC', 'SKYBTC','SNMBTC', 'SNTBTC', 'SNGLSBTC', 'STEEMBTC', 'STORJBTC', 'STRATBTC', 'SUBBTC', 'SYSBTC', 'THETABTC','TNBBTC', 'TNTBTC', 'TRIGBTC', 'TRXBTC', 'VIABTC', 'VIBBTC', 'VIBEBTC', 'WABIBTC', 'WANBTC', 'WAVESBTC', 'WINGSBTC', 'WPRBTC', 'WTCBTC', 'XEMBTC', 'XLMBTC', 'XMRBTC', 'XVGBTC', 'XRPBTC', 'XZCBTC', 'YOYOBTC', 'ZECBTC', 'ZENBTC','ZILBTC', 'ZRXBTC', 'ADAUSDT', 'BCCUSDT', 'BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'EOSUSDT', 'IOTAUSDT', 'LTCUSDT', 'NEOUSDT', 'QTUMUSDT', 'XLMUSDT', 'XRPUSDT']
        #Calculate for all time periods 
        time_periods1 = ['2h']
        time_periods = ['1h','2h','4h','6h','8h','12h','1d']
        for period in time_periods:
            results_fr = []
            results_current_div = []
            for coin in coin_list:
                normal_results = []
                results_cd = []           
                coin_data = await get_candles(coin,80,period)
                normal_results, results_current_div = analysis_RSIOBVMACD(coin,coin_data,normal_results,results_current_div)
                if len(normal_results) > 0:
                    for idx in range(len(normal_results)):
                        results_fr.append(normal_results[idx])
                if len(results_current_div) > 0:
                    for idx in range(len(results_current_div)):
                        results_cd.append(results_current_div[idx])
            results_dict[period] = (results_fr, results_cd)
            bot.results_dict = results_dict
            await asyncio.sleep(10)

#Bot commands for analysis results
@bot.command(pass_context=True)
async def histdiv(ctx,time_frame:str):
    valid_time_frames = ['1hour','2hour','4hour','6hour','8hour','12hour','1day']
    if time_frame not in valid_time_frames:
        await bot.say('Not a valid timeframe to analyze for')
        await bot.say('Valid Time Frames: {}'.format(valid_time_frames))
    else:
        #Retrieve results from background task
        tf_to_period = {'1hour':'1h','2hour':'2h','4hour':'4h','6hour':'6h','8hour':'8h','12hour':'12h','1day':'1d'}
        results_dict = bot.results_dict
        results_desired_fr,results_desired_cd = results_dict[tf_to_period[time_frame]]
        #Format results into lists of strings for embedding and avoiding max length for messages in discord and embeds and based on value of 'score'
        results_desired_fr = divs_filter(results_desired_fr,1)
        results_desired_fr = score_filter(results_desired_fr)
        full_results_sorted = sort_based_on_score(results_desired_fr)
        full_results_str_list = full_results_to_str(full_results_sorted)
        tf_converter_print = {'1hour':'1 hour','2hour':'2 hour','4hour':'4 hour','6hour':'6 hour','8hour':'8 hour','12hour':'12 hour','1day':'1 day'}
        #Print embed statements to Discord
        for idx in range(len(full_results_str_list)):
            embed_title = 'Historical Divergences within 42 periods for {} Candles: Part {} of {}'.format(tf_converter_print[time_frame],idx + 1,len(full_results_str_list))
            message = full_results_str_list[idx][0]
            embed = discord.Embed(title=embed_title,description=message)
            await bot.say(embed=embed)
            await asyncio.sleep(0.5)

@bot.command(pass_context=True)
async def currentdiv(ctx,time_frame:str):
    valid_time_frames = ['1hour','2hour','4hour','6hour','8hour','12hour','1day']
    if time_frame not in valid_time_frames:
        await bot.say('Not a valid timeframe to analyze for')
        await bot.say('Valid Time Frames are: {}'.format(valid_time_frames))
    else:
        #Retrieve results from background task
        tf_to_period = {'1hour':'1h','2hour':'2h','4hour':'4h','6hour':'6h','8hour':'8h','12hour':'12h','1day':'1d'}
        results_dict = bot.results_dict
        results_desired_fr,results_desired_cd = results_dict[tf_to_period[time_frame]]
        #Format results into lists of strings for embedding and avoiding max length for messages in discord and embeds and based on value of 'score'
        cd_results_sorted = sort_based_on_score(results_desired_cd)
        cdr_str_list = current_div_results_to_str(cd_results_sorted)

        tf_converter_print = {'1hour':'1 hour','2hour':'2 hour','4hour':'4 hour','6hour':'6 hour','8hour':'8 hour','12hour':'12 hour','1day':'1 day'}
        #Print embed statements to Discord
        for idx in range(len(cdr_str_list)):
            embed_title = '**Current Possible RSI Divergences:** Part {} of {}'.format(idx + 1,len(cdr_str_list))
            message = cdr_str_list[idx][0]
            embed = discord.Embed(title=embed_title,description=message)
            await bot.say(embed=embed)
            await asyncio.sleep(0.5)

@bot.command(pass_context=True)
async def tripdiv(ctx,time_frame:str):
    valid_time_frames = ['1hour','2hour','4hour','6hour','8hour','12hour','1day']
    if time_frame not in valid_time_frames:
        await bot.say('Not a valid timeframe to analyze for')
        await bot.say('Valid Time Frames are: {}'.format(valid_time_frames))
    else:
        #Retrieve results from background task
        tf_to_period = {'1hour':'1h','2hour':'2h','4hour':'4h','6hour':'6h','8hour':'8h','12hour':'12h','1day':'1d'}
        results_dict = bot.results_dict
        results_desired_fr,results_desired_cd = results_dict[tf_to_period[time_frame]]
        #Find triple divergences
        results_sorted = sort_based_on_score(results_desired_fr)
        trip_divs = find_tripdivs(results_sorted)
        #Format embed message for tripdivs
        tf_converter_print = {'1hour':'1 Hour','2hour':'2 Hour','4hour':'4 Hour','6hour':'6 Hour','8hour':'8 Hour','12hour':'12 Hour','1day':'1 Day'}
        msg_list = tripdivs_message(trip_divs)
        embed_title = 'Historical Triple Divergence(s) for {} Candles'.format(tf_converter_print[time_frame])
        embed = discord.Embed(title=embed_title,description='')
        for result in msg_list:
            for header,body in result.items():
                embed.add_field(name=header,value=body)
        await bot.say(embed=embed)
        
@bot.command(pass_context=True)
async def helpme(ctx):
    embed = discord.Embed(title='Help Guide',description='*A quick overview of the bot*')
    embed.set_author(name='Triple Divergence Indicator (RSI/OBV/MACD)')
    embed.add_field(name='Commands:',value='$helpme \n$histdiv (time frame) \n$currentdiv (time frame) \n$tripdiv (time frame) \n$howmany \n$coinsearch (COINPAIRING) \n$recent \n$filter (1-42)')
    embed.add_field(name='Valid Time Frames (written how is):',value='1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day')
    embed.add_field(name='Calculates/Finds?',value='RSI, OBV, and MACD Divergences (within 42 periods) and possible forming RSI Divergences')
    embed.add_field(name='Feedback, Changes, or Input?',value='Add me on Discord: rpp#9779')
    await bot.say(embed=embed)

@bot.command(pass_context=True)
async def howmany(ctx):
    results_dict = bot.results_dict
    time_frames = ['1h','2h','4h','6h','8h','12h','1d']
    fr_divs = []
    cd_divs = []
    t_divs  = []
    #determine number of divergence for historical, current, and triples
    for time_frame in time_frames:
        full_results, current_div_results = results_dict[time_frame]
        #Filter for space in divergence and minimum score
        full_results2 = divs_filter(full_results,1)
        full_results_sorted = score_filter(full_results2)
        fr_divs.append(len(full_results_sorted))
        cd_divs.append(len(current_div_results))
        trip_divs = find_tripdivs(full_results)
        t_divs.append(len(trip_divs))
    #Form message for embed
    fr_msg, cd_msg, t_msg = howmany_message(fr_divs,cd_divs,t_divs)
    embed = discord.Embed(title='**Number of Divergence for All Analyses**',description='*Analyses = Historical, Current, Triple*')
    embed.add_field(name='__$histdiv__',value=fr_msg)
    embed.add_field(name='__$currentdiv__',value=cd_msg)
    embed.add_field(name='__$tripdiv__',value=t_msg)
    await bot.say(embed=embed)

@bot.command(pass_context=True)
async def coinsearch(ctx,coin:str):
    coin = coin.upper()
    coin_list = ['ADABTC', 'ADXBTC', 'AEBTC', 'AIONBTC', 'AMBBTC', 'APPCBTC', 'ARKBTC', 'ARNBTC', 'ASTBTC', 'BATBTC', 'BCCBTC', 'BCDBTC', 'BCNBTC','BCPTBTC', 'BLZBTC', 'BNBBTC', 'BNTBTC', 'BQXBTC', 'BRDBTC', 'BTGBTC', 'BTSBTC', 'CDTBTC', 'CHATBTC', 'CLOAKBTC', 'CMTBTC', 'CNDBTC', 'DASHBTC', 'DGDBTC', 'DLTBTC', 'DNTBTC', 'EDOBTC', 'ELFBTC', 'ENGBTC', 'ENJBTC', 'EOSBTC', 'ETCBTC', 'ETHBTC', 'EVXBTC', 'FUELBTC', 'FUNBTC', 'GASBTC', 'GNTBTC','GRSBTC', 'GTOBTC', 'GVTBTC', 'GXSBTC', 'HSRBTC', 'ICNBTC', 'ICXBTC', 'INSBTC', 'IOSTBTC', 'IOTABTC', 'IOTXBTC', 'KMDBTC', 'KNCBTC', 'LENDBTC', 'LINKBTC', 'LOOMBTC', 'LRCBTC', 'LSKBTC', 'LTCBTC', 'LUNBTC', 'MANABTC', 'MCOBTC', 'MDABTC', 'MODBTC', 'MTHBTC', 'MTLBTC', 'NANOBTC', 'NAVBTC', 'NCASHBTC', 'NEBLBTC', 'NEOBTC', 'NULSBTC', 'OAXBTC', 'OMGBTC', 'ONTBTC', 'OSTBTC', 'PIVXBTC', 'POABTC', 'POEBTC', 'POWRBTC', 'PPTBTC', 'QLCBTC', 'QSPBTC', 'QTUMBTC', 'RCNBTC', 'RDNBTC', 'REPBTC','REQBTC', 'RLCBTC', 'RPXBTC', 'SALTBTC', 'SKYBTC','SNMBTC', 'SNTBTC', 'SNGLSBTC', 'STEEMBTC', 'STORJBTC', 'STRATBTC', 'SUBBTC', 'SYSBTC', 'THETABTC','TNBBTC', 'TNTBTC', 'TRIGBTC', 'TRXBTC', 'VIABTC', 'VIBBTC', 'VIBEBTC', 'WABIBTC', 'WANBTC', 'WAVESBTC', 'WINGSBTC', 'WPRBTC', 'WTCBTC', 'XEMBTC', 'XLMBTC', 'XMRBTC', 'XVGBTC', 'XRPBTC', 'XZCBTC', 'YOYOBTC', 'ZECBTC', 'ZENBTC','ZILBTC', 'ZRXBTC', 'ADAUSDT', 'BCCUSDT', 'BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'EOSUSDT', 'IOTAUSDT', 'LTCUSDT', 'NEOUSDT', 'QTUMUSDT', 'XLMUSDT', 'XRPUSDT']
    if coin not in coin_list:
        await bot.say('**Not a valid coin** \n__Common Problems__: \nCoin pairing does not have enough data to be run for results (will be added in the future) \nMispelling \nCoin Pairing not listed on Binance')
    else:
        results_dict = bot.results_dict
        msg_fr, msg_cd, msg_t, msg_fr_r, msg_cd_r = coinsearch_message(coin,results_dict)
        embed = discord.Embed(title='**Overview Search Results for {}**'.format(coin),description='*Searched in $histdiv, $currentdiv, $tripdiv*')
        embed.add_field(name='$histdiv',value=msg_fr)
        embed.add_field(name='$currentdiv',value=msg_cd)
        embed.add_field(name='$tripdiv',value=msg_t)
        await bot.say(embed=embed)
        await asyncio.sleep(0.1)
        cr_msg = '**$histdiv:**\n{}\n**$currentdiv:**\n{}'.format(msg_fr_r,msg_cd_r)
        embed = discord.Embed(title='Search Results for {}'.format(coin),description=cr_msg)
        await bot.say(embed=embed)

@bot.command(pass_context=True)
async def recent(ctx):
    results_dict = bot.results_dict
    filtered_results = recent_filter(results_dict,2)
    msg_dict = recent_message(filtered_results)
    #Create embed
    embed = discord.Embed(title='Recent Divergences for All Time Frames',description='')
    char_counter = 0
    for d in msg_dict:
        for header,body in d.items():
            char_counter += len(header)
            for msg in body:
                char_counter += len(msg)
                if char_counter > 5000:
                    await bot.say(embed=embed)
                    await asyncio.sleep(0.05)
                    embed = discord.Embed(title='Recent Divergences for All Time Frames (Page 2)', description='')
                    char_counter = 0
                embed.add_field(name='__{}__'.format(header),value=msg)
    await bot.say(embed=embed)
    await asyncio.sleep(0.5)
    #Trip Divs
    time_frames = ['1h','2h','4h','6h','8h','12h','1d']
    #rewrite
    embed = discord.Embed(title='Recent Triple Divergences for all Time Frames',description='')
    tf_converter = {'1h':'1 Hour', '2h':'2 Hour', '4h':'4 Hour', '6h':'6 Hour', '8h':'8 Hour', '12h':'12 Hour', '1d':'1 Day'}
    field_counter = 0
    char_counter = []
    fieldheader_counter = 0
    for time_frame in time_frames:
        results_dict = bot.results_dict
        results_fr,results_cd = results_dict[time_frame]
        results_recent = recent_filter_td(results_fr)
        results_sorted = sort_based_on_score(results_recent)
        trip_divs = find_tripdivs(results_sorted)
        t_msg = tripdivs_message(trip_divs)
        if t_msg != [{'None':'None'}]:
            field_name = tf_converter[time_frame]
            embed.add_field(name='__{}__:'.format(field_name),value='')
            fieldheader_counter += 1
            print(field_name)
            print(t_msg)
            for result in t_msg:
                print('result',result)
                for header,body in result.items():
                    field_counter += 1
                    print('header',header)
                    print('body',body)
                    if header != 'None' or body != 'None':
                        print('tracker',header,body)
                        char_counter.append(len(header) + len(body))
                        embed.add_field(name=header,value=body)
    print('TOTAL FIELDS',field_counter,fieldheader_counter)
    print('TOTAL CHAR',char_counter)
    print('TOTAL CHARS TOTAL:',sum(char_counter))
    if field_counter == 0:
        embed.add_field(name='None',value='None')
    await asyncio.sleep(0.5)
    await bot.say(embed=embed)

@bot.command(pass_context=True)
async def filter(ctx,i:str):
    if valid_when(i) == False:
        await bot.say('Invalid input for $filter command. Second input for command must be a whole number between 2 and 42')
    else:
        results_dict = bot.results_dict
        i = int(i)
        filtered_results = recent_filter(results_dict,i)
        fr = score_filter(filtered_results)
        msg_dict = recent_message(fr)
        #Create embed
        embed = discord.Embed(title='Divergences for All Time Frames for {} Periods Ago'.format(str(i)),description='')
        char_counter = 0
        for d in msg_dict:
            for header,body in d.items():
                char_counter += len(header)
                for msg in body:
                    char_counter += len(msg)
                    if char_counter > 5000:
                        await bot.say(embed=embed)
                        char_counter = 0
                    embed.add_field(name='__{}__'.format(header),value=msg)
        await bot.say(embed=embed)

@bot.command(pass_context=True)
async def test(ctx,useless_command:str):
    if useless_command == 'weewoo':
        print(len(bot.servers))
        print(bot.servers)

async def get_candles(coin,limitK,period):
    """Uses aiohttp to download data from Binance based on coin, period, and limit
    Parameters:
        coin;str
        limitK;number
        period;str
    Returns:
        coin_data;list of dictionaries
    """
    limitK = str(limitK)
    ENDPOINT = 'https://api.binance.com/api/v1/klines'
    url = ENDPOINT + '?symbol=' + coin + '&interval=' + period + '&limit=' + limitK
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                coin_data = await resp.json()
    return [{
        "open": float(d[1]),
        "close": float(d[4]),
        "volume": float(d[5]),
    } for d in coin_data]

def calculateRSI(coin_data):
    """Calculates RSI for coin
    Parameters:
        coin_data; list of dictionaries
    Returns:
        list_RSI;list(list of RSIs(floats))
        last_avg_gain;float (to be used in void RSI calculations)
        last_avg_loss;float (to be used in void RSI calculations)
    """
    change_list = []
    #Download and organize Price data into list
    for idx in range(len(coin_data)):
        change = float(coin_data[idx]['close'])-float(coin_data[idx]['open'])        
        change_list.append(change)
    #create total avg gain and loss lists with correct 0 values based on gains and losses
    list_gain = []
    list_loss = []
    for change in change_list:
        if change > 0:
            list_gain.append(abs(change))
            list_loss.append(0)
        elif change < 0:
            list_gain.append(0)
            list_loss.append(abs(change))
        elif change == 0:
            list_gain.append(0)
            list_loss.append(0)
    #calculate RS based off change and initialize last_avg_gain and last_avg_loss 
    list_rs = []
    last_avg_gain = 0
    last_avg_loss = 0
    for idx in range(13,80):
        if idx == 13:
            avg_gain = numpy.mean(list_gain[0:14])
            avg_loss = numpy.mean(list_loss[0:14])
            new_rs = avg_gain / avg_loss
            list_rs.append(new_rs)
            prev_avg_gain = avg_gain
            prev_avg_loss = avg_loss
        elif idx > 13:
            avg_gain = ((prev_avg_gain * 13) + list_gain[idx]) / 14
            avg_loss = ((prev_avg_loss * 13) + list_loss[idx]) / 14
            new_rs = avg_gain/avg_loss
            list_rs.append(new_rs)
            prev_avg_gain = avg_gain
            prev_avg_loss = avg_loss
        #for void price calculations
        if idx == 78:            
            last_avg_gain = prev_avg_gain
            last_avg_loss = prev_avg_loss
    #calculate RSI based off list_rs
    list_RSI=[]
    for rs in list_rs:
        rsi = (100 - (100 / (1 + rs)))
        rsi = round(rsi,2)
        list_RSI.append(rsi)
    #reduce list_RSI to last 42 rsi's for analysis
    list_RSI = list_RSI[-42:]
    return list_RSI,last_avg_gain,last_avg_loss

def calculate_obv(coin_data):
    """Calculate OBV for coin
    Parameters:
        coin_data; list of dictionaries
    Returns:
        list_OBV;list of floats
    """
    #Initialize list_OBV with starting value at 0 and prev_OBV with an arbitrary value of 0
    list_OBV = [0]
    prev_OBV = 0
    #Calculate OBV
    for idx in range(1,80):
        change_day = float(coin_data[idx]['close']) - float(coin_data[idx-1]['close'])
        change_volume = float(coin_data[idx]['volume'])
        if idx == 1:
            if change_day > 0:
                new_OBV = change_volume
            elif change_day < 0:
                new_OBV = 0 - change_volume
            else:
                new_OBV = 0
        else:
            if change_day > 0:
                new_OBV = prev_OBV + change_volume
            elif change_day < 0:
                new_OBV = prev_OBV - change_volume
            else:
                new_OBV = prev_OBV
        new_OBV = round(new_OBV,2)
        list_OBV.append(new_OBV)
        prev_OBV = new_OBV
    #Remove the 0 from the beginning of the list
    zero_check = True
    while zero_check == True:
        if list_OBV[0] == 0:
            del list_OBV[0]
        if list_OBV[0] != 0:
            zero_check = False
    #Reduce list_OBV to last 42 OBVs for later analysis
    list_OBV = list_OBV[-42:]
    return list_OBV

def calculate_macd(coin_data):
    '''Calculate MACD for a coin organized into two lists: MACD line values and Signal Line values
        Due to how MACD is calculated, coin_data needs at least 70 points of data (65 at least)
    Parameters:
        coin_data;list of dictionaries
    Returns:
        list_macd;list of floats
        list_sigline;list of floats
    '''
    #Retrieve closes from coin_data
    list_price = [float(adict['close']) for adict in coin_data]
    #Set up constants for a 12 EMA and calculate
    scontant_12 = 2 / 13
    ema_12 = []
    
    for idx in range(11,80):
        if idx == 11:
            new_ema = numpy.mean(list_price[0:12])
            ema_12.append(new_ema)
            prev_ema = new_ema
        else:
            new_ema = (list_price[idx] - prev_ema) * scontant_12 + prev_ema
            ema_12.append(new_ema)
            prev_ema = new_ema
            
    #Set up constants for a 26 EMA and calculate
    sconstant_26 = 2 / 27
    ema_26 = []
    for idx in range(25,80):
        if idx == 25:
            new_ema = numpy.mean(list_price[0:26])
            ema_26.append(new_ema)
            prev_ema = new_ema
        else:
            new_ema = (list_price[idx] - prev_ema) * sconstant_26 + prev_ema
            ema_26.append(new_ema)
            prev_ema = new_ema
            
    #Calculate MACD Line
    list_macd = []
    for idx in range(1,56):
        amacd = ema_12[-idx] - ema_26[-idx]
        list_macd.append(amacd)
    list_macd.reverse()
    #Calculate signal line
    sconstant_9 = 1 / 10
    list_sigline = []
    for idx in range(8,55):
        if idx == 8:
            new_ema = numpy.mean(list_macd[0:9])
            list_sigline.append(new_ema)
            prev_ema = new_ema
        else:
            new_ema = (list_macd[idx] - prev_ema) * sconstant_9 + prev_ema
            list_sigline.append(new_ema)
            prev_ema = new_ema
    #Reduce list_macd and list_sigline to 42 data points for further analysis
    list_macd = list_macd[-42:]
    list_sigline = list_sigline[-42:]
    #Return statements
    return list_macd, list_sigline

def price_per_period(coin_data):
    """Extracts the closing prices for each period for a coin from coin_data
    Parameters:
        coin_data;list of floats
    Returns:
        list_price;list of floats
    """
    #print(type(coin_data)
    #Initialize list_price
    list_price = []
    #Extract closing price for each period and add to list_price
    for idx in range(len(coin_data)):
        price = float(coin_data[idx]['close'])
        list_price.append(price)
    #Reduce list_price to the last 42 closing prices for later analysis
    list_price = list_price[-42:]
    return list_price

def comparator(list_price,list_RSI,list_OBV,last_avg_gain,last_avg_loss,list_macd,list_sigline):
    """Determines trend of Price, RSI, and OBV
        Determines if RSI bullish divergence or OBV bullish divergence occurs
    Parameters:
        list_price;list of floats
        list_RSI;list of floats
        list_OBV;list of floats
        last_avg_gain;float
        last_avg_loss;float
        list_macd;list of floats
        list_sigline;list of floats
    Returns:
        trend_price;bool
        trend_RSI;bool
        trend_OBV;bool
        trend_MACD;bool
        score_RSI;float
        score_OBV;float
        current_div_RSI;tuple (bool,float)
        void_price;float 
        rsi_div_idx;list
        obv_div_idx;list
    """
    """
    #Intitialize lists 
    ll_price_broad = []
    ll_idx = []
    ll_idx_broad = []
    ll_price = []
    #Initialize idx_counter to determine index of local lows (ll = local lows)
    idx_counter = 1
    #Find local lows of Price (ll_price_broad)
    for idx in range(1,len(list_price) - 1):
        if list_price[idx] <= list_price[idx-1] and list_price[idx] <= list_price[idx+1]:
            ll_price_broad.append(list_price[idx])
            ll_idx_broad.append(idx_counter)
        idx_counter += 1
    #reset idx_counter
    idx_counter = 1
    #Find local lows of the local lows for Price (ll_price)
    for idx in range(1,len(ll_price_broad) - 1):
        if (ll_price_broad[idx -1] - ll_price_broad[idx]) > 0:
            if ll_price_broad[idx - 1] not in ll_price:
                ll_price.append(ll_price_broad[idx - 1])
                ll_idx.append(ll_idx_broad[idx_counter - 1])
        if ll_price_broad[idx] < ll_price_broad[idx-1] and ll_price_broad[idx] < ll_price_broad[idx+1]:
            ll_price.append(ll_price_broad[idx])
            ll_idx.append(ll_idx_broad[idx_counter])
        idx_counter += 1
    #Determine if endpoints could be considered lows (despite not having a high on one side) and add their indices accordingly
    #Find if first price is considered to be a low
    if ll_price_broad[0] < ll_price_broad[1]:
        ll_price.insert(0,ll_price_broad[0])
        ll_idx.insert(0,ll_idx_broad[0])
    #Find if last price is considered to be a low
    if ll_price_broad[-1] < ll_price_broad[-2]:
        ll_price.append(ll_price_broad[-1])
        ll_idx.append(ll_idx_broad[-1])
    """
    ll_price, ll_idx = ll_comparator_v2(list_price)

    #Find local lows for RSI and OBV according to the local low indices (ll_idx) for comparison against Price
    #Initialize lists
    ll_RSI = []
    ll_OBV = []
    ll_MACD_macd = []
    ll_MACD_sigline = []
    #Add correct RSIs and OBVs according to ll_idx
    for idx in ll_idx:
        ll_RSI.append(list_RSI[idx])
        ll_OBV.append(list_OBV[idx])
        ll_MACD_macd.append(list_macd[idx])
        ll_MACD_sigline.append(list_sigline[idx])
    """
    #Testing statements for bug fixing (unnecessary for normal use)
    print(ll_idx_broad)
    print(ll_idx)
    print('Prices',list_price)
    print('Low Prices:',ll_price)
    print('RSIs:',list_RSI)
    print('Low RSIs:',ll_RSI)
    print('OBVs:',list_OBV)
    print('Low OBVs:',ll_OBV)
    plot(list_price,'price total')
    plot(ll_price,'price lows')
    plot(list_RSI,'rsi total')
    plot(ll_RSI,'rsi lows')
    plot(list_OBV,'obv total')
    plot(ll_OBV,'obv lows')
    """
    #Determine the trend of Price, RSI, and OBV (True = Up; False = Down)
    #Initialize trends for Price, RSI, and OBV; Desired Trends: Price --> False; RSI --> True; OBV --> True)
    trend_price = True 
    trend_RSI = False
    trend_OBV = False
    trend_MACD = False
    #Determine trend_price
    threshold = 1
    counter_trend_price = 0
    #Adds 1 to counter_trend_price everytime price decreases between local lows in ll_price
    for idx in range(1,len(ll_price)):
        if (ll_price[idx] - ll_price[idx - 1]) < 0:
            counter_trend_price += 1
    #Switches trend_price to False if there is 
    if counter_trend_price >= threshold:
        trend_price = False
        
    #Determine if RSI is currently diverging (current period)
    #Initialize current_div_RSI = (bool (True if diverging),score (how much the divergence is))
    current_div_RSI = (False,0)
    #Determine if RSi is currently diverging and calculate score (% change in price * RSI change)
    if list_price[-1] < ll_price[-1] and list_RSI[-1] > ll_RSI[-1]:
        score_div_RSI = abs(ll_RSI[-1] - list_RSI[-1])
        score_div_price = ((abs(ll_price[-1] - list_price[-1]) / (ll_price[-1])) * 100) + 1
        current_div_RSI = (True,round(score_div_RSI*score_div_price,2))
    #Calcualte void_price for RSI (the price at which the RSI will no longer be higher than the previous local low)
    void_price = 0
    #Calculate by continually decreasing price until RSI is below last local low RSI
    if current_div_RSI[0] == True:
        last_ll_rsi = ll_RSI[-1]
        void = False
        fake_price = list_price[-1]
        while void == False:
            fake_change = list_price[-2] - fake_price
            void_avg_gain = (last_avg_gain*13) / 14
            void_avg_loss = ((last_avg_loss*13) + fake_change) / 14
            void_RS = void_avg_gain / void_avg_loss
            void_rsi = 100 - (100 / (1 + void_RS))
            if void_rsi < last_ll_rsi:
                void_price = fake_price
                void = True
            fake_price -= (0.001 * fake_price)
            
    #Determine trend_RSI
    #Initialize score_RSI and counter_trend_RSI and rsi_div_idx
    score_RSI = []
    counter_trend_RSI = 0
    rsi_div_idx = []
    #Calculate score for any divergences and increase RSI divergence counter
    for idx in range(1,len(ll_price)):
        if (ll_price[idx] - ll_price[idx - 1]) < 0 and (ll_RSI[idx] - ll_RSI[idx - 1]) > 0:
            counter_trend_RSI += 1
            score_RSI_RSI = abs(ll_RSI[idx - 1] - ll_RSI[idx])
            score_RSI_price = ((abs(ll_price[idx - 1] - ll_price[idx]) / (ll_price[idx - 1])) * 100) + 1
            score_RSI.append(round(score_RSI_RSI * score_RSI_price,2))
            #Record position of divergence 
            rsi_div_idx.append(42 - ll_idx[idx - 1])
            rsi_div_idx.append(42 - ll_idx[idx])
    
    #Determine trend_RSI based on number of divergences (at least 1)
    if counter_trend_RSI >= threshold:
        trend_RSI = True
        
    #determine trend_OBV
    #Initialize score_OBV and counter_trend_OBV
    score_OBV = []
    counter_trend_OBV = 0
    obv_div_idx = []
    #Calculate score for any divergences and increase OBV divergence counter
    for idx in range(1,len(ll_price)):
        if (ll_price[idx] - ll_price[idx - 1]) < 0 and (ll_OBV[idx] - ll_OBV[idx - 1]) > 0:
            counter_trend_OBV += 1
            score_OBV_OBV = (abs(ll_OBV[idx - 1] - ll_OBV[idx]) / (ll_OBV[idx - 1])) * 10
            score_OBV_price = ((abs(ll_price[idx - 1] - ll_price[idx]) / (ll_price[idx - 1])) * 100) + 1
            score_OBV.append(abs(round(score_OBV_OBV * score_OBV_price,2)))
            #Record position of divergence
            obv_div_idx.append(42 - ll_idx[idx - 1])
            obv_div_idx.append(42 - ll_idx[idx])
    #Determine trend_OBV based on number of divergences (at least 1)
    if counter_trend_OBV >= threshold:
        trend_OBV = True

    #determine trend of MACD
    #Initialize score_MACD and counter_trend_MACD
    score_MACD = []
    counter_trend_MACD = 0
    macd_div_idx = []
    #Calculate score for any divergence and increase MACD divergence counter
    for idx in range(1,len(ll_price)):
        if (ll_price[idx] - ll_price[idx - 1]) < 0 and ((ll_MACD_macd[idx] + ll_MACD_sigline[idx]) / 2) > ((ll_MACD_macd[idx - 1] + ll_MACD_sigline[idx - 1]) / 2):
            counter_trend_MACD += 1
            score_MACD_MACD = (abs(ll_MACD_sigline[idx - 1] - ll_MACD_sigline[idx]) / (ll_MACD_sigline[idx - 1])) * 10
            score_MACD_price = ((abs(ll_price[idx - 1] - ll_price[idx]) / (ll_price[idx - 1])) * 100) + 1
            score_MACD.append(abs(round(score_MACD_MACD * score_MACD_price,2)))
            #Record position of divergence
            macd_div_idx.append(42 - ll_idx[idx - 1])
            macd_div_idx.append(42 - ll_idx[idx])
    #Deterine trend_MACD based on number of divergences (at least 1)
    if counter_trend_MACD >= threshold:
        trend_MACD = True

    return trend_price,trend_RSI,trend_OBV,trend_MACD,score_RSI,score_OBV,score_MACD,current_div_RSI,void_price,rsi_div_idx,obv_div_idx,macd_div_idx

def comparator_results_compiler(coin,trend_RSI,trend_OBV,trend_MACD,score_RSI,score_OBV,score_MACD,rsi_div_idx,obv_div_idx,macd_div_idx,full_results):
    """Prints results from comparator (divergence and score if applicable) and returns a tuple with (coin,divergences)
    Parameters:
        trend_price;bool
        trend_RSI;bool
        trend_OBV;bool
        trend_MACD;bool
        coin;str
        score_RSI;float
        score_OBV;float
    Returns:
        full_results;list of dictionaries(dictionaries contain information on divergences)
    """
    if trend_RSI == True:
        for idx in range(len(score_RSI)):
            full_results.append({'coin':coin,'type div':'RSI Divergence','score':score_RSI[idx],'position':[rsi_div_idx[idx * 2], rsi_div_idx[(idx * 2) + 1]]})
    if trend_OBV == True:
        for idx in range(len(score_OBV)):
            full_results.append({'coin':coin,'type div':'OBV Divergence','score':score_OBV[idx],'position':[obv_div_idx[idx * 2], obv_div_idx[(idx * 2) + 1]]})
    if trend_MACD == True:
        for idx in range(len(score_MACD)):
            full_results.append({'coin':coin,'type div':'MACD Divergence','score':score_MACD[idx],'position':[macd_div_idx[idx * 2], macd_div_idx[(idx * 2) + 1]]})
    return full_results

def current_div_results_compiler(coin,current_div_RSI,void_price,list_price,current_div_results):
    """Compiles information into current_div_results if there is a current RSI divergence forming
        Compiles coin,score,void price,current price into a dictionary and then adds the dictionary to the list current_div_results
    Parameters:
        coin;str
        current_div_RSI;tuple(bool,float)
        void_price;float
        list_price;list
        current_div_results;list of dictionaries (for storage of current divergence RSI data)
    Returns:
        current_div_results;list of dictionaries
    """
    if current_div_RSI[0] == True:
        void_price = '{:.8f}'.format(void_price)
        current_price = '{:.8f}'.format(list_price[-1])
        void_price = reformat_overflow_str(void_price)
        current_price = reformat_overflow_str(current_price)
        current_div_results.append({'coin':coin,'score':current_div_RSI[1],'void price':void_price,'current price':current_price})
    return current_div_results

def pre_comparator(list_price):
    """Smaller comparator to run before main comparator to prevent unnecessary calculations being performed 
        Determines trend of price
    Parameters:
        list_price;list
    Returns:
        trend_price;bool (True if downtrending)
    """
    #Initialize ll_price_broad and ll_price
    ll_price_broad = []
    ll_price = []

    #Find local lows of price
    for idx in range(1,len(list_price) - 1):
        if list_price[idx] < list_price[idx - 1] and list_price[idx] < list_price[idx + 1]:
            ll_price_broad.append(list_price[idx])

    #Find the local lows of the local lows for price
    idx_counter = 1
    for idx in range(1,len(ll_price_broad) - 1):
        if (ll_price_broad[idx - 1] - ll_price_broad[idx]) > 0:
            if ll_price_broad[idx - 1] not in ll_price:
                ll_price.append(ll_price_broad[idx -1])
        if ll_price_broad[idx] < ll_price_broad[idx - 1] and ll_price_broad[idx] < ll_price_broad[idx + 1]:
            ll_price.append(ll_price_broad[idx])

    #Determine if endpoints of the list are lows (despite missing one point for comparison) and add if applicable
    if len(ll_price_broad) > 1: #Prevents error with list of len == 1
        if ll_price_broad[0] < ll_price_broad[1]:
            ll_price.insert(0,ll_price_broad[0])
        if ll_price_broad[-1] < ll_price_broad[-2]:
            ll_price.append(ll_price_broad[-1])

    #Determine trend_price
    trend_price = True
    threshold = 1
    counter_trend_price = 0
    for idx in range(1,len(ll_price)):
        if (ll_price[idx] - ll_price[idx - 1]) < 0:
            counter_trend_price += 1
    if counter_trend_price >= threshold:
        trend_price = False

    return trend_price

def analysis_RSIOBVMACD(coin,coin_data,full_results,current_div_results):
    '''Main analysis function that runs and compiles all data into dictionaries for coins based on trends for RSI, OBV, and MACD
    Parameters:
        coin;str
        coin_data;list of dictionaries
        full_results;list of dictionaries
        current_div_results;list of dictionaries
    Returns:
        full_results;list of dictionaries
        current_div_results;list of dictionaries
    '''
    #list_price = price_per_period(coin_data)
    list_price = prices_v2(coin_data)
        #Runs full analysis if downtrend in price is detected
    if pre_comparator(list_price) == False:
        #Calculates RSI and OBV and MACD
        list_RSI,last_avg_gain,last_avg_loss = calculateRSI(coin_data)
        list_OBV = calculate_obv(coin_data)
        list_macd,list_sigline = calculate_macd(coin_data)
         #Determines trend of Price, RSI, and OBV
        trend_price,trend_RSI,trend_OBV,trend_MACD,score_RSI,score_OBV,score_MACD,current_div_RSI,void_price,rsi_div_idx,obv_div_idx,macd_div_idx = comparator(list_price,list_RSI,list_OBV,last_avg_gain,last_avg_loss,list_macd,list_sigline)
        #test_plot(list_price,list_RSI,list_OBV) #This line is meant to be used for testing in coordination with coin_list1
        #Compile into dictionaries for mapping and results during printing
        full_results = comparator_results_compiler(coin,trend_RSI,trend_OBV,trend_MACD,score_RSI,score_OBV,score_MACD,rsi_div_idx,obv_div_idx,macd_div_idx,full_results)
        current_div_results = current_div_results_compiler(coin,current_div_RSI,void_price,list_price,current_div_results)
    return full_results,current_div_results
        
def full_results_to_str(full_results):
    """Changes full_results (a list of dictionaries) into a multi-line str to be used in embed statements in Discord
    Parameters:
        full_results;list of dictionaries
    Returns:
        full_results_str;multi-line str formatted to fit embed statements
    """
    full_results_str_list = []
    temp_list = []
    result_message = ''
    for idx in range(len(full_results)):
        dct = full_results[idx]
        result = '**{}** | {} | Score: {} | Divergence {} to {} periods ago\n'.format(dct['coin'],dct['type div'],dct['score'],dct['position'][1],dct['position'][0])
        result_message = result_message + result
        #organizes into groups of 20
        if (idx + 1) % 20 == 0 or idx == (len(full_results) - 1):
            temp_list.append(result_message)
            full_results_str_list.append(temp_list)
            temp_list = []
            result_message = ''
    return full_results_str_list

def current_div_results_to_str(current_div_results):
    """Changes current_div_results (a list of dictionaries) into a multi-line str to be used in embed statements in Discord
    Parameters:
        current_div_results;list of dictionaries
    Returns:
        cdr_str_list;list of strings with length under 1024 for embed fields to not give error
    """
    cdr_str_list = []
    temp_list = []
    result_message = ''
    #Formats result and adds to a temp_list which is used to not exceed char limit
    for idx in range(len(current_div_results)):
        dct = current_div_results[idx]
        result = '**{}** | Score: {} | Void Sats: {} | Current Sats: {}\n'.format(dct['coin'],dct['score'],dct['void price'],dct['current price'])
        result_message = result_message + result
        #organizes into groups of 15 to not exceed Character Limit 1024
        if (idx + 1) % 15 == 0 or idx == (len(current_div_results) - 1):
            temp_list.append(result_message)
            cdr_str_list.append(temp_list)
            temp_list = []
            result_message = ''
    return cdr_str_list

def sort_based_on_score(results):
    '''Sorts results based on their score back into a list
    Parameters:
        results;list of dictionaries
    Returns:
        sorted_results;list of dictionaries
    '''
    sorted_results = sorted(results, key=lambda results: float(results['score']),reverse=True)
    return sorted_results

def reformat_overflow_str(price):
    '''Reformat prices for dictionary entries in the case they exceed len(str(price)) = 10 to reduce line bleed in result printing
    Parameters:
        price;float
    Returns:
        price;float
    '''
    if len(str(price)) > 10:
        overflow = len(str(price)) - 10
        price = float(price)
        if overflow == 4:
            price = '{:.4f}'.format(price)
        elif overflow == 3:
            price = '{:.5f}'.format(price)
        elif overflow == 2:
            price = '{:.6f}'.format(price)
        elif overflow == 1:
            price = '{:.7f}'.format(price)
    return price

def find_tripdivs(full_results):
    '''Finds all coins with triple divergences (RSI, OBV, and MACD)
    Parameters:
        full_results;list of dictionaries
    Returns:
        trip_divs;list of dictionaries
    '''
    trip_divs = []
    #format = {coin:list of results}
    ld_r = [r for r in full_results if r['type div'] == 'RSI Divergence']
    ld_o = [r for r in full_results if r['type div'] == 'OBV Divergence']
    ld_m = [r for r in full_results if r['type div'] == 'MACD Divergence']
    #find triple divergences
    coins = []
    for r in ld_r:
        for o in ld_o:
            if r['coin'] == o['coin'] and (r['position'][0] - o['position'][0]) <= 1 and (r['position'][1] - o['position'][1]) <= 1:
                for m in ld_m:
                    if r['coin'] == m['coin'] and (r['position'][0] - m['position'][0]) <= 1 and (r['position'][1] - m['position'][1]) <= 1:
                        if float(r['score']) > 1 or float(o['score']) > 1 or float(m['score']) > 1:
                            #triple divergece found; format entry
                            entry = {r['coin']:[r,o,m]}
                            #prevent duplicates
                            if r['coin'] not in coins:
                                trip_divs.append(entry)
                            coins.append(r['coin'])
    return trip_divs

def tripdivs_message(trip_divs):
    '''Create message to be printed in embed for $tripdiv
    Parameters:
        trip_divs;list of dictionaries
    Returns:
        msg_list;list of dictionaries ({header:body})
    '''
    msg_list = []
    for result in trip_divs:
        for coin,results in result.items():
            #Make header
            header = '__{}__: Divergence {} to {} periods ago   \n'.format(coin,results[0]['position'][1],results[0]['position'][0])
            #Make body
            body = ''
            for r in results:
                msg = '{} | Score: {}\n'.format(r['type div'], r['score'])
                body = body + msg
            msg_list.append({header:body})
    if len(msg_list) == 0:
        msg_list = [{'None':'None'}]
    return msg_list

def howmany_message(fr_divs,cd_divs,t_divs):
    '''Creates message to be printed in embed for $howmany
    Parameters:
        fr_divs;list of ints
        cd_divs;list of ints
        t_divs;list of ints
    Returns:
        message;str
    '''
    periods = ['1 hour', '2 hour', '4 hour', '6 hour', '8 hour', '12 hour', '1 day']
    fr_msg = ''
    for idx in range(len(fr_divs)):
        new_msg = '{}: {} divergences \n'.format(periods[idx], fr_divs[idx])
        fr_msg = fr_msg + new_msg
    cd_msg = ''
    for idx in range(len(cd_divs)):
        new_msg = '{}: {} divergences \n'.format(periods[idx], cd_divs[idx])
        cd_msg = cd_msg + new_msg
    t_msg = ''
    for idx in range(len(t_divs)):
        new_msg = '{}: {} divergences \n'.format(periods[idx], t_divs[idx])
        t_msg = t_msg + new_msg
    return fr_msg, cd_msg, t_msg

def divs_filter(full_results,i):
    '''Reduces number of results in full_results by analyzing length of divergence period (5 or more only)
    (in response to an accuracy update which captures quicker divergences)
    Parameters:
        full_results;list of dictionaries
        i;int
    Returns:
        r;list of dictionaries
    '''
    r = [d for d in full_results if abs((d['position'][1] - d['position'][0])) >= i]
    return r

def score_filter(results):
    '''Filter out scores under 1 to prevent spam
    Paramters:
        results;list of dictionaries
    Returns:
        r;list of dictionaries
    '''
    r = [d for d in results if float(d['score']) > 1]
    return r

def coinsearch_message(coin,results_dict):
    '''Creates message to be printed in embed for $coinsearch
    Parameters:
        coin_found;list of dictionaries
    Returns:
        cs_msg;str
    '''
    time_frames = ['1h','2h','4h','6h','8h','12h','1d']
    tf_converter = {'1h':'1 Hour:','2h':'2 Hour:','4h':'4 Hour:','6h':'6 Hour:','8h':'8 Hour:','12h':'12 Hour:','1d':'1 Day:'}
    msg_fr = ''
    msg_cd = ''
    msg_t = ''
    msg_fr_r = ''
    msg_cd_r = ''
    for time_frame in time_frames:
        full_results, current_div_results = results_dict[time_frame]
        full_results = divs_filter(full_results,1)
        #find occurrences in full_results
        coins_fr = [adict['coin'] for adict in full_results]
        if coin in coins_fr:
            msg_fr = msg_fr + '{}: :white_check_mark:\n'.format(time_frame)
        else:
            msg_fr = msg_fr + '{}: :x:\n'.format(time_frame)
        #Format message for $tripdiv
        coin_appearance = [c for c in full_results if coin == c['coin']]
        if len(coin_appearance) != 0:
            msg_fr_r = msg_fr_r + '__{}__\n'.format(tf_converter[time_frame])
            for r in full_results:
                if r['coin'] == coin:
                    result = '{} | Score: {} | Divergence {} to {} periods ago\n'.format(r['type div'],r['score'],r['position'][1],r['position'][0])
                    msg_fr_r = msg_fr_r + result

        #find occurrences in current_div_results
        coins_cd = [adict['coin'] for adict in current_div_results]
        if coin in coins_cd:
            msg_cd = msg_cd + '{}: :white_check_mark:\n'.format(time_frame)
        else:
            msg_cd = msg_cd + '{}: :x:\n'.format(time_frame)
        #Format message for $tripdiv
        coin_appearance = [c for c in current_div_results if coin == c['coin']]
        if len(coin_appearance) != 0:
            msg_cd_r = msg_cd_r + '__{}__\n'.format(tf_converter[time_frame])
            for r in current_div_results:
                if r['coin'] == coin:
                    result = 'Score: {} | Void Price: {} | Current Price: {}\n'.format(r['score'],r['void price'],r['current price'])
                    msg_cd_r = msg_cd_r + result

        #find occurrences in triple div
        trip_divs = find_tripdivs(full_results)
        coins_td = []
        for result in trip_divs:
            for c,info in result.items():
                coins_td.append(c)
        if coin in coins_td:
            msg_t = msg_t + '{}: :white_check_mark:\n'.format(time_frame)
        else:
            msg_t = msg_t + '{}: :x:\n'.format(time_frame)
    #In case of nul results
    if len(msg_fr_r) == 0:
        msg_fr_r = 'None\n'
    if len(msg_cd_r) == 0:
        msg_cd_r = 'None\n'

    return msg_fr,msg_cd,msg_t,msg_fr_r,msg_cd_r

def recent_filter(full_results,i):
    '''
    Parameters:
        full_results;list of dictionaries of tuples of lists of dictionaries
        i;int
    Returns:
        filtered_results;list of dictionaries
    '''
    time_periods = ['1h','2h','4h','6h','8h','12h','1d']
    filtered_results = []
    #Find all divergences at 1 period ago
    for period in time_periods:
        #Take hist results (not currentdiv)
        results = full_results[period][0]
        for r in results:
            if r['position'][1] == i:
                #overwrite entry for 'period' with labeled period from loop
                r['period'] = period
                filtered_results.append(r)
    return filtered_results

def recent_filter_td(results):
    return [r for r in results if r['position'][1] == 2]

def recent_message(results):
    '''Makes the message for $recent command for embed
    Paramters:
        results;list of dictionaries
    Returns:
        msg_dict;list of dictionaries of lists
    '''
    #Separate into individual time periods
    r_1 = [r for r in results if r['period'] == '1h']
    r_2 = [r for r in results if r['period'] == '2h']
    r_4 = [r for r in results if r['period'] == '4h']
    r_6 = [r for r in results if r['period'] == '6h']
    r_8 = [r for r in results if r['period'] == '8h']
    r_12 = [r for r in results if r['period'] == '12h']
    r_24 = [r for r in results if r['period'] == '1d']
    results_list = [r_1, r_2, r_4, r_6, r_8, r_12, r_24]
    #Form messages
    tf_converter = {'1h':'1 Hour:','2h':'2 Hour:','4h':'4 Hour:','6h':'6 Hour:','8h':'8 Hour:','12h':'12 Hour:','1d':'1 Day:'}
    msg_dict = []
    for idx in range(len(results_list)):
        r = results_list[idx]
        msg_list = []
        msg = ''
        if len(r) != 0:
            #Add Title
            #msg = msg + '__{}__\n'.format(tf_converter[r[0]['period']])
            #Sort r based on score
            r = sorted(r, key=lambda r: float(r['score']),reverse=True)

            for rr in r:
                new_msg = '{} | {} | Score: {} | Divergence {} to {} periods ago\n'.format(rr['coin'], rr['type div'], rr['score'], rr['position'][1], rr['position'][0])
                if (len(msg) + len(new_msg)) > 1000:
                    msg_list.append(msg)
                    msg = new_msg
                else:
                    msg = msg + new_msg
            msg_list.append(msg)
            msg_dict.append({tf_converter[r[0]['period']]:msg_list})
        
    #Rewrite for empty results
    if len(msg_dict) == 0:
        msg_dict = [{'None':'None'}]
    return msg_dict

def valid_when(i):
    '''Checks for valid input on 'when' for filter command
    Parameters:
        when;int
    Returns:
        correct;bool
    '''
    try:
        int(i)
    except ValueError:
        return False
    if int(i) >= 42 or int(i) <= 1:
        return False
    else:
        return True

def prices_v2(data):
    prices = []
    for d in data:
        c = float(d['close'])
        o = float(d['open'])
        if c < o:
            prices.append(c)
        elif o < c:
            prices.append(o)
        else:
            prices.append(c)
    return prices[-42:]

def ll_comparator_v2(prices):
    '''
    *Possibly run the comparator for more days than 42 then shorter after results are gathered?
    (subtract 52 from indexes? after shorten?)
    '''
    lows = []
    lows_idx = []
    for i in range(1,len(prices) - 1):
        if prices[i] <= prices[i - 1] and prices[i] <= prices[i + 1]:
            lows.append(prices[i])
            lows_idx.append(i)
            
    lows2 = []
    lows2_idx = []
    for i in range(1,len(lows)-1):
        if lows[i] < lows[i - 1]:
            lows2.append(lows[i])
            lows2_idx.append(lows_idx[i])
    if lows[-1] < lows[2]:
        lows2.append(lows[-1])
        lows2_idx.append(lows_idx[-1])

    #Handle 
    lows3 = [lows2[0]]
    lows3_idx = [lows2_idx[0]]
    for i in range(1, len(lows2)):
        if (lows2[i] < lows2[i - 1]):
            lows3.append(lows2[i])
            lows3_idx.append(lows2_idx[i])
    return lows3, lows3_idx

#results_dict = [{'period':(results_fr,results_cd)}, ...]

my_token = os.environ.get('TOKEN')
bot.run(my_token)
