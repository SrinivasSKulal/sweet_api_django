from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Sweets
from .serializer import SweetsSerializer


# @api_view(['GET'])
# def get_users(request):
    
#     sweets = Sweets.objects.all()
#     serializer = SweetsSerializer(sweets , many=True)
#     return Response(serializer.data)


# @api_view(['POST'])
# def create_user(request):
#     serializer = SweetsSerializer(data = request.data)

#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST','GET'])
def sweets(request):
    if request.method == 'GET':
        sweets = Sweets.objects.all()
        serializer = SweetsSerializer(sweets , many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        serializer = SweetsSerializer(data = request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors , status=status.HTTP_400_BAD_REQUEST)
