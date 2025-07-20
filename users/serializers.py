from rest_framework import serializers
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        
        fields = ('id', 'email', 'password', 'name', 'address', 'phone')
        
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            phone=validated_data['phone'],
            address=validated_data.get('address', None)
        )
        
        return user

# This serializer is used for viewing and updating user profiles.
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'address', 'phone')
        read_only_fields = ('id', 'email')

    def validate(self, data):
        
        if self.instance:
            if 'email' in self.initial_data:
                raise serializers.ValidationError({'email': 'Email address cannot be changed.'})
            if 'id' in self.initial_data:
                raise serializers.ValidationError({'id': 'The ID cannot be changed.'})
        
        return data