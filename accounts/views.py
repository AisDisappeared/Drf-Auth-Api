from http.client import responses
from multiprocessing import context
import stat
from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework.views import APIView
from .serializers import *
from rest_framework import status
from django.contrib.auth import authenticate
from .renderers import UserRenderer 
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated




# Json Web Token For Each User. 
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }





# Sign Up Class View 
class UserCreation(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({"token":token ,"msg":"You registered successfuly!"},status=status.HTTP_201_CREATED)





# Login Class View 
class LoginView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            user = authenticate(email=email,password=password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({"token":token,"msg" : "Login Successful"} , status=status.HTTP_200_OK)
            else:
                return Response({"errors":"Login Faild , Email or Password is not valid !"} , status=status.HTTP_404_NOT_FOUND)
            



# User Profile View Class 
class UserProfileView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request , format=None):
        user = request.user 
        serializer = UserProfileSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)






# User Change Password Class 
class UserChangePasswordView(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post (self,request,format=None):
        serializer = UserChangePasswordSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid():
            return Response({"msg":"password changed successfully"} ,status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        


        

# User Reset Password Classes 
# 1 ---> User Reset Password Request View 
class ResetPasswordRequestView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format=None):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"msg":"Reset Password's Link Sent, Please Check Your Email BOX."},status=status.HTTP_200_OK)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)





# 2 ---> User Reset Password View 
class ResetPasswordView(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request ,uid, token, format=None):
        serializer = ResetPasswordSerializer(data=request.data, context={"uid":uid,"token":token})
        if serializer.is_valid():
            return Response({"msg":"password reset successfully"},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)





# User Logout View
# For logout functionality we use the simple jwt blacklist token functionality system. 
class LogoutView(APIView):
    def post(self, request, format=None):
        try:
            refresh_token = request.data.get('refresh_token')
            token_object = RefreshToken(refresh_token)
            token_object.blacklist()
            return Response({"msg" : "You Logout Successfully"},status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)