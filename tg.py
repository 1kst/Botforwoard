from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from telegram import Update, Bot
import logging

# 请替换为您自己的Token
TOKEN = '********************************'
# 您的用户ID
MY_USER_ID = 123456

# 配置日志记录
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# 用于存储消息映射的字典，键为转发给您的消息ID，值为原始消息的发送者ID
message_map = {}

# 消息处理函数
def handle_message(update: Update, context: CallbackContext):
    # 检查是否是图片或文件
    if update.message.photo or update.message.document:
        # 转发图片或文件
        forwarded_message = context.bot.forward_message(chat_id=MY_USER_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
        # 记录原始消息的发送者ID
        message_map[forwarded_message.message_id] = update.effective_chat.id
        logger.info(f"Media from {update.effective_user.first_name} ({update.effective_chat.id}) forwarded to user {MY_USER_ID}")
    else:
        # 转发文本消息
        forwarded_message = context.bot.forward_message(chat_id=MY_USER_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
        # 记录原始消息的发送者ID
        message_map[forwarded_message.message_id] = update.effective_chat.id
        logger.info(f"Message from {update.effective_user.first_name} ({update.effective_chat.id}) forwarded to user {MY_USER_ID}")

# 回复处理函数
def handle_reply(update: Update, context: CallbackContext):
    # 检查是否为您的回复
    if update.effective_user.id == MY_USER_ID:
        # 获取原始消息的发送者ID
        original_chat_id = message_map.get(update.message.reply_to_message.message_id)
        if original_chat_id:
            # 转发回复到原始发送者
            context.bot.send_message(chat_id=original_chat_id, text=update.message.text)
            logger.info(f"Reply from {update.effective_user.first_name} sent to original user ({original_chat_id})")
        else:
            logger.warning("Original message not found for reply.")

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    # 添加消息处理器，这里我们使用 Filters.all 以确保所有消息都被捕捉
    dp.add_handler(MessageHandler(Filters.all & ~Filters.command & ~Filters.reply, handle_message))
    dp.add_handler(MessageHandler(Filters.text & Filters.reply & Filters.user(user_id=MY_USER_ID), handle_reply))

    # 开始机器人
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
