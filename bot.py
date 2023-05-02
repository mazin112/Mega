import os
import requests
import telebot
from mega import Mega
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
pip install asyncio --upgrad

bot_token = os.environ['BOT_TOKEN']
mega_email = os.environ['MEGA_EMAIL']
mega_password = os.environ['MEGA_PASSWORD']

bot = telebot.TeleBot(bot_token)

# Handler for when a user sends a direct link to the bot
@bot.message_handler(regexp='^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$')
def handle_link(message):
    # Get the direct link sent by the user
    direct_link = message.text

    # Download the file from the direct link
    response = requests.get(direct_link)
    file_content = response.content

    # Upload the file to Mega
    m = Mega()
    mega = m.login(mega_email, mega_password)
    uploaded_file = mega.upload(file_content)

    # Create tidy buttons for the user to download the file
    file_url = mega.get_upload_link(uploaded_file)
    download_button = InlineKeyboardButton(text='Download file', url=file_url)
    delete_button = InlineKeyboardButton(text='Delete file', callback_data=f'delete:{uploaded_file}')
    markup = InlineKeyboardMarkup([[download_button, delete_button]])

    # Send the user a message with the download and delete buttons
    bot.send_message(message.chat.id, 'File uploaded to Mega!', reply_markup=markup)

# Handler for when a user clicks the delete button
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete:'))
def handle_delete_callback(call):
    # Get the file ID from the callback data
    file_id = call.data.split(':')[1]

    # Delete the file from Mega
    m = Mega()
    mega = m.login(mega_email, mega_password)
    mega.remove(file_id)

    # Send a message to the user confirming the file deletion
    bot.send_message(call.message.chat.id, 'File deleted from Mega.')

# Start the bot
bot.polling()
