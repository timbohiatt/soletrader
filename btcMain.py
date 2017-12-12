from flask import *
from flask import jsonify
from decimal import *
from btcmarkets import BTCMarkets
import requests
import random
import socket
import time
import os

#Setting Environment Variables osx
#launchctl setenv PATH $PATH


app = Flask(__name__)


#====== GLOBALS ===================================================================================================================================================

v_BTC_Client = None
v_Trade = "TRUE"
v_count = 0
v_config = {'rfrshInt':30, 'opportunity':False, 'DecPrecision':10, 'BTCDivisor':100000000}

v_rates = []
v_old_rates = []
v_wallets = []
v_openOrders = []
v_portfolio = {}
v_portfolioBalance = 0.0




#====== ROUTES ===================================================================================================================================================
@app.route("/")
def main():
	global v_count
	setup()
	v_count = v_count + 1
	#Output the Amount of time the Site has Updated Data
	config = getConfig()
	#wallet = getWallet()
	rates = getMarketRates()

	#return send_from_directory('templates', 'home.html', value=wallets)
	return render_template('home.html',  config=config) #wallet=wallet, rates=rates,


@app.route("/dyn_data_update")
def dyn_up_Data():
	#msg("==== DATA UPDATE ====")
	setup()
	config = getConfig()
	wallet = getWallet()
	rates = getMarketRates()
	tradeHistory = getTradeHistory()

	portfolio = getPortfolioBalance(rates, wallet)
	openOrders = getPendingTrades()
	json_dict = {"Username":"timbohiatt", "Full Name":"Tim Hiatt", "Email":"timbohiatt@gmail.com" ,"Wallets":wallet, "Rates":rates, "Portfolio":portfolio, "TradeHistory":tradeHistory, "OpenOrders":openOrders, "Configuration":config}
	json_package = {"Account":json_dict}

	#	print  json.dumps(json_package, indent=4, sort_keys=True)
	msg(" Core Data Updated")
	#return render_template('obj_DataUpdate.html',  flask_RawData=json_package)
	return jsonify(json_package)

#====== SUPPORT FUNCTIONS ========================================================================================================================================

def setup():
	createClient()
	getConfig()

def getConfig():
#-- This Function Will Eventually pull all configuration fields from a DB and load them into Python Dictionary
	global v_config
	return v_config

def setConfig():
#-- This Function Will Eventually pull all configuration fields from the Python Dictionary and load them into SQL DB
	return 

def updateConfig(option, value):
#-- This Function will update the Config Python Dictionary with New Values. Then Call the setConfig() 
#	Function to write those values To The DB.
	global v_config
	if (option in v_config.keys()):
		if (v_config[option] is not value):
			msg("Updating Configuration Element: '"+str(option) + "' = '" + str(value)+"'")
			v_config[option] = value
		else:
			msg("Configuration Element: "+str(option) + " Already is set to " + str(value) + " No Change Made")
	return


#-- This Function is for correctig the BTC Markets Values by adding the Decimal Places back to the value.
def addSymbol(value):
	return (str("$"+str(value)))


def getDateTimeStamp():
	ts = time.strftime("%d-%m-%Y %H:%M:%S")
	return ts

def getPercentageChange(currentValue, originalValue):
	if (Decimal(originalValue) == 0):
		return str(0.0)
	else:
		change = Decimal(Decimal((Decimal(currentValue)/Decimal(originalValue)) * 100))
		return str(change)

#-- This Funtion handles the output of messages from the Screen. 
def msg(message):
	print("(*) |--->  " + str(message))


#-- This function created the BTC Markets Class object in the event that one isn't already created and existing.
def createClient():
	global v_BTC_Client
	if v_BTC_Client is None:
		v_BTC_Client = BTCMarkets(os.environ['BTCAPIKEY'], os.environ['BTCAPISECRET'])
		#msg("BTC Client Created")

	return


def detectChange(old, new):
	if (old is None):
		delta = True
		indicator = "U" 	#U = Up
		#print("Up -> From:" + str(old) + " To:" +str(new))
	elif (old == new):
		delta = False
		indicator = "N" 	#N = No Change
	elif (old > new):
		delta = True
		indicator = "D" 	#D = Down
		#print("Down -> From:" + str(old) + " To:" +str(new))
	elif (old < new):
		delta = True
		indicator = "U" 	#U = Up
		#print("Up -> From:" + str(old) + " To:" + str(new))
	else:
		delta = True
		indicator = "U" 	#U = Up
		#print("Up -> From:" + str(old) + " To:" +str(new))
	return indicator, delta



def getPortfolioBalance(rates, wallet):
	global v_rates, v_old_rates, v_portfolio

	#Move old to new
	v_old_portfolio = v_portfolio


	v_portfolioBalance = 0
	portfolio = {}
	portfolio['balance'] = Decimal(0.0)
	portfolio['pending'] = Decimal(0.0)
	portfolio['available'] = Decimal(0.0)

	for currency in wallet:
		if currency['balance'] > 0.0:
			if (currency['currency']  == "AUD"): 
				portfolio['balance'] = portfolio['balance'] + (Decimal(currency['balance']))
				portfolio['pending'] = portfolio['pending'] + (Decimal(currency['pending']))
				portfolio['available'] = portfolio['available'] + (Decimal(currency['available']))
			else:
				for rate in rates: 
					if (currency['currency'] == rate['instrument']):
						#Totals
						portfolio['balance'] = portfolio['balance'] + (Decimal(currency['balance'])*Decimal(rate['bestBid']))
						portfolio['pending'] = portfolio['pending'] + (Decimal(currency['pending'])*Decimal(rate['bestBid']))
						portfolio['available'] = portfolio['available'] + (Decimal(currency['available'])*Decimal(rate['bestBid']))
						
						




	portfolio['totalInvested'] = 10100.00
	valueProfitLoss = Decimal(Decimal(portfolio['balance']) - Decimal(portfolio['totalInvested']))
	portfolio['valueProfitLoss'] = str(Decimal(valueProfitLoss))
	#portfolio['valueProfitLoss_CI'], portfolio['valueProfitLoss_delta'] = detectChange(v_old_portfolio['valueProfitLoss'], portfolio['valueProfitLoss'])
	portfolio['percentProfitLoss'] = str(getPercentageChange(valueProfitLoss, portfolio['totalInvested']))
	#portfolio['percentProfitLoss_CI'], portfolio['percentProfitLoss_delta'] = detectChange(v_old_portfolio['percentProfitLoss'], portfolio['percentProfitLoss'])
	portfolio['balance'] = str(portfolio['balance']) 
	#portfolio['balance_CI'], portfolio['balance_delta'] = detectChange(v_old_portfolio['balance'], portfolio['balance'])
	portfolio['pending'] = str(portfolio['pending']) 
	#portfolio['pending_CI'], portfolio['pending_delta'] = detectChange(v_old_portfolio['bestBid'], portfolio['bestBid'])
	portfolio['available'] = str(portfolio['available'])
	#portfolio['available_CI'], portfolio['available_delta'] = detectChange(v_old_portfolio['available'], portfolio['available'])

	v_portfolio = portfolio
	return portfolio


#-- This function gets all the current market rates from BTC Markets. 
def getMarketRates():
	global v_rates, v_old_rates

	#Move old to new
	v_old_rates = v_rates
	v_rates = []
	
	currencyPair = [['ETH','AUD'],['BTC','AUD'],['XRP','AUD'],['BCH','AUD'],['LTC','AUD'],['ETC','AUD']]
	for pair in currencyPair:

		old_bestBid = 0.00000
		old_bestAsk = 0.00000
		old_lastPrice = 0.00000
		old_volume24h = 0.00000
		old_bestBid_PC = 0.00000
		old_bestAsk_PC = 0.00000
		old_lastPrice_PC = 0.00000
		old_volume24h_PC = 0.00000

		resp_rate = v_BTC_Client.get_market_tick(pair[0],pair[1])
		if resp_rate is not None:
			getcontext().prec = v_config['DecPrecision']
			rate = {}

			if v_old_rates is not None:
				for old_rate in v_old_rates:
					if (old_rate['instrument'] == resp_rate['instrument']):
						old_bestBid = old_rate['bestBid']
						old_bestAsk = old_rate['bestAsk']
						old_lastPrice = old_rate['lastPrice']
						old_volume24h = old_rate['volume24h']
						old_bestBid_PC = old_rate['bestBid_PC']
						old_bestAsk_PC = old_rate['bestAsk_PC']
						old_lastPrice_PC = old_rate['lastPrice_PC']
						old_volume24h_PC = old_rate['volume24h_PC']


			rate['instrument'] = str(resp_rate['instrument'])
			rate['currency'] =  str(resp_rate['currency'])
			rate['bestBid'] =  (resp_rate['bestBid'])
			rate['bestBid_CI'], rate['bestBid_delta'] = detectChange(old_bestBid, rate['bestBid'])
			#rate['bestBid_PC'] = getPercentageChange(rate['bestBid'], old_bestBid)
			rate['bestBid_PC'] = getPercentageChange(old_bestBid, rate['bestBid'])
			rate['bestBid_PC_CI'], rate['bestBid_PC_delta'] = detectChange(old_bestBid_PC, rate['bestBid_PC'])
			rate['bestAsk'] =  (resp_rate['bestAsk'])
			rate['bestAsk_CI'], rate['bestAsk_delta'] = detectChange(old_bestAsk, rate['bestAsk'])
			#rate['bestAsk_PC'] =  getPercentageChange(rate['bestAsk'], old_bestAsk)
			rate['bestAsk_PC'] =  getPercentageChange(old_bestAsk, rate['bestAsk'])
			rate['bestAsk_PC_CI'], rate['bestAsk_PC_delta'] = detectChange(old_bestAsk_PC,rate['bestAsk_PC'])
			rate['lastPrice'] =  (resp_rate['lastPrice'])
			rate['lastPrice_CI'], rate['lastPrice_delta'] = detectChange(old_lastPrice, rate['lastPrice'])
			#rate['lastPrice_PC'] = getPercentageChange(rate['lastPrice'], old_lastPrice)
			rate['lastPrice_PC'] = getPercentageChange(old_lastPrice, rate['lastPrice'])
			rate['lastPrice_PC_CI'], rate['lastPrice_PC_delta'] = detectChange(old_lastPrice_PC, rate['lastPrice_PC'])
			rate['volume24h'] =  (resp_rate['volume24h'])
			rate['volume24h_CI'], rate['volume24h_PC_delta'] = detectChange(old_volume24h, rate['volume24h'])
			#rate['volume24h_PC'] = getPercentageChange(rate['volume24h'], old_volume24h)
			rate['volume24h_PC'] = getPercentageChange(old_volume24h, rate['volume24h'])
			rate['volume24h_PC_CI'], rate['volume24h_PC_delta'] = detectChange(old_volume24h_PC, rate['volume24h_PC'])
			rate['sys_updated'] = getDateTimeStamp()
			#Add the Current Rate Data to the collection of rates.
			v_rates.append((rate))

	return v_rates

#-- This function is used to get all the Details about the Existing BTC Wallets.
def getWallet():
	global v_wallets
	v_accountBalances = v_BTC_Client.account_balance()
	v_wallets = []
	for currency in v_accountBalances:

		wallet = {}
		getcontext().prec = v_config['DecPrecision']
		wallet['currency'] = str(currency['currency'])
		wallet['balance'] = str((Decimal(currency['balance']))/ Decimal(v_config['BTCDivisor']))
		wallet['pending'] = str((Decimal(currency['pendingFunds']))/ Decimal(v_config['BTCDivisor']))
		wallet['available'] = str(Decimal(wallet['balance']) - Decimal(wallet['pending']))
		#Add the Current Wallet Data to the collection of rates.
		if (str(currency['currency']) == "AUD"):
			wallet['valueAUD'] = wallet['balance']
		else:
			for rate in v_rates:
				if (rate['instrument'] == wallet['currency']):
					wallet['valueAUD'] = str(Decimal(wallet['balance']) * Decimal(rate['bestBid']))


		v_wallets.append(wallet)
	

	return v_wallets


def getTradeHistory():
	global v_openOrders
	tradeHistory = v_BTC_Client.trade_history('AUD', 'ETH', 200, 809829145)
	v_tradeHistory = []

	for tradeItem in tradeHistory['trades']:
		trade = {}
		tradeItem['orderId'] = tradeItem['orderId']
		tradeItem['fee'] = tradeItem['fee']
		tradeItem['description'] = tradeItem['description']
		tradeItem['price'] = tradeItem['price']
		tradeItem['creationTime'] = tradeItem['creationTime']
		tradeItem['id'] = tradeItem['id']
		tradeItem['volume'] = tradeItem['volume']
		tradeItem['side'] = tradeItem['side']
		#Add the Current Trade Item Data to the collection of rates.
		v_tradeHistory.append(tradeItem)

	return v_tradeHistory

def getPendingTrades():
	v_openOrders= []
	currencyPair = [['AUD','ETH'],['ETH','AUD'],['BTC','AUD'],['XRP','AUD'],['BCH','AUD'],['LTC','AUD'],['ETC','AUD']]
	for pair in currencyPair:
		openOrders = v_BTC_Client.order_open(pair[0], pair[1], 200, 985787075)
		if openOrders['orders'] is not None:
			for orderItem in openOrders['orders']:
				order = {}
				order['clientRequestId'] = orderItem['clientRequestId']
				order['instrument'] = orderItem['instrument']
				order['orderType'] = orderItem['ordertype']
				order['price'] = str((Decimal(orderItem['price']))/ Decimal(v_config['BTCDivisor']))
				order['volume'] = str((Decimal(orderItem['volume']))/ Decimal(v_config['BTCDivisor']))
				order['openVolume'] = str((Decimal(orderItem['openVolume']))/ Decimal(v_config['BTCDivisor']))
				order['status'] = orderItem['status']
				v_openOrders.append(order)
	
	print v_openOrders

	return v_openOrders


if __name__ == '__main__':
	app.run(threaded=True)
#	app.run()