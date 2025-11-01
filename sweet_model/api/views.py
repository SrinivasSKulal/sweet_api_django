from django.forms import ValidationError
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Sweets
from .serializer import SweetsSerializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import permission_classes
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
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







@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')

    print(username)
    print(password)
    if not username and not password:
        return Response(
            {
                'error':'Username and password are required'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    if User.objects.filter(username=username).exists():
        return Response(
            {
                'error':'Username already exists'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        validate_password(password)


    except ValidationError as e:
        return Response(
            {
                'error':list(e.message)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    user = User.objects.create_user(
        username=username,
        password=password
    )

    return Response(
        {
            'message' : 'User created Successfully'
        },
        status=status.HTTP_201_CREATED
    )



@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username , password=password)


    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access':str(refresh.access_token),
            'refresh':str(refresh),
            'username':user.username
        })
    else:
        return Response(
            {
                'error':'Invalid Credentials'
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search(request):
    name = request.GET.get('name')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')


    sweets = Sweets.objects.all()

    if name:
        sweets = sweets.filter(name__icontains=name)
    if category:
        sweets = sweets.filter(category__icontains=category)
    if min_price:
        sweets = sweets.filter(price__gte=min_price)
    if max_price:
        sweets = sweets.filter(price__lte=max_price)

    serializer = SweetsSerializer(sweets, many=True)
    return Response(serializer.data)
    
