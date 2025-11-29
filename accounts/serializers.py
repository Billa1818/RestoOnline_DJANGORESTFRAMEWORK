from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, ClientDevice


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour le modèle User"""
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'user_type', 'phone', 'is_available', 'profile_picture',
            'total_deliveries', 'average_rating', 'password', 'confirm_password',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'total_deliveries', 'average_rating', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, attrs):
        if 'password' in attrs and 'confirm_password' in attrs:
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError({"confirm_password": "Les mots de passe ne correspondent pas."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour les listes"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'user_type', 'phone', 'is_available', 'average_rating']


class DeliveryPersonSerializer(serializers.ModelSerializer):
    """Serializer spécifique pour les livreurs"""
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'phone',
            'is_available', 'profile_picture', 'total_deliveries',
            'average_rating'
        ]
        read_only_fields = ['total_deliveries', 'average_rating']


class ClientDeviceSerializer(serializers.ModelSerializer):
    """Serializer pour ClientDevice"""
    order_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientDevice
        fields = [
            'id', 'device_id', 'device_info', 'device_name', 'fcm_token',
            'customer_name', 'customer_phone', 'customer_email',
            'first_seen', 'last_seen', 'is_active', 'is_blocked',
            'order_count'
        ]
        read_only_fields = ['id', 'first_seen', 'last_seen', 'order_count']
    
    def get_order_count(self, obj):
        return obj.orders.count()


class ClientDeviceCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création/enregistrement d'un appareil client"""
    class Meta:
        model = ClientDevice
        fields = [
            'device_id', 'device_info', 'device_name', 'fcm_token',
            'customer_name', 'customer_phone', 'customer_email'
        ]


# ===================================
# Serializers pour la réinitialisation de mot de passe
# ===================================

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer pour la demande de réinitialisation de mot de passe"""
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Valider le format de l'email"""
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer pour confirmer la réinitialisation du mot de passe"""
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Les mots de passe ne correspondent pas."
            })
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                "confirm_password": "Les mots de passe ne correspondent pas."
            })
        return attrs