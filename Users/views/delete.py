from django.contrib.auth import logout
from rest_framework.views import APIView


class UserDeleteView(APIView):

    def delete(self, request):
        user = request.user
        print(user)
        # if user exists, delete user
        if user:
            user.delete()
            logout(request)  # logout
            messages.success(request, 'Your account has been deleted.')
            return Response({'message': 'Account deleted successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)