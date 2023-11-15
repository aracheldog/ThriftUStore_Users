from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email']  # Add other fields as needed

    def to_representation(self, instance):
        data = super().to_representation(instance)
        extra_fields = {}

        # Iterate over all fields in the model

        for field_name in ["full_name", 'socialaccount', 'created_at', 'updated_at', 'address', 'zip_code', 'state', 'country', 'description']:
            # Check if the field is not in the serializer fields and is not the email field
            if field_name not in self.fields:
                # Use getattr to dynamically get the value of the field
                extra_fields[field_name] = getattr(instance, field_name, None)
        # Update the data dictionary with the extra fields
        data.update(extra_fields)
        return data
