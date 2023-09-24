from rest_framework.views import APIView
from rest_framework.response import Response


class PostAPIView(APIView):
    def get(self, request, pk):
        return Response({"pk": pk})
