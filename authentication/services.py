from authentication.chat_engine_helper import ChatEngineHelper
from authentication.models import ChatUser
from rest_framework.exceptions import ValidationError


def delete_chat_user(chat_user: ChatUser):
    helper = ChatEngineHelper()
    try:
        helper.delete_chat_user(chat_user)
    except ValidationError:
        pass
    chat_user.delete(hard_delete=True)
