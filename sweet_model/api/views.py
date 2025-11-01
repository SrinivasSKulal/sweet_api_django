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
from django.db import transaction
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
@permission_classes([IsAuthenticated])
def purchase(request, id):
    try:
        sweet = Sweets.objects.get(id=id)
    except Sweets.DoesNotExist:
        return Response(
            {
                'error':f'Sweet with id:{id} not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    purchase_quantity = request.data.get('quantity',1)


    if not isinstance(purchase_quantity,int) or purchase_quantity <= 0:
        return Response(
            {
                'error': 'Quantity  must be a positive integer'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    if sweet.quantity < purchase_quantity:
        return Response(
            {
                'error':'Insufficient funds',
                'available':sweet.quantity,
                'requested': purchase_quantity
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    #just to make sure every process happens or it roles back to previous state before this failed transaction
    with transaction.atomic():
        sweet.quantity -= purchase_quantity
        sweet.save()

    serializer = SweetsSerializer(sweet)

    return Response(
        {
            'message':'Purchase complete',
            'purchased_quantity' :  purchase_quantity,
            'total_cost' : float(sweet.price)*purchase_quantity,
            'sweet' : serializer.data
        },
        status=status.HTTP_200_OK
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restock(request, id):


    if not request.user.is_staff:
        return Response(
            {
                'error': 'Restock can only be done by a admin'
            },
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        sweet = Sweets.objects.get(id=id)
    except Sweets.DoesNotExist:
        return Response(
            {
                'error':f'Sweet with id:{id} not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )

    restock_quantity = request.data.get('quantity')

    if not restock_quantity:
        return Response(
            {
                'error':'Quantity is required'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    


    if not isinstance(restock_quantity,int) or restock_quantity <= 0:
        return Response(
            {
                'error': 'Quantity  must be a positive integer'
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        
    
    #just to make sure every process happens or it roles back to previous state before this failed transaction
    with transaction.atomic():
        old_quantity = sweet.quantity
        sweet.quantity += restock_quantity
        sweet.save()

    serializer = SweetsSerializer(sweet)

    return Response(
        {
            'message':'Restock complete complete',
            'previous_quantity' :  old_quantity,
            'new_quantity':sweet.quantity,
            'sweet' : serializer.data,

        },
        status=status.HTTP_200_OK
    )



@api_view(['PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def update(request,id):
    try:
        sweet = Sweets.objects.get(id=id)
    except Sweets.DoesNotExist:
        return Response(
            {
                'error':f'Sweet with id: {id} not found'
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if request.method == 'PUT':
        serializer = SweetsSerializer(sweet , data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data
            )
        return Response(serializer.errors  , status=status.HTTP_400_BAD_REQUEST)


    if request.method == 'DELETE':
        if not request.user.is_staff:
            return Response(
                {
                    'message':'Only admins can delete sweets'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        sweet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
    
