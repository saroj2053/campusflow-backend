from django.contrib.auth.hashers import make_password
from user.models import UserProfile
from django.contrib.auth import login, get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import jwt  # Import PyJWT library
from datetime import datetime, timedelta
import json
import requests
from google.oauth2 import id_token
from google.auth.transport.requests import Request as GoogleAuthRequest
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.contrib.auth.hashers import check_password

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))

        # Extract data fields
        email = data.get('email', '').strip()
        full_name = data.get('full_name', '').strip()
        password = data.get('password', '').strip()
        confirmPassword = data.get('confirmPassword', '').strip()
        last_activity = data.get('last_activity','').strip()
        
        try:
            existing_profiles = UserProfile.objects.filter(email=email)
            if existing_profiles.exists():
                return JsonResponse({'message': 'User already exists, go to login page'}, status=409)  

            validate_email(email)
            validate_password(password)
            if password !=confirmPassword:
                return JsonResponse({"message": "Passwords don't match"}, status=400)
            hashed_password = make_password(password)

              # Save the data with the hashed password
            user_profile = UserProfile(email=email, full_name=full_name, password=hashed_password, university_name="", signup_using='FORM', role='USER', last_activity=last_activity)
            user_profile.save()
            # Generate JWT token upon successful registration
            payload = {
                'email': user_profile.email,
                'exp': datetime.utcnow() + timedelta(days=1)  # Token expiration time (adjust as needed)
            }
            # Serialize the UserProfile instance to JSON
            user_profile_data = {
                'email': user_profile.email,
                'full_name': user_profile.full_name,
                'signup_using': user_profile.signup_using,
                'role':user_profile.role,
                "university_name": "",
            }  
            jwt_token = jwt.encode(payload,settings.SECRET_KEY , algorithm='HS256')
            return JsonResponse({'message': 'User registered successfully', 'token': jwt_token, "user": user_profile_data})

        except ValidationError as e:
            return JsonResponse({'message': str(e)}, status=400)
        except jwt.InvalidTokenError as e:
            return JsonResponse({'message': 'Invalid token: ' + str(e)})
        except jwt.ExpiredSignatureError as e:
            return JsonResponse({'message': 'Token expired: ' + str(e)})
        except jwt.InvalidSignatureError as e:
            return JsonResponse({'message': 'Invalid signature: ' + str(e)})
        except jwt.InvalidIssuerError as e:
            return JsonResponse({'message': 'Invalid issuer: ' + str(e)})
        except Exception as ex:
            # Handle other exceptions if needed
            return JsonResponse({'message': 'Error generating token: ' + str(ex)})
 
    return JsonResponse({'message': 'Invalid request method'})

@csrf_exempt
def google_login(request):

    # Get the raw request body
    body = request.body.decode('utf-8')

    try:
        # Parse JSON data from the request body
        data = json.loads(body)
        access_token = data.get('access_token', '')
        last_activity = data.get('last_activity','')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data in the request body'}, status=400)

    # Step 1: Verify the Token
    try:
        # Assuming you have a Google Client ID
        CLIENT_ID = '939129256680-qe0149eq0b5g9oc14cj3lc78inbue6rq.apps.googleusercontent.com'
        id_token.verify_oauth2_token(access_token, GoogleAuthRequest(), CLIENT_ID)
    except ValueError as e:
        return JsonResponse({'error': f'Token verification failed: {str(e)}'}, status=400)

    # Step 2: Access data from access_token
    try:
        token_info_url = 'https://oauth2.googleapis.com/tokeninfo'
        token_info_response = requests.get(f'{token_info_url}?id_token={access_token}')
        token_info = token_info_response.json()
    except Exception as e:
        return JsonResponse({'error': f'Invalid token info from oauth2, {str(e)}'}, status=400)

    try:
        user_info = json.dumps(token_info)
        user_info_json = json.loads(user_info)
    except Exception as e:
        return JsonResponse({'error': f'Error in JSON format, {str(e)}'}, status=400)

    # Step 3: Create or Authenticate User
    # You may customize this part based on your Django User model and application logic
    email_id = user_info_json.get('email')
    first_name = user_info_json.get('given_name')
    last_name = user_info_json.get('family_name')

    if None in (email_id, first_name, last_name):
        return JsonResponse({'error': 'One or more required fields are missing.'}, status=400)

    try:
        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=email_id,
            defaults={'first_name': first_name, 'last_name': last_name, 'username': email_id,
                      'password': make_password('encryptedsamplepasswordforgooglesignin'),'last_activity':last_activity}
        )
        user.save()
    except Exception as e:
        return JsonResponse({'error': f'Error in handling User Model, {str(e)}'}, status=400)

    # Step 4: Authenticate User in Django
    user = authenticate(username=email_id, password='encryptedsamplepasswordforgooglesignin')

    if user is not None:
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        user_profile_data = {}

        # Step 5: Make a entry in common database as well for maintaining the data
        existing_user_profile = UserProfile.objects.filter(email=email_id).first()

        # Check if the user already exist or not. If not then create new account else collect data and send with the message
        if not existing_user_profile:

            # Perform additional actions after successful login
            user_profile_from_google = UserProfile(email=email_id, full_name=first_name + ' ' + last_name,
                                                   password=make_password('encryptedsamplepasswordforgooglesignin'),
                                                   university_name='', signup_using='GOOGLE', role="USER", last_activity = last_activity)
            user_profile_from_google.save()
            user_profile_data = {
                        'email': user_profile_from_google.email,
                        'full_name': user_profile_from_google.full_name,
                        'university_name': user_profile_from_google.university_name,
                        'signup_using': user_profile_from_google.signup_using,
                        'role':user_profile_from_google.role,
                        'last_activity':last_activity
                    } 
            response_data = {
                'message': 'User account created successfully'
            } 
        ## In future need to remove this access_token from here
        else:
            user_profile = UserProfile.objects.get(email=email_id)
            user_profile.last_activity = last_activity
            user_profile.save()
            user_profile_data = {
                        'email': user_profile.email,
                        'full_name': user_profile.full_name,
                        'university_name': user_profile.university_name,
                        'signup_using': user_profile.signup_using,
                        'role':user_profile.role,
                        'last_activity':last_activity
                    }
            response_data = {
                'message': 'User account already exist, logging you in...'
            }
        update_fields = {
            'token' : access_token,
            "data"  : user_profile_data
        }
        response_data.update(update_fields)
        return JsonResponse(response_data, status =200)
    else:
        return JsonResponse({'error': 'Authentication failed'}, status=401)

@login_required
@csrf_exempt
def google_logout(request):
    # You might revoke the Google access token here
    # Logout the user from the Django session
    request.session.flush()

    if not request.user.is_authenticated:
        return JsonResponse({'message': 'Google logout successful'})
    else:
        return JsonResponse({'message': 'Failed to logout'})

@csrf_exempt
def authenticate_user_login(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            # Extract email and password from the data
            email = data.get('email', '')
            password = data.get('password', '')
            last_activity = data.get('last_activity','')

            # Perform authentication
            user_profile = UserProfile.objects.get(email=email)
            if user_profile is not None:
                passwords_match = check_password(password, user_profile.password)
                if passwords_match:
                    user_profile.last_activity = last_activity
                    user_profile.save()
                    # Serialize the UserProfile instance to JSON
                    user_profile_data = {
                        'email': user_profile.email,
                        'full_name': user_profile.full_name,
                        'university_name': user_profile.university_name,
                        'signup_using': user_profile.signup_using,
                        'role':user_profile.role,
                        'last_activity':last_activity
                    }

                    payload = {
                        'email': user_profile.email,
                        'exp': datetime.utcnow() + timedelta(days=1)  # Token expiration time (adjust as needed)
                    }
                    jwt_token = jwt.encode(payload,settings.SECRET_KEY , algorithm='HS256')                    
                    response = {
                        "message":"Login Successful",
                        "user": user_profile_data,
                        "token": jwt_token
                    }
                    return JsonResponse(response, status=200)
                else:
                    return JsonResponse({'message': 'Email or password is incorrect'}, status = 401)
        except ObjectDoesNotExist:
            return JsonResponse({'message': "Email or password is incorrect"}, status = 401)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON data in the request body'}, status=400)
        except jwt.InvalidTokenError as e:
            return JsonResponse({'message': 'Invalid token: ' + str(e)})
        except jwt.ExpiredSignatureError as e:
            return JsonResponse({'message': 'Token expired: ' + str(e)})
        except jwt.InvalidSignatureError as e:
            return JsonResponse({'message': 'Invalid signature: ' + str(e)})
        except jwt.InvalidIssuerError as e:
            return JsonResponse({'message': 'Invalid issuer: ' + str(e)})
    return JsonResponse({'message':'Method not allowed'}, status = 405)

@csrf_exempt
def update_user_role(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            # Extract email from the data
            emailObj = json.loads(data.get('data', ''))
            email = emailObj.get('email', '')

            user_profile = UserProfile.objects.get(email=email)
            
            # Check if the user is already an admin
            if user_profile.role == "ADMIN":
                return JsonResponse({'message': f'{user_profile.full_name} is already an admin.'}, status=200)
            
            # Update the user role to "admin"
            user_profile.role = "ADMIN"
            # Save the changes to the database
            user_profile.save()

            return JsonResponse({'message': 'User update successful.', 'data' : data}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({'message': "Email is incorrect"}, status=401)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=400)
    
@csrf_exempt
@require_GET
def fetch_users(request):
    try:
        all_users = []
        # Convert the queryset to a list of dictionaries
        for user_profile in UserProfile.objects.all():
            user_data_list = {'email': user_profile.email,
                               'full_name': user_profile.full_name,
                               'university_name': user_profile.university_name,
                               'role': user_profile.role}
            all_users.append(user_data_list)
        # Return the data as JSON response
        return JsonResponse({'user_data': all_users}, safe=False)
    except Exception as e:
        response = {
            "message": f"An unexpected error occurred: {e}"
        }
        return JsonResponse(response, status =500)

@csrf_exempt
def update_user(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))
            # Extract email from the data
            email = data.get('email', '')
            full_name = data.get('full_name', '')
            university_name =  data.get('university_name', '')

            user_profile = UserProfile.objects.get(email=email)
            # Update the user role to "admin"
            user_profile.full_name = full_name
            user_profile.university_name = university_name

            # Save the changes to the database
            user_profile.save()
            return JsonResponse({'message': f'Update successful.'}, status=200)   
        except ObjectDoesNotExist:
            return JsonResponse({'message': "Email is incorrect"}, status=401)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=400)

@csrf_exempt
def delete_user(request):
    if request.method == 'DELETE':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))
            # Extract email from the data
            email = data.get('email', '')
            user_profile = UserProfile.objects.get(email=email)
            userFullName = user_profile.full_name
            # Delete the user
            user_profile.delete()
            return JsonResponse({'message': f'User deletion successful.'}, status=200)     
        except ObjectDoesNotExist:
            return JsonResponse({'message': "Email is incorrect"}, status=401)
    else:
        return JsonResponse({'message': 'Invalid request method.'}, status=400)

