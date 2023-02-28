from rest_framework import status
from rest_framework.response import Response


class CreateViewMixin:
    def perform_create(self, validator):
        raise NotImplementedError(
            'You should implement `perform_create` for <{cls}> view'.format(
                cls=self.__class__.__name__
            )
        )

    def create(self, request, *args, **kwargs):
        validator = self.get_validator(data=request.data)
        validator.is_valid(raise_exception=True)
        obj = self.perform_create(validator)
        data = self._serialize_obj(obj)
        return Response(data=data, status=status.HTTP_201_CREATED)


class UpdateViewMixin:
    def perform_update(self, validator):
        raise NotImplementedError(
            'You should implement `perform_update` for <{cls}> view'.format(
                cls=self.__class__.__name__
            )
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        validator = self.get_validator(instance, data=request.data, partial=partial)
        validator.is_valid(raise_exception=True)
        obj = self.perform_update(validator)
        return Response(self._serialize_obj(obj), status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class DestroyViewMixin:
    def perform_destroy(self, instance):
        raise NotImplementedError(
            'You should implement `perform_destroy` for <{cls}> view'.format(
                cls=self.__class__.__name__
            )
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
