from authentication.chat_engine_helper import ChatEngineHelper
from authentication.models import ChatUser


def delete_chat_user(chat_user: ChatUser):
    helper = ChatEngineHelper()
    helper.delete_chat_user(chat_user)
    chat_user.delete(hard_delete=True)
