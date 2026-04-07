from rest_framework import generics, permissions, status
from .models import Post, User
from .serializers import PostSerializer, RegisterSerializer, MyTokenObtainPairSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from .permissions import IsAuthorOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response



# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()



class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    # This ensures ONLY logged-in users can post
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # This tells Django: "The author is the guy who sent this request"
        serializer.save(author=self.request.user)
    

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    
    # Permission logic:
    # 1. User must be logged in (IsAuthenticatedOrReadOnly)
    # 2. User must be the author to EDIT/DELETE (IsAuthorOrReadOnly)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]



class PostListCreateView(generics.ListCreateAPIView):
    # 1. Fetch all posts and order them by newest first (LinkedIn style)
    queryset = Post.objects.all().order_by('-created_at')
    
    # 2. Use the PostSerializer to handle data
    serializer_class = PostSerializer
    
    # 3. Permissions: Read-only for guests, Full access for logged-in users
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # 4. Automatically set the author to the user who is currently logged in
        # This prevents users from trying to 'spoof' or post as someone else
        serializer.save(author=self.request.user)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

# Login View (Using our custom serializer)
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



class LogoutView(APIView):
    # The user MUST be logged in to logout
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # We need the REFRESH token from the request body
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except KeyError:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    






class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET: Returns the profile of the logged-in user.
    PUT/PATCH: Updates the profile of the logged-in user.
    """
    serializer_class = UserSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Instead of looking for an ID in the URL (like /profile/1/),
        # this returns the user associated with the JWT token.
        return self.request.user