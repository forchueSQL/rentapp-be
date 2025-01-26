from rest_framework import generics
from .models import  User, Property, PropertyPhoto, Inquiry, PropertyStatus
from .serializers import UserSerializer, PropertySerializer, PropertyPhotoSerializer, InquirySerializer, PropertyStatusSerializer
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, BotoCoreError, ClientError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.conf import settings
import magic

class UploadPhotoView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        mime = magic.Magic(mime=True)
        file_mime_type = mime.from_buffer(file.read(1024))
        file.seek(0)  # Reset file pointer to the beginning

        allowed_mime_types = ['image/jpeg', 'image/png']
        if file_mime_type not in allowed_mime_types:
            return Response({"error": "Invalid file type"}, status=status.HTTP_400_BAD_REQUEST)

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

        try:
            s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file.name)
            file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file.name}"
            return Response({"file_url": file_url}, status=status.HTTP_201_CREATED)
        except NoCredentialsError:
            return Response({"error": "Credentials not available"}, status=status.HTTP_403_FORBIDDEN)
        except PartialCredentialsError:
            return Response({"error": "Incomplete credentials provided"}, status=status.HTTP_403_FORBIDDEN)
        except ClientError as e:
            return Response({"error": f"Client error: {e.response['Error']['Message']}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except BotoCoreError as e:
            return Response({"error": f"BotoCore error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PropertyList(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class PropertyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class PropertyPhotoList(generics.ListCreateAPIView):
    queryset = PropertyPhoto.objects.all()
    serializer_class = PropertyPhotoSerializer

class PropertyPhotoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyPhoto.objects.all()
    serializer_class = PropertyPhotoSerializer

class InquiryList(generics.ListCreateAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer

class InquiryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer

class PropertyStatusList(generics.ListCreateAPIView):
    queryset = PropertyStatus.objects.all()
    serializer_class = PropertyStatusSerializer

class PropertyStatusDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyStatus.objects.all()
    serializer_class = PropertyStatusSerializer

