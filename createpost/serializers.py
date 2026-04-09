from rest_framework import serializers
from .models import Post, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer








# class PostSerializer(serializers.ModelSerializer):
#     # Get username and fullname directly from the related User model
#     author = serializers.CharField(source="author.username", read_only=True)
#     author_fullname = serializers.CharField(source="author.fullname", read_only=True)
    
#     # We use SerializerMethodField for the profile pic to handle the full URL safely
#     profile_pic = serializers.SerializerMethodField()

#     class Meta:
#         model = Post
#         fields = ["id", "author", "author_fullname", "content", "image", "created_at", "profile_pic"]

#     def get_profile_pic(self, obj):
#         request = self.context.get('request')
#         if obj.author.profile_pic:
#             url = obj.author.profile_pic.url
#             # build_absolute_uri ensures http://127.0.0.1:8000 is added
#             if request is not None:
#                 return request.build_absolute_uri(url)
#             return obj.author.profile_pic.url
#         return None


# class PostSerializer(serializers.ModelSerializer):
#     author = serializers.CharField(source="author.username", read_only=True)
#     author_fullname = serializers.CharField(source="author.fullname", read_only=True)

#     profile_pic = serializers.SerializerMethodField()
#     image_url = serializers.SerializerMethodField()  # ✅ NEW FIELD

#     class Meta:
#         model = Post
#         fields = [
#             "id",
#             "author",
#             "author_fullname",
#             "content",
#             "image",        # ✅ KEEP THIS (for upload)
#             "image_url",    # ✅ ADD THIS (for display)
#             "created_at",
#             "profile_pic"
#         ]

#     def get_profile_pic(self, obj):
#         request = self.context.get('request')
#         if obj.author.profile_pic:
#             url = obj.author.profile_pic.url
#             return request.build_absolute_uri(url) if request else url
#         return None

#     def get_image_url(self, obj):
#         request = self.context.get('request')
#         if obj.image:
#             url = obj.image.url
#             return request.build_absolute_uri(url) if request else url
#         return None

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="author.username", read_only=True)
    author_fullname = serializers.CharField(source="author.fullname", read_only=True)

    profile_pic = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "author",
            "author_fullname",
            "content",
            "image",
            "image_url",
            "created_at",
            "profile_pic"
        ]

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        if obj.author.profile_pic:
            url = obj.author.profile_pic.url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return None

    def update(self, instance, validated_data):
        image = validated_data.pop('image', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if image:
            instance.image = image

        instance.save()
        return instance




# 1. SIGNUP SERIALIZER
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'fullname', 'email', 'password', 'bio', 'profile_pic']

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password'],
#             fullname=validated_data.get('fullname', ''),
#             bio=validated_data.get('bio', ''),
#             profile_pic=validated_data.get('profile_pic', None)
#         )
#         return user


# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'fullname', 'email', 'password', 'bio', 'profile_pic']
#         extra_kwargs = {
#             'password': {'write_only': True}
#         }

#     def create(self, validated_data):
#         return User.objects.create_user(**validated_data)

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'fullname', 'email', 'password', 'bio', 'profile_pic']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        profile_pic = validated_data.pop('profile_pic', None)

        # create user first
        user = User.objects.create_user(**validated_data)

        # assign image separately
        if profile_pic:
            user.profile_pic = profile_pic
            user.save()

        return user





# 2. LOGIN SERIALIZER (Customized to return profile data with the token)
# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         data = super().validate(attrs)
#         # Add extra data to the response
#         data['username'] = self.user.username
#         data['fullname'] = self.user.fullname
#         data['bio'] = self.user.bio
#         data['profile_pic'] = self.user.profile_pic.url if self.user.profile_pic else None
#         data['is_staff'] = self.user.is_staff
#         return data


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        request = self.context.get('request')

        data['username'] = self.user.username
        data['fullname'] = self.user.fullname
        data['bio'] = self.user.bio
        data['is_staff'] = self.user.is_staff

        if self.user.profile_pic:
            url = self.user.profile_pic.url
            data['profile_pic'] = request.build_absolute_uri(url) if request else url
        else:
            data['profile_pic'] = None

        return data


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'fullname', 'email', 'bio', 'profile_pic', 'is_staff']
#         # We don't want users changing their username or staff status
#         read_only_fields = ['id', 'username', 'is_staff']


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'fullname', 'email', 'bio', 'profile_pic', 'is_staff']
        read_only_fields = ['id', 'username', 'is_staff']

    def get_profile_pic(self, obj):
        request = self.context.get('request')
        if obj.profile_pic:
            url = obj.profile_pic.url
            return request.build_absolute_uri(url) if request else url
        return None