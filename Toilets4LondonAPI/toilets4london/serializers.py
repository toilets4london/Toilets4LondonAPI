from rest_framework import serializers
from Toilets4LondonAPI.toilets4london.models import Toilet
from django.contrib.auth.models import User


# class ToiletSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     address = serializers.CharField(required=False, allow_blank=True, max_length=500)
#     borough = serializers.CharField(required=False, allow_blank=True, max_length=100)
#
#     def create(self, validated_data):
#         return Toilet.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         """
#         Update and return an existing Toilet instance, given the validated data.
#         """
#         instance.address = validated_data.get('address', instance.address)
#         instance.borough = validated_data.get('borough', instance.borough)
#         instance.save()
#         return instance


class ToiletSerializer(serializers.HyperlinkedModelSerializer):
    """
    shortcut for creating serializer classes:
    An automatically determined set of fields.
    Simple default implementations for the create() and update() methods.
    """

    # The untyped ReadOnlyField is always read-only,
    # and will be used for serialized representations,
    # but will not be used for updating model instances
    # when they are deserialized.
    # We could have also used CharField(read_only=True) here.

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Toilet
        fields = ['url', 'id', 'owner', 'address', 'borough']


class UserSerializer(serializers.HyperlinkedModelSerializer):
    toilets = serializers.PrimaryKeyRelatedField(many=True, queryset=Toilet.objects.all())

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'toilets']