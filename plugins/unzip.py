# the logging things
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import shutil
import subprocess
import time
from helper_funcs.display_progress import humanbytes, progress_for_pyrogram
# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from sample_config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply
from pyrogram.errors import PeerIdInvalid, ChannelInvalid, FloodWait
from pyrogram.emoji import *
#from helper_funcs.chat_base import TRChatBase
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes


@pyrogram.Client.on_message(pyrogram.filters.command(["unzip"]))
async def unzip(bot, update):
    #TRChatBase(update.from_user.id, update.text, "unzip")
    if str(update.from_user.id) in Config.AUTH_USERS:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    saved_file_path = Config.DOWNLOAD_LOCATION + \
        "/" + str(update.from_user.id) + ".unzip.zip"
    if os.path.exists(saved_file_path):
        os.remove(saved_file_path)
    reply_message = update.reply_to_message
    if ((reply_message is not None) and
        (reply_message.document is not None) and
        (reply_message.document.file_name.endswith(Translation.UNZIP_SUPPORTED_EXTENSIONS))):
        a = await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.DOWNLOAD_START,
            reply_to_message_id=update.message_id
        )
        c_time = time.time()
        try:
            await bot.download_media(
                message=reply_message,
                file_name=saved_file_path,
                progress=progress_for_pyrogram,
                progress_args=(Translation.DOWNLOAD_START, a, c_time)
            )
        except (ValueError) as e:
            await bot.edit_message_text(
                chat_id=update.chat.id,
                text=str(e),
                message_id=a.message_id
            )
        else:
            await bot.edit_message_text(
                chat_id=update.chat.id,
                text=Translation.SAVED_RECVD_DOC_FILE,
                message_id=a.message_id
            )
            extract_dir_path = Config.DOWNLOAD_LOCATION + \
                "/" + str(update.from_user.id) + "zipped" + "/"
            if not os.path.isdir(extract_dir_path):
                os.makedirs(extract_dir_path)
            await bot.edit_message_text(
                chat_id=update.chat.id,
                text=Translation.EXTRACT_ZIP_INTRO_THREE,
                message_id=a.message_id
            )
            try:
                command_to_exec = [
                    "unzip",
                    "e",
                    "-o" + extract_dir_path,
                    saved_file_path
                ]
                # https://stackoverflow.com/a/39629367/4723940
                logger.info(command_to_exec)
                t_response = subprocess.check_output(
                    command_to_exec, stderr=subprocess.STDOUT)
                # https://stackoverflow.com/a/26178369/4723940
            except:
                try:
                    #os.remove(saved_file_path)
                    shutil.rmtree(extract_dir_path)
                except:
                    pass
                await bot.edit_message_text(
                    chat_id=update.chat.id,
                    text=Translation.EXTRACT_ZIP_ERRS_OCCURED,
                    disable_web_page_preview=True,
                    parse_mode="html",
                    message_id=a.message_id
                )
            else:
                os.remove(saved_file_path)
                inline_keyboard = []
                zip_file_contents = os.listdir(extract_dir_path)
                i = 0
                for current_file in zip_file_contents:
                    cb_string = "ZIP:{}:ZIP".format(str(i))
                    inline_keyboard.append([
                        InlineKeyboardButton(
                            current_file,
                            callback_data=cb_string.encode("UTF-8")
                        )
                    ])
                    i = i + 1
                cb_string = "ZIP:{}:ZIP".format("ALL")
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "Upload All Files",
                        callback_data=cb_string.encode("UTF-8")
                    )
                ])
                cb_string = "ZIP:{}:ZIP".format("NONE")
                inline_keyboard.append([
                    InlineKeyboardButton(
                        "Cancel",
                        callback_data=cb_string.encode("UTF-8")
                    )
                ])
                reply_markup = InlineKeyboardMarkup(inline_keyboard)
                files = await bot.edit_message_text(
                    chat_id=update.chat.id,
                    text=Translation.EXTRACT_ZIP_STEP_TWO,
                    message_id=a.message_id,
                    reply_markup=reply_markup,
                )
            
            #try:
                #await bot.edit_message_text(
                    #chat_id=message.chat.id,
                    #text=Translation.UPLOAD_START,
                    #reply_to_message_id=a.message_id
                #)

            c_time = time.time()
            await bot.send_document(
                chat_id=update.chat.id,
                document=files,
                #thumb=thumb_image_path,
                #caption=script.CAPTION_TEXT.format(newfile_name),
                # reply_markup=reply_markup,
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    a, 
                    c_time
                )
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.EXTRACT_ZIP_INTRO_ONE,
            reply_to_message_id=update.message_id
        )
