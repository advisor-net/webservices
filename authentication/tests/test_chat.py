from authentication.chat_engine_helper import ChatEngineHelper
from authentication.factories import UserFactory
from authentication.models import ChatUser
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from webservices.test_utils import BaseJWTAPITestCase


class TestChatHelperTestCase(BaseJWTAPITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.authenticate_with_generated_token(self.user)
        self.helper = ChatEngineHelper()
        self.chat_user = self.helper.create_chat_user(self.user, False)
        resp = self.helper.get_chat_user_by_id(self.chat_user.chat_engine_id)
        self.assertEqual(resp["username"], self.user.handle)

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
        user = UserFactory()
        url = reverse('create_chat_user', kwargs=dict(uuid=str(user.uuid)))
        response = self.client.post(url, data=dict(agreed_to_terms=True))
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data['chat_user']['username'], user.handle)
        self.helper.delete_chat_user(user.chat_user)

    def test_update_agree_to_terms(self):
        url = reverse('update_chat_terms', kwargs=dict(uuid=str(self.user.uuid)))
        response = self.client.post(url, data=dict(agreed_to_terms=True))
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(response.data['chat_user']['agreed_to_terms'])

    def tearDown(self):
        self.helper.delete_chat_user(self.chat_user)
        with self.assertRaises(ValidationError):
            self.helper.get_chat_user_by_id(self.chat_user.chat_engine_id)
