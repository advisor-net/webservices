from typing import Iterable

from rest_framework import mixins as drf_mixins
from rest_framework import serializers
from rest_framework.generics import GenericAPIView

from . import mixins


class BaseView(GenericAPIView):
    serializer_class = serializers.Serializer
    validator_class = serializers.Serializer

    def _prepare_response(self, data):
        if isinstance(data, Iterable):
            return self._serialize_collection(data)
        return self._serialize_obj(data)

    def _serialize_collection(self, collection):
        return self._serialize_obj(collection, many=True)

    def _serialize_obj(self, obj, many=False):
        return self.get_serializer_class()(
            instance=obj, context=self.get_serializer_context(), many=many
        ).data

    def get_validator_class(self):
        return self.validator_class

    def get_validator_context(self):
        return self.get_serializer_context()

    def get_validator(self, instance=None, data=None, many=False, partial=False):
        """Return the validator instance that should be used for validating input"""
        validator_class = self.get_validator_class()
        context = self.get_validator_context()
        return validator_class(
            instance, data=data, many=many, partial=partial, context=context
        )


# Concrete view classes that provide method handlers
# by composing the mixin classes with the base view.


class CreateAPIView(mixins.CreateViewMixin, BaseView):
    """
    Concrete view for creating a model instance.
    """

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(drf_mixins.ListModelMixin, BaseView):
    """
    Concrete view for listing a queryset.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(drf_mixins.RetrieveModelMixin, BaseView):
    """
    Concrete view for retrieving a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class DestroyAPIView(mixins.DestroyViewMixin, BaseView):
    """
    Concrete view for deleting a model instance.
    """

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class UpdateAPIView(mixins.UpdateViewMixin, BaseView):
    """
    Concrete view for updating a model instance.
    """

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class ListCreateAPIView(drf_mixins.ListModelMixin, mixins.CreateViewMixin, BaseView):
    """
    Concrete view for listing a queryset or creating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(
    drf_mixins.RetrieveModelMixin, mixins.UpdateViewMixin, BaseView
):
    """
    Concrete view for retrieving, updating a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(
    drf_mixins.RetrieveModelMixin, mixins.DestroyViewMixin, BaseView
):
    """
    Concrete view for retrieving or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(
    drf_mixins.RetrieveModelMixin,
    mixins.UpdateViewMixin,
    mixins.DestroyViewMixin,
    BaseView,
):
    """
    Concrete view for retrieving, updating or deleting a model instance.
    """

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
