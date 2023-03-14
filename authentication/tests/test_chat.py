import json

from authentication.chat_engine_helper import ChatEngineHelper
from authentication.factories import UserFactory
from authentication.models import ChatUser
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from webservices.test_utils import BaseJWTAPITestCase


class TestChatHelperTestCase(BaseJWTAPITestCase):
    def setUp(self):
        self.user = UserFactory(handle="TEST_USER1")
        self.authenticate_with_generated_token(self.user)
        self.helper = ChatEngineHelper()
        self.chat_user = self.helper.create_chat_user(self.user, False)
        resp = self.helper.get_chat_user_by_id(self.chat_user.chat_engine_id)
        self.assertEqual(resp["username"], self.user.handle)
        custom_json = json.loads(resp["custom_json"])
        self.assertEqual(custom_json["uuid"], str(self.user.uuid))
        self.assertIsNotNone(self.chat_user.secret)

    def test_create_and_destroy_chat_user(self):
        self.assertTrue(ChatUser.objects.filter(user_id=self.user.id).exists())

    def test_update_chat_user_handle(self):
        self.user.handle = "new_handle_name"
        resp = self.helper.update_chat_user_username(self.chat_user, self.user.handle)
        self.assertEqual(resp['username'], "new_handle_name")

        # now test via the API
        url = reverse('update_handle', kwargs=dict(uuid=str(self.user.uuid)))
        response = self.client.patch(url, data=dict(handle='other_new_handle'))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.user.refresh_from_db()
        self.assertEqual(self.user.handle, 'other_new_handle')
        resp = self.helper.get_chat_user_by_id(self.chat_user.chat_engine_id)
        self.assertEqual(resp["username"], 'other_new_handle')

    def test_create_chat_user_api(self):
        user = UserFactory(handle='TEST_USER2')
        url = reverse('get_or_create_chat_user', kwargs=dict(uuid=str(user.uuid)))
        response = self.client.post(url, data=dict(agreed_to_terms=True))
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data['chat_user']['username'], user.handle)
        self.assertEqual(ChatUser.objects.count(), 2)
        # test get or create functionality as well here
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(ChatUser.objects.count(), 2)
        self.helper.delete_chat_user(user.chat_user)

    def test_update_agree_to_terms(self):
        url = reverse('update_chat_terms', kwargs=dict(uuid=str(self.user.uuid)))
        response = self.client.post(url, data=dict(agreed_to_terms=True))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(response.data['chat_user']['agreed_to_terms'])

    def test_public_api(self):
        response = self.helper.get_public_user_details(self.chat_user)
        self.assertEqual(response["username"], self.chat_user.username)

    def test_create_list_delete_direct_chats(self):
        # create user
        user = UserFactory(handle='TEST_USER2')
        url = reverse('get_or_create_chat_user', kwargs=dict(uuid=str(user.uuid)))
        response = self.client.post(url, data=dict(agreed_to_terms=True))
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data['chat_user']['username'], user.handle)
        # create direct chat
        resp = self.helper.get_or_create_direct_chat(self.chat_user, user.chat_user)
        chat_list = self.helper.get_chats_for_chat_user(self.chat_user)
        self.assertEqual(1, len(chat_list))
        chat = chat_list[0]
        self.assertEqual(chat["id"], resp["id"])
        self.helper.delete_chat(self.chat_user, chat["id"])
        chat_list = self.helper.get_chats_for_chat_user(self.chat_user)
        self.assertEqual(0, len(chat_list))
        self.helper.delete_chat_user(user.chat_user)

    def tearDown(self):
        self.helper.delete_chat_user(self.chat_user)
        with self.assertRaises(ValidationError):
            self.helper.get_chat_user_by_id(self.chat_user.chat_engine_id)
