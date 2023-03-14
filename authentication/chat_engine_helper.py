import json
from typing import Optional, Union

import requests
from authentication.models import ChatUser, User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from rest_framework.exceptions import ValidationError


class METHODS:
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"
    PATCH = "PATCH"
    PUT = "PUT"


class ChatEngineHelper:
    """
    API docs: https://rest.chatengine.io/#6775ec07-601e-4730-ba08-d87bc81d019a

    """

    CHAT_ENGINE_BASE_URL = settings.CHAT_ENGINE_BASE_URL
    CHAT_ENGINE_PROJECT_ID = settings.CHAT_ENGINE_PROJECT_ID
    CHAT_ENGINE_SECRET_KEY = settings.CHAT_ENGINE_SECRET_KEY

    def generate_private_headers(self) -> dict:
        return {
            "PRIVATE-KEY": self.CHAT_ENGINE_SECRET_KEY,
        }

    def generate_public_headers(self, chat_user: ChatUser) -> dict:
        return {
            "Project-ID": self.CHAT_ENGINE_PROJECT_ID,
            "User-Name": chat_user.username,
            "User-Secret": str(chat_user.password),
        }

    def perform_request(
        self,
        url_detail: str,
        headers: dict,
        method: str,
        payload: dict,
    ) -> Union[dict, list]:
        url = f'{self.CHAT_ENGINE_BASE_URL}{url_detail}'
        response = requests.request(method, url, headers=headers, data=payload)
        if response.status_code == 500:
            raise ValidationError(detail="Unknown error")
        elif response.status_code == 404:
            raise ValidationError(detail="Object not found")
        elif response.status_code >= 400:
            raise ValidationError(detail=response.json().get("detail", "Unknown error"))
        return response.json()

    def perform_private_request(
        self,
        url_detail: str,
        method: str = METHODS.GET,
        payload: Optional[dict] = None,
    ) -> Union[dict, list]:
        return self.perform_request(
            url_detail=url_detail,
            headers=self.generate_private_headers(),
            method=method,
            payload=payload or dict(),
        )

    def perform_public_request(
        self,
        chat_user: ChatUser,
        url_detail: str,
        method: str = METHODS.GET,
        payload: Optional[dict] = None,
    ):
        return self.perform_request(
            url_detail=url_detail,
            headers=self.generate_public_headers(chat_user),
            method=method,
            payload=payload or dict(),
        )

    def get_chat_user_by_id(self, chat_engine_user_id: int) -> dict:
        url_detail = f"users/{chat_engine_user_id}/"
        return self.perform_private_request(url_detail)

    def get_or_create_chat_user(self, user: User, agreed_to_terms: bool) -> ChatUser:
        try:
            return user.chat_user
        except ObjectDoesNotExist:
            return self.create_chat_user(user, agreed_to_terms)

    @transaction.atomic
    def create_chat_user(self, user: User, agreed_to_terms: bool) -> ChatUser:
        assert user.handle is not None
        assert not ChatUser.objects.filter(user_id=user.id).exists()
        url_detail = "users/"
        obj = ChatUser(user=user, username=user.handle, agreed_to_terms=agreed_to_terms)
        payload = dict(
            username=user.handle,
            secret=str(obj.password),
            custom_json=json.dumps(dict(uuid=str(user.uuid))),
        )
        resp = self.perform_private_request(
            url_detail, method=METHODS.POST, payload=payload
        )
        obj.chat_engine_id = resp["id"]
        obj.secret = resp["secret"]
        obj.save()
        return obj

    @transaction.atomic
    def delete_chat_user(self, chat_user: ChatUser):
        url_detail = f'users/{chat_user.chat_engine_id}/'
        self.perform_private_request(url_detail, method=METHODS.DELETE)

    @transaction.atomic
    def update_chat_user_username(self, chat_user: ChatUser, new_username: str) -> dict:
        url_detail = f'users/{chat_user.chat_engine_id}/'
        return self.perform_private_request(
            url_detail, method=METHODS.PATCH, payload=dict(username=new_username)
        )

    def get_public_user_details(self, chat_user: ChatUser) -> dict:
        url_detail = "users/me/"
        return self.perform_public_request(chat_user, url_detail, METHODS.GET)

    def get_chats_for_chat_user(self, chat_user: ChatUser) -> list:
        url_detail = 'chats/'
        return self.perform_public_request(chat_user, url_detail)

    def get_or_create_direct_chat(
        self, sender_chat_user: ChatUser, recipient_chat_user: ChatUser
    ):
        url_detail = 'chats/'
        payload = dict(
            usernames=[recipient_chat_user.username],
            is_direct_chat=True,
        )
        return self.perform_public_request(
            sender_chat_user, url_detail, method=METHODS.PUT, payload=payload
        )

    def delete_chat(self, chat_user: ChatUser, chat_id: int):
        url_detail = f'chats/{chat_id}/'
        return self.perform_public_request(chat_user, url_detail, method=METHODS.DELETE)

    def delete_all_chats_for_chat_user(self, chat_user: ChatUser):
        for chat in self.get_chats_for_chat_user(chat_user):
            self.delete_chat(chat_user, chat["id"])
