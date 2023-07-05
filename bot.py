import youtube_dl
import telegram


# Replace YOUR_TOKEN with the token provided by BotFather
bot = telegram.Bot(token='YOUR_TOKEN')

def download_video(update, context):
    # Get the message sent to the bot
    message = update.message.text

    # Check if the message is a valid YouTube or Tiktok link
    if 'youtube' in message or 'tiktok' in message:
        # Ask the user for the desired video quality
        quality_keyboard = [[telegram.KeyboardButton('Low'), telegram.KeyboardButton('Medium'), telegram.KeyboardButton('High')]]
        reply_markup = telegram.ReplyKeyboardMarkup(quality_keyboard, resize_keyboard=True, one_time_keyboard=True)
        context.bot.send_message(chat_id=update.effective_chat.id, text='Please select the desired video quality:', reply_markup=reply_markup)

        # Wait for the user's response
        user_response = context.bot.get_updates()[0].message.text.lower()

        # Download the video and subtitles using youtube-dl
        ydl_opts = {'outtmpl': '%(id)s%(ext)s', 'format': 'best[height<={}]'.format(360 if user_response == 'low' else 480 if user_response == 'medium' else 720 if user_response == 'high' else 1080 if user_response == 'very high' else 2160), 'writesubtitles': True, 'subtitleslangs': ['en'], 'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}, {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(message, download=True)

        # Send the video file and subtitles to the user
        context.bot.send_video(chat_id=update.effective_chat.id, video=open(info_dict['id'] + '.mp4', 'rb'), supports_streaming=True)
        if info_dict.get('subtitles'):
            for lang in info_dict['subtitles']:
                context.bot.send_document(chat_id=update.effective_chat.id, document=open(info_dict['id'] + f'.{lang}.vtt', 'rb'))
        if info_dict.get('ext') == 'mp3':
            context.bot.send_audio(chat_id=update.effective_chat.id, audio=open(info_dict['id'] + '.mp3', 'rb'))
    else:
        # Send an error message if the link is not valid
        context.bot.send_message(chat_id=update.effective_chat.id, text='Invalid link')

# Create a handler for messages that contain a link
from telegram.ext import MessageHandler, Filters
link_handler = MessageHandler(Filters.text & (~Filters.command), download_video)

# Add the handler to the bot's dispatcher
from telegram.ext import Dispatcher
dispatcher = Dispatcher(bot, None)
dispatcher.add_handler(link_handler)

# Start the bot
bot.polling()