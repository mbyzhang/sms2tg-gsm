#!/usr/bin/env python3

import argparse
import logging
import telebot
import threading
from gsmmodem.modem import GsmModem
from db import Db
from config import load_config

parser = argparse.ArgumentParser()
parser.add_argument("config", nargs="?", default="config.yaml", help="Path to the configuration file")
args = parser.parse_args()

config = load_config(args.config)

bot = telebot.TeleBot(config.telegram.bot_token)
db = Db(config.db_filename)

def broadcast_message(text):
    for chat_id in config.telegram.chat_ids:
        bot.send_message(chat_id, text, parse_mode="Markdown")

@bot.message_handler(commands=['reset'])
def bot_reset(message):
    broadcast_message("Resetting")
    bot.stop_polling()

@bot.message_handler(commands=['status'])
def bot_status(message):
    text = f"""
**IMEI**: {modem.imei}
**Own number**: {modem.ownNumber}
**Network name**: {modem.networkName}
**Modem manufacturer**: {modem.manufacturer}
**Modem model**: {modem.model}
**Signal strength**: {modem.signalStrength}
"""
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

def handleSms(sms):
    print(u'== SMS message received ==\nFrom: {0}\nTime: {1}\nMessage:\n{2}\n'.format(sms.number, sms.time, sms.text))
    db.add_sms(sms)
    text = f"*{sms.number}* @ {sms.time}\n{sms.text}"
    broadcast_message(text)

def handleIncomingCall(call):
    db.add_call(call)
    broadcast_message(f"Call from {call.number}")
    call.hangup()

def main():
    global modem
    broadcast_message("Starting")
    print('Initializing modem...')
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    modem = GsmModem(config.modem.port, config.modem.baudrate, smsReceivedCallbackFunc=handleSms, incomingCallCallbackFunc=handleIncomingCall)
    modem.smsTextMode = False
    modem.connect(config.modem.pin)
    print('AT+CGATT=0:', modem.write('AT+CGATT=0', parseError=False))
    print('AT+CIPSHUT:', modem.write('AT+CIPSHUT', parseError=False, waitForResponse=False))
    print('Waiting for SMS message...')
    broadcast_message("Started")
    modem.processStoredSms()
    bot_thread = threading.Thread(target=bot.infinity_polling)
    bot_thread.start()

    try:
        bot_thread.join()
    finally:
        modem.close()

if __name__ == '__main__':
    main()

