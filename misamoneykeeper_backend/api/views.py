from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.hashers import make_password,check_password
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .serializers import UserDetailsSerializer, UserSerializer, UserViewSerializer, UserLoginSerializer, AccountSerializer, CategorySerializer, CategoryDetailsSerializer, PayAddSerializer, PayViewSerializer, BalanceAdjustmentSerializer, AccountUpdateSerializer,NotificationSerializer
from .models import User, Account, Category, CategoryDetails, Pay, UserDetails, notification
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum, Q

class UserRegisterAdmin(APIView):
    permission_classes = []
    def post(self, request):
        data=request.data

        email = data.get('email')

        if get_user_model().objects.filter(email=email).exists():
                return JsonResponse({
                    'error_message': 'Email này đã được đăng ký.',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            data['type'] = 2  
            data['is_superuser'] = True
            data['is_staff'] = True
        
            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                serializer.validated_data['password'] = make_password(serializer.validated_data['password'])

                user = serializer.save()

                data = {
                    'status': 1,
                    'payload': UserViewSerializer(user).data,
                    'message': "Bạn đã đăng kí tài khoản admin thành công"
                }
                return JsonResponse(data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({
                    'error_message': 'Dữ liệu không hợp lệ.',
                    'errors_code': 400,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

class UserRegisterView(APIView):
    permission_classes = []
    def post(self, request):
        data=request.data

        email = data.get('email')

        if get_user_model().objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 0,
                    'error_message': 'Email đã được được sử dụng',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # data['type'] = 1 
            # data['is_superuser'] = False
            # data['is_staff'] = False
            # data['groups'] = [] 
            # data['user_permissions'] = [] 
        
            serializer = UserSerializer(data=data)

            if serializer.is_valid():
                serializer.validated_data['password'] = make_password(serializer.validated_data['password'])

                user = serializer.save()

                data = {
                    'status': 1,
                    'payload': UserViewSerializer(user).data,
                    'message': "Bạn đã đăng kí thành công"
                }
                return JsonResponse(data, status=status.HTTP_201_CREATED)
            else:
                return JsonResponse({
                    'error_message': 'Dữ liệu không hợp lệ.',
                    'errors_code': 400,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
class UserLoginView(APIView):
    permission_classes = []
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            data=request.data
            email = data.get('email')

            if not get_user_model().objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 0,
                    'error_message': 'Email không tồn tại.',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                user = authenticate(
                    request,
                    username=serializer.validated_data['email'],
                    password=serializer.validated_data['password']
                )
                if user is not None:
                    login(request, user)
                    refresh = TokenObtainPairSerializer().get_token(user)
                    user.access_token = refresh.access_token
                    user.refresh_token = refresh
                    user.access_token_expiration = timezone.now() + timedelta(minutes=120)
                    user.refresh_token_expiration = timezone.now() + timedelta(days=10)
                    user.save()
                    data = {
                        'status': 1,
                        'payload': UserViewSerializer(user).data,
                        'message': "Bạn đã đăng nhập thành công"
                    }
                    return JsonResponse(data, status=status.HTTP_200_OK)
                return JsonResponse({
                    'status': 0,
                    'error_message': 'Email hoặc mật khẩu không đúng',
                    'error_code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({
            'error_messages': serializer.errors,
            'error_code': 400
        }, status=status.HTTP_400_BAD_REQUEST)
        
class UserLogoutView(APIView):
    def post(request):
        logout(request)
        data = {
            'status': 1,
            'message': "Bạn đã đăng xuất thành công"
        }
        return JsonResponse(data, status=status.HTTP_200_OK)
    
class RefreshAccessToken(APIView):
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            try:
                refresh_token_instance = RefreshToken(refresh_token)
                access_token = refresh_token_instance.access_token
            except Exception as e:
                return JsonResponse({'error': 'Invalid refresh token'}, status=400)
            
            user = get_user_model().objects.get(refresh_token=refresh_token_instance)
            user.access_token = access_token
            user.access_token_expiration = timezone.now() + timedelta(minutes=120)
            user.save()
            data = {
                'status': 1,
                'payload': UserSerializer(user).data,
                'message': "Cập nhập access token thành công"
            }
            return JsonResponse(data, status=status.HTTP_200_OK)
            
        return JsonResponse({'error': 'refresh token không hợp lệ'}, status=400)

class PayAddView(APIView):
    def post(self, request):

        data=request.data

        user_id = data.get('user_id')
        category_details_id = data.get('category_details_id')
        account_id = data.get('account_id')
        if not User.objects.filter(id=user_id).exists():
                return JsonResponse({
                    'error_message': 'Người dùng không tồn tại',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not CategoryDetails.objects.filter(category_details_id=category_details_id).exists(): 
                return JsonResponse({
                    'error_message': 'Hạng mục không tồn tại',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                if not Account.objects.filter(account_id=account_id).exists():
                    return JsonResponse({
                        'error_message': 'Ví không tồn tại',
                        'error_code': 400,
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializer = PayAddSerializer(data=request.data)
                    if serializer.is_valid():
                        account = Account.objects.get(account_id=account_id)
                        if account.ac_money < int(data.get('p_money')) and data.get('p_type') == "1":
                            return JsonResponse({
                                    'status': 0,     
                                    'error_message': 'Số dư không đủ để thực hiện',
                                    'error_code': 400,
                            }, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            pay = serializer.save()
                            if data.get('p_type') == "1":
                                money = account.ac_money - int(data.get('p_money'))
                                account.ac_money = money
                                account.save() 
                            else:
                                money = account.ac_money + int(data.get('p_money'))
                                account.ac_money = money
                                account.save()
                        data = {
                            'status': 1,
                            'payload': PayViewSerializer(pay).data,
                            'message': "Bạn đã thêm khoản thu/chi thành công!"
                        }
                        return JsonResponse(data, status=status.HTTP_200_OK)
                    return JsonResponse({
                        'error_messages': serializer.errors,
                        'error_code': 400
                    }, status=status.HTTP_400_BAD_REQUEST)

class PayUpdateView(APIView):
    def patch(self, request):

        data=request.data
        pay_id = data.get('pay_id')
        user_id = data.get('user_id')
        category_details_id = data.get('category_details_id')
        account_id = data.get('account_id')
        money_old = data.get('money_old')
        if not Pay.objects.filter(pay_id=pay_id, user_id=user_id, category_details_id=category_details_id, account_id=account_id).exists():
                return JsonResponse({
                    'error_message': 'Khoản chi/thu không tồn tại',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not User.objects.filter(id=user_id).exists():
                return JsonResponse({
                    'error_message': 'Người dùng không tồn tại',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                if not CategoryDetails.objects.filter(category_details_id=category_details_id).exists(): 
                    return JsonResponse({
                         'error_message': 'Hạng mục không tồn tại',
                        'error_code': 400,
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if not Account.objects.filter(account_id=account_id).exists():
                        return JsonResponse({
                            'error_message': 'Ví không tồn tại',
                            'error_code': 400,
                        }, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        pay = Pay.objects.get(pay_id=pay_id, user_id=user_id, category_details_id=category_details_id, account_id=account_id)
                        serializer = PayAddSerializer(data=request.data)
                        if serializer.is_valid():
                            account = Account.objects.get(account_id=account_id)
                            if account.ac_money < int(data.get('p_money')) and data.get('p_type') == "1":
                                return JsonResponse({
                                    'status': 0,     
                                    'error_message': 'Số dư không đủ để thực hiện',
                                    'error_code': 400,
                                }, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                pay.p_type = data.get('p_type')
                                pay.p_money = data.get('p_money')
                                pay.p_explanation = data.get('p_explanation')
                                pay.p_date = data.get('p_date')
                                pay.save()

                                if data.get('p_type') == 1:
                                    money = account.ac_money + int(money_old) - int(data.get('p_money'))
                                    account.ac_money = money
                                    account.save()
                                else:
                                    money = account.ac_money - int(money_old) + int(data.get('p_money'))
                                    account.ac_money = money
                                    account.save()
                            data = {
                                'status': 1,
                                'payload': PayViewSerializer(pay).data,
                                'message': "Bạn cập nhật khoản thu/chi thành công!"
                            }
                            return JsonResponse(data, status=status.HTTP_200_OK)
                        return JsonResponse({
                            'error_messages': serializer.errors,
                            'error_code': 400
                        }, status=status.HTTP_400_BAD_REQUEST)
                
class BalanceAdjustmentView(APIView):
    def patch(self, request):
        data = request.data
        account_id = data.get('account_id')
        user_id = data.get('user_id')
        ac_money = data.get('ac_money')
        if not Account.objects.filter(account_id=account_id).exists():
            return JsonResponse({
                'error_message': 'Ví không tồn tại',
                    'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not User.objects.filter(id=user_id).exists():
                return JsonResponse({
                    'status': 0,
                    'error_message': 'Người dùng không tồn tại',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                account = Account.objects.get(account_id=account_id)
                serializer = BalanceAdjustmentSerializer(data=request.data)
                if serializer.is_valid():
                    account.ac_money = ac_money
                    account.save()
                    data = {
                        'status': 1,
                        'payload': AccountSerializer(account).data,
                        'message': "Bạn đã thay đổi số dư thành công"
                    }
                    return JsonResponse(data, status=status.HTTP_200_OK)
                return JsonResponse({
                    'error_messages': serializer.errors,
                    'error_code': 400
                }, status=status.HTTP_400_BAD_REQUEST)

class PayDeleteView(APIView):
    def delete(self, request):
        data = request.data
        pay_id = data.get('pay_id')
        user_id = data.get('user_id')
        category_details_id = data.get('category_details_id')
        account_id = data.get('account_id')
        if not Pay.objects.filter(pay_id=pay_id, user_id=user_id, category_details_id=category_details_id, account_id=account_id).exists():
                return JsonResponse({
                    'error_message': 'Khoản chi/thu không tồn tại',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            pay = Pay.objects.get(pay_id=pay_id, user_id=user_id, category_details_id=category_details_id, account_id=account_id)
            pay.delete()
            data = {
                'status': 1,
                'message': "Bạn đã xóa tài khoản thu/chi thành công"
            }
            return JsonResponse(data, status=status.HTTP_200_OK)

   
class CategoryView(APIView):
    def post(self, request):
        data = request.data
        cad_type = data.get('cad_type')
        category = Category.objects.order_by('category_id') # Sắp xếp giảm dần có dấu trừ đằng trc ('-account_id')
        if not CategoryDetails.objects.filter(cad_type=cad_type).exists():
            return JsonResponse({
                'error_message': 'Loại hạng mục không tồn tại',
                    'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            category = Category.objects.filter(ca_type=cad_type).order_by('category_id')
            categoryDetails = CategoryDetails.objects.filter(cad_type=cad_type).order_by('category_details_id')
            categorySerializer = CategorySerializer(category, many=True).data # many=True, Serializer sẽ xử lý một danh sách (list)
            categoryDetailsSerializer = CategoryDetailsSerializer(categoryDetails, many=True).data # .data để danh sách dữ liệu sau khi serializer đã xử lý xong
            for a in categorySerializer:
                a['category_details'] = [b for b in categoryDetailsSerializer if b['category_id'] == a['category_id']]
            data = {
                'status': 1,
                'payload': list(categorySerializer),
                'message': "Bạn đã lấy ra dữ liệu hạng mục thành công"
            }
            return JsonResponse(data)

class CategoryCollectView(APIView):
    def post(self, request):
        data = request.data
        cad_type = data.get('cad_type')
        if not CategoryDetails.objects.filter(cad_type=cad_type).exists():
            return JsonResponse({
                'error_message': 'Loại hạng mục không tồn tại',
                    'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            categoryDetails = CategoryDetails.objects.filter(cad_type=cad_type).order_by('category_details_id')
            categoryDetailsSerializer = CategoryDetailsSerializer(categoryDetails, many=True).data 
            data = {
                'status': 1,
                'payload': list(categoryDetailsSerializer),
                'message': "Bạn đã lấy ra dữ liệu loại hạng mục thu thành công"
            }
            return JsonResponse(data)

class HistoryHomeView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({
                'error_message': 'Người dùng không tồn tại',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            category = Pay.objects.filter(user_id=user_id
            ).prefetch_related( # Liên kết 3 bảng, sử dụng __ để định quan hệ
                'category_details_id__category_id'
            ).values(
                'category_details_id__category_id',
                'category_details_id__category_id__ca_name',
                'category_details_id__category_id__ca_image'
            ).annotate(
                sum_money=Sum('p_money')
            )
            data = []
            for p in category:
                data.append({
                    'category_id': p['category_details_id__category_id'],
                    'ca_name': p['category_details_id__category_id__ca_name'],
                    'ca_image': "/api/media/" + p['category_details_id__category_id__ca_image'],
                    'sum_money': p['sum_money']
            })
            pay = Pay.objects.filter(user_id=user_id).values('user_id').annotate(
                sum_money_pay=Sum('p_money', filter=Q(p_type=1)),
                sum_money_collect=Sum('p_money', filter=Q(p_type=2))
            )
            data1 = []
            for p in pay:
                data1.append({
                    'p_money_pay': p['sum_money_pay'] if p['sum_money_pay'] is not None else 0, 
                    'p_money_collect': p['sum_money_collect'] if p['sum_money_collect'] is not None else 0
                })
            data2 = []
            data2.append({
                'sum': data1,
                'category': data
            })
            data3 = {
                'status': 1,
                'payload': list(data2),
                'message': "Bạn đã lấy ra dữ liệu lịch sử ghi chép thành công"
            }
            return JsonResponse(data3)
            
class HistoryView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        p_type = data.get('p_type')
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({
                'error_message': 'Người dùng không tồn tại',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not Pay.objects.filter(user_id=user_id).exists():
                return JsonResponse({
                    'error_message': 'Không có dữ liệu thu/chi nào',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                category = Pay.objects.filter(user_id=user_id, p_type=p_type
                ).prefetch_related( 
                    'category_details_id__category_id'
                ).values(
                    'category_details_id__category_id',
                    'category_details_id__category_id__ca_name',
                    'category_details_id__category_id__ca_image'
                ).annotate(
                    sum_money=Sum('p_money')
                )
                data1 = []
                for p in category:
                    data1.append({
                        'category_id': p['category_details_id__category_id'],
                        'ca_name': p['category_details_id__category_id__ca_name'],
                        'ca_image': "/api/media/" + p['category_details_id__category_id__ca_image'],
                        'sum_money': p['sum_money']
                    })
                # Thứ 2
                categoryDetails = Pay.objects.filter(user_id=user_id, p_type=p_type
                ).prefetch_related(
                    'category_details_id'
                ).values(
                    'category_details_id',
                    'category_details_id__category_id',
                    'category_details_id__cad_name',
                    'category_details_id__cad_image'
                 ).annotate(
                    sum_money=Sum('p_money')
                )
                data2 = []
                for p in categoryDetails:
                    data2.append({
                        'category_details_id': p['category_details_id'],
                        'category_id': p['category_details_id__category_id'],
                        'cad_name': p['category_details_id__cad_name'],
                        'cad_image': "/api/media/" + p['category_details_id__cad_image'],
                        'sum_money': p['sum_money']
                    })
                pay = Pay.objects.filter(user_id=user_id).prefetch_related(
                    'category_details_id', 'account_id'
                ).order_by('-p_date')

                data3 = []
                for c in pay:
                    data3.append({
                        'pay_id': c.pay_id,
                        'category_details_id': c.category_details_id.category_details_id,
                        'category_name': c.category_details_id.cad_name,
                        'cad_image': c.category_details_id.cad_image.url, 
                        'p_type': c.p_type,
                        'p_date': c.p_date, 
                        'p_money': c.p_money,
                        'p_explanation': c.p_explanation,
                        'account_id': c.account_id.account_id,
                        'ac_name': c.account_id.ac_name,
                        'ac_type': c.account_id.ac_type
                    })
                for a in data2:
                    a['pay'] = [b for b in data3 if b['category_details_id'] == a['category_details_id']]
                for a in data1:
                    a['category_details'] = [b for b in data2 if b['category_id'] == a['category_id']]
                
                data4 = {
                    'status': 1,
                    'payload': list(data1),
                    'message': "Bạn đã lấy ra dữ liệu lịch sử ghi chép thành công"
                }
                return JsonResponse(data4)

class RecentNotesHomeView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        if not Pay.objects.filter(user_id=user_id).exists():
            return JsonResponse({
                'status': 0,
                'error_message': 'Không có dữ liệu thu/chi nào',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            category = Pay.objects.filter(user_id=user_id).prefetch_related(
                'category_details_id', 'account_id'
            ).order_by('-p_date')[:3]

            data = []
            for c in category:
                data.append({
                    'pay_id': c.pay_id,
                    'category_details_id': c.category_details_id.category_details_id,
                    'category_name': c.category_details_id.cad_name,
                    'cad_image': c.category_details_id.cad_image.url, 
                    'p_type': c.p_type,
                    'p_date': c.p_date, 
                    'p_money': c.p_money,
                    'p_explanation': c.p_explanation,
                    'account_id': c.account_id.account_id,
                    'ac_name': c.account_id.ac_name,
                    'ac_type': c.account_id.ac_type
                })
            data1 = {
                'status': 1,
                'payload': list(data),
                'message': "Bạn đã lấy ra dữ liệu ghi chép gần đây thành công"
            }
            return JsonResponse(data1)

class RecentNotesView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        month = data.get('month')
        year = data.get('year')
        if not Pay.objects.filter(user_id=user_id).exists():
            return JsonResponse({
                'status': 0,
                'error_message': 'Không có dữ liệu thu/chi nào',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            
            pay = Pay.objects.filter(user_id=user_id, p_date__month=month, p_date__year=year).values('p_date'
            ).annotate(
                sum_money_pay=Sum('p_money', filter=Q(p_type=1)),
                sum_money_collect=Sum('p_money', filter=Q(p_type=2))
            ).order_by('-p_date')
            data1 = []
            for p in pay:
                data1.append({
                    
                    'p_date': p['p_date'],
                    'p_money_type': 1 if p['sum_money_pay'] is not None else 2,
                    'p_money_pay': p['sum_money_pay'] if p['sum_money_pay'] is not None else 0, 
                    'p_money_collect': p['sum_money_collect'] if p['sum_money_collect'] is not None else 0, 
                })
            category = Pay.objects.filter(user_id=user_id).prefetch_related(
                'category_details_id', 'account_id'
            )

            data2 = []
            for c in category:
                data2.append({
                    'pay_id': c.pay_id,
                    'category_details_id': c.category_details_id.category_details_id,
                    'category_name': c.category_details_id.cad_name,
                    'cad_image': c.category_details_id.cad_image.url, 
                    'p_type': c.p_type,
                    'p_date': c.p_date, 
                    'p_money': c.p_money,
                    'p_explanation': c.p_explanation,
                    'account_id': c.account_id.account_id,
                    'ac_name': c.account_id.ac_name,
                    'ac_type': c.account_id.ac_type
                })

            for a in data1:
                a['category'] = [b for b in data2 if b['p_date'] == a['p_date']]
            data3 = {
                'status': 1,
                'payload': list(data1),
                'message': "Bạn đã lấy ra dữ liệu ghi chép gần đây thành công"
            }
            return JsonResponse(data3)

class AccountView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({
                'error_message': 'Người dùng không tồn tại',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            accounts = Account.objects.filter(user_id=user_id)
            if not accounts.exists():
                return JsonResponse({
                    'status': 0,
                    'error_message': 'Chưa có ví nào',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = AccountSerializer(accounts, many=True)
                data = {
                    'status': 1,
                    'payload': serializer.data,
                    'message': "Bạn đã lấy thông tin tài khoản thành công"
                }
                return JsonResponse(data)
        
class AccountAddView(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({
                'error_message': 'Người dùng không tồn tại',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = AccountSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                data = {
                    'status': 1,
                    'payload': serializer.data,
                    'message': "Chúc mừng bạn đã đăng kí tài khoản (ví) thành công"
                }
                return JsonResponse(data, status=status.HTTP_201_CREATED)
            return JsonResponse({
                'error_messages': serializer.errors,
                'error_code': 400
            }, status=status.HTTP_400_BAD_REQUEST)

class AccountUpdateView(APIView):
    def patch(self, request):
        data = request.data
        account_id = data.get('account_id')
        user_id = data.get('user_id')
        if not Account.objects.filter(account_id=account_id, user_id=user_id).exists():
            return JsonResponse({
                'error_message': 'Ví không tồn tại',
                    'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not User.objects.filter(id=user_id).exists():
                return JsonResponse({
                    'error_message': 'Người dùng không tồn tại',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                account = Account.objects.get(account_id=account_id, user_id=user_id)
                serializer = AccountUpdateSerializer(data=request.data)
                if serializer.is_valid():
                    account.ac_name = data.get('ac_name')
                    account.ac_money = data.get('ac_money')
                    account.ac_type = data.get('ac_type')
                    account.ac_explanation = data.get('ac_explanation')
                    account.save()
                    data = {
                        'status': 1,
                        'payload': AccountSerializer(account).data,
                        'message': "Bạn đã cập nhật thông tin tài khoản (ví) thành công"
                    }
                    return JsonResponse(data, status=status.HTTP_200_OK)
                return JsonResponse({
                    'error_messages': serializer.errors,
                    'error_code': 400
                }, status=status.HTTP_400_BAD_REQUEST)
    
class AccountDeleteView(APIView):
    def delete(self, request):
        data = request.data
        account_id = data.get('account_id')
        user_id = data.get('user_id')
        if not Account.objects.filter(account_id=account_id, user_id=user_id).exists():
            return JsonResponse({
                'error_message': 'Ví không tồn tại',
                    'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not User.objects.filter(id=user_id).exists():
                return JsonResponse({
                    'error_message': 'Người dùng không tồn tại',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                account = Account.objects.get(account_id=account_id, user_id=user_id)
                account.delete()
                data = {
                    'status': 1,
                    'message': "Bạn đã xóa tài khoản (ví) thành công"
                }
                return JsonResponse(data, status=status.HTTP_200_OK)

class SpendingView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        year = data.get('year')
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({
                'error_message': 'Người dùng không tồn tại',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not Pay.objects.filter(user_id=user_id).exists():
                return JsonResponse({
                    'error_message': 'Không có dữ liệu chi nào',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                data2=[]
                for month_number in range(1, 13):
                    sum_pay = Pay.objects.filter(user_id=user_id, p_date__month=month_number, p_date__year=year).values('p_date__year').aggregate(
                        sum_money_collect=Sum('p_money', filter=Q(p_type=1))

                    )

                    month_data = {
                        'p_month': month_number,
                        'p_total_money': sum_pay['sum_money_collect'] if sum_pay and sum_pay['sum_money_collect'] is not None else 0

                    }
                    
                    data2.append({
                        'p_month': month_data['p_month'],
                        'p_sum': month_data['p_total_money'],
                        })
                
                    data = {
                        'status': 1,
                        'payload': data2,
                        'message': "Bạn đã lấy thông tin chi thành công"
                    }
                return JsonResponse(data, status= status.HTTP_200_OK, safe=False)
            
class CollectedView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        year = data.get('year')
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({
                'error_message': 'Người dùng không tồn tại',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not Pay.objects.filter(user_id=user_id).exists():
                return JsonResponse({
                    'error_message': 'Không có dữ liệu thu nào',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:              
                data2=[]
                for month_number in range(1, 13):
                    sum_pay = Pay.objects.filter(user_id=user_id, p_date__month=month_number, p_date__year=year).values('p_date__year').aggregate(
                        sum_money_collect=Sum('p_money', filter=Q(p_type=2))
                    )
                    month_data = {
                        'p_month': month_number,
                        'p_total_money': sum_pay['sum_money_collect'] if sum_pay and sum_pay['sum_money_collect'] is not None else 0
                    }
                    data2.append({
                        'p_month': month_data['p_month'],
                        'p_sum': month_data['p_total_money'],
                        })
                data = {
                        'status': 1,
                        'payload': data2,
                        'message': "Bạn đã lấy thông tin thu thành công"
                    }
                return JsonResponse(data, status= status.HTTP_200_OK, safe=False)
   
class SpendingCollectedView(APIView):
    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        year = data.get('year')
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({
                'error_message': 'Người dùng không tồn tại',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not Pay.objects.filter(user_id=user_id).exists():
                return JsonResponse({
                    'error_message': 'Không có dữ liệu chi nào',
                    'error_code': 400,
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                data2=[]
                for month_number in range(1, 13):
                    sum_revenue = Pay.objects.filter(user_id=user_id, p_date__month=month_number, p_date__year=year).values('p_date__year').aggregate(
                        sum_money_collect=Sum('p_money', filter=Q(p_type=1))
                    )

                    sum_expense = Pay.objects.filter(user_id=user_id, p_date__month=month_number, p_date__year=year).values('p_date__year').aggregate(
                        sum_money_collect=Sum('p_money', filter=Q(p_type=2))
                    )

                    month_data = {
                        'p_month': month_number,
                        'p_total_revenue': sum_revenue['sum_money_collect'] if sum_revenue and sum_revenue['sum_money_collect'] is not None else 0,
                        'p_total_expense': sum_expense['sum_money_collect'] if sum_expense and sum_expense['sum_money_collect'] is not None else 0,
                    }

                    data2.append({
                        'p_month': month_data['p_month'],
                        'p_total_revenue': month_data['p_total_revenue'],
                        'p_total_expense': month_data['p_total_expense'],
                    })

                data = {
                    'status': 1,
                    'payload': data2,
                    'message': "Bạn đã lấy thông tin thu chi thành công"
                }
                return JsonResponse(data, status= status.HTTP_200_OK, safe=False)
   
            
class ShowNotification(APIView):
    def post(self, request):
        user_id = request.data.get('user_id')
        if not User.objects.filter(id=user_id).exists():
            return JsonResponse({
                'error_message': 'Người dùng không tồn tại',
                'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            
            notifications = notification.objects.filter(user_id=user_id)
            serializer = NotificationSerializer(notifications, many=True)
            data = {
                'status': 1,
                'payload': serializer.data,
                'message': 'Dữ liệu thông báo đã được lấy thành công.'
            }
            return JsonResponse(data)

        
class UserUpdateView(APIView):
    def patch(self, request):
        data = request.data
        user_id = data.get('user_id')
        password = data.get('password')
        new_password = data.get('new_password')
        if not get_user_model().objects.filter(id=user_id).exists():
            return JsonResponse({
                'error_message': 'Người dùng không tồn tại',
                'error_code': 400,
        }, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = get_user_model().objects.get(id=user_id)
            if not check_password(password, user.password): 
                return JsonResponse({
                    'error_message': 'Mật khẩu không chính xác',
                    'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
            else:
                if password == new_password:
                    return JsonResponse({
                        'error_message': 'Mật khẩu mới không thể trung lặp với mật khẩu cũ',
                        'error_code': 400,
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    serializer = UserViewSerializer(data=request.data)
                    if serializer.is_valid():
                        user.password = make_password(data.get('new_password'))
                        user.save()
                        data = {
                            'status': 1,
                            'payload': UserViewSerializer(user).data,
                            'message': "Bạn đã thay đổi mật khẩu thành công"
                        }
                    return JsonResponse(data, status=status.HTTP_200_OK)

class CategoryUpdateView(APIView):
    permission_classes = []  
    def patch(self, request):
        data = request.data
        category_id = data.get('category_id')
        
        if not Category.objects.filter(category_id=category_id).exists():
            return JsonResponse({
                'error_message': 'hạng muc không tồn tại',
                    'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        else:
                category = Category.objects.get(category_id=category_id)
                serializer = CategorySerializer(data=request.data)
                if serializer.is_valid():
                    category.ca_name=data.get('ca_name')
                    category.ca_image=data.get('ca_image')
                    category.ca_explanation=data.get('ca_explanation')
                    category.save()
                    data = {
                        'status': 1,
                        'payload': AccountSerializer(category).data,
                        'message': "Bạn đã cập nhật hạng mục thành công"
                    }
                    return JsonResponse(data, status=status.HTTP_200_OK)
                return JsonResponse({
                    'error_messages': serializer.errors,
                    'error_code': 400
                }, status=status.HTTP_400_BAD_REQUEST)

class CategoryDeleteView(APIView):
    permission_classes = []
    def delete(self, request):
        data = request.data
       
        category_id=data.get('category_id')
        if not Category.objects.filter(category_id=category_id).exists():
            return JsonResponse({
                'error_message': 'hạng mục  không tồn tại',
                    'error_code': 400,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        else:
               category = Category.objects.get(category_id=category_id)
               category.delete()
               data = {
                    'status': 1,
                    'message': "Bạn đã xóa hạng mục thành công"
                }
               return JsonResponse(data, status=status.HTTP_200_OK)

# API View thông tin user 
class UserProfileView(APIView): 
    def post(self, request): 
        data = request.data 
        user_id = data.get('user_id') 
        if not get_user_model().objects.filter(id=user_id).exists(): 
            return JsonResponse({ 
                'error_message': 'Người dùng không tồn tại', 
                'error_code': 400, 
        }, status=status.HTTP_400_BAD_REQUEST) 
        else: 
            if not UserDetails.objects.filter(user_id=user_id).exists(): 
                user = get_user_model().objects.filter(id=user_id) 
                data = [] 
                for c in user: 
                    data.append({ 
                        'user_id': c.id, 
                        'user_details_id': 0, 
                        'email': c.email, 
                        'mobile': c.mobile, 
                        'first_name': c.first_name, 
                        'last_name': c.last_name, 
                        'u_image': '', 
                        'u_gender': 1, 
                        'u_birthday': '1990-01-01', 
                        'u_address': '', 
                        'u_job': '' 
                    }) 
                data1 = { 
                   'status': 1, 
                    'payload': list(data), 
                    'message': "Hiển thị thông tin người dùng" 
                } 
                return JsonResponse(data1, status=status.HTTP_200_OK) 
            else: 
                user = UserDetails.objects.filter(user_id=user_id).prefetch_related('user_id') 
                data = [] 
                for c in user: 
                    u_image_url = c.u_image.url if c.u_image else '' 
                    data.append({ 
                        'user_id': c.user_id.id, 
                        'user_details_id': c.user_details_id, 
                        'email': c.user_id.email, 
                        'mobile': c.user_id.mobile, 
                        'first_name': c.user_id.first_name, 
                        'last_name': c.user_id.last_name, 
                        'u_image': u_image_url, 
                        'u_gender': c.u_gender, 
                        'u_birthday': c.u_birthday, 
                        'u_address': c.u_address, 
                        'u_job': c.u_job 
                    }) 
                    data1 = { 
                        'status': 1, 
                        'payload': list(data), 
                        'message': "Bạn đã thông tin người dùng thành công" 
                    } 
                    return JsonResponse(data1, status=status.HTTP_200_OK) 
                 
    # API Update thông tin User 
class UserUpdateProfileView(APIView): 
    def post(self, request): 
        user_id = request.data.get('user_id') 
        if not get_user_model().objects.filter(id=user_id).exists(): 
            return JsonResponse({ 
                'error_message': 'Người dùng không tồn tại', 
                'error_code': 400, 
        }, status=status.HTTP_400_BAD_REQUEST) 
        else: 
            if not UserDetails.objects.filter(user_id=user_id).exists(): # Nếu không tìm thấy thuộc tính phụ 
                 
                # Lưu thông tin vào bảng User  
                user = get_user_model().objects.get(id=user_id) 
                serializer = UserViewSerializer(instance=user, data={'mobile': request.data.get('mobile'), 'first_name': request.data.get('first_name'), 'last_name': request.data.get('last_name')}) 
                if serializer.is_valid(): 
                    user.mobile = request.data.get('mobile') 
                    user.first_name = request.data.get('first_name') 
                    user.last_name = request.data.get('last_name') 
                    user.save() 
 
                    # Lưu thông tin vào bảng User Details 
                    serializerDetails = UserDetailsSerializer(data={'user_id': request.data.get('user_id'), 'u_gender': request.data.get('u_gender'), 'u_birthday': request.data.get('u_birthday'), 'u_address': request.data.get('u_address'), 'u_job': request.data.get('u_job')}) 
                    if serializerDetails.is_valid(): 
                        serializerDetails.save() 
                        data1 = { 
                            'status': 1, 
                            'payload': UserViewSerializer(user).data,
                            'message': "Chúc mừng tạo thông tin cho user thành công" 
                        } 
                        return JsonResponse(data1, status=status.HTTP_201_CREATED) 
                return JsonResponse({ 
                    'error_messages': "Có lỗi gì đó đã sảy ra với bảng user", 
                    'error_code': 400 
                }, status=status.HTTP_400_BAD_REQUEST) 
            else: 
                    # Lưu thông tin vào bảng User  
                    user = get_user_model().objects.get(id=user_id) 
                    serializer = UserViewSerializer(instance=user, data={'mobile': request.data.get('mobile'), 'first_name': request.data.get('first_name'), 'last_name': request.data.get('last_name')}) 
                    if serializer.is_valid(): 
                        user.mobile = request.data.get('mobile') 
                        user.first_name = request.data.get('first_name') 
                        user.last_name = request.data.get('last_name') 
                        user.save() 
 
                    # Lưu thông tin vào bảng User Details 
                    userDetails = UserDetails.objects.get(user_details_id=request.data.get('user_details_id')) 
                    serializerDetails = UserDetailsSerializer(instance=userDetails, data={'u_gender': request.data.get('u_gender'), 'u_birthday': request.data.get('u_birthday'), 'u_address': request.data.get('u_address'), 'u_job': request.data.get('u_job')}) 
                    if serializerDetails.is_valid(): 
                        userDetails.u_gender = request.data.get('u_gender') 
                        userDetails.u_birthday = request.data.get('u_birthday') 
                        userDetails.u_address = request.data.get('u_address') 
                        userDetails.u_job = request.data.get('u_job') 
                        userDetails.save() 
                    data1 = { 
                        'status': 1, 
                        'payload': UserViewSerializer(user).data,
                        'message': "Bạn đã cập nhật thông tin người dùng thành công" 
                    } 
                    return JsonResponse(data1, status=status.HTTP_200_OK)
            




# class UserProfileView(APIView):
#     def post(self, request):
#         data = request.data
#         user_id = data.get('user_id')
#         if not get_user_model().objects.filter(id=user_id).exists():
#             return JsonResponse({
#                 'error_message': 'Người dùng không tồn tại',
#                 'error_code': 400,
#         }, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             if not UserDetails.objects.filter(user_id=user_id).exists():
#                 user = get_user_model().objects.filter(id=user_id)
#                 data = []
#                 for c in user:
#                     data.append({
#                         'user_id': c.id,
#                         'user_details_id': '',
#                         'email': c.email,
#                         'mobile': '',
#                         'u_name': '',
#                         'u_image': '',
#                         'u_gender': '1',
#                         'u_birthday': '1990-01-01',
#                         'u_address': '',
#                         'u_job': ''
#                     })
#                 data1 = {
#                    'status': 1,
#                     'payload': list(data),
#                     'message': "Bạn đã thông tin người dùng thành công"
#                 }
#                 return JsonResponse(data1, status=status.HTTP_200_OK)
#             else:
#                 user = UserDetails.objects.filter(user_id=user_id).prefetch_related('user_id')
#                 data = []
#                 for c in user:
#                     u_image_url = c.u_image.url if c.u_image else ''
#                     data.append({
#                         'user_id': c.user_id.id,
#                         'user_details_id': c.user_details_id,
#                         'email': c.user_id.email,
#                         'mobile': c.user_id.mobile,
#                         'u_name': c.u_name,
#                         'u_image': u_image_url,
#                         'u_gender': c.u_gender,
#                         'u_birthday': c.u_birthday,
#                         'u_address': c.u_address,
#                         'u_job': c.u_job
#                     })
#                     data1 = {
#                         'status': 1,
#                         'payload': list(data),
#                         'message': "Bạn đã thông tin người dùng thành công"
#                     }
#                     return JsonResponse(data1, status=status.HTTP_200_OK)
                
# class UserUpdateProfileView(APIView):
#     def post(self, request):
#         data = request.data
#         user_id = data.get('user_id')
#         if not get_user_model().objects.filter(id=user_id).exists():
#             return JsonResponse({
#                 'error_message': 'Người dùng không tồn tại',
#                 'error_code': 400,
#         }, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             if not UserDetails.objects.filter(user_id=user_id).exists(): 
                
#                 serializerDetails = UserDetailsSerializer(data=request.data)
#                 if serializerDetails.is_valid():
#                     serializerDetails.save()
#                     data1 = {
#                         'status': 1,
#                         'payload': serializerDetails.data,
#                         'message': "Chúc mừng tạo thông tin cho user thành công"
#                     }
#                     return JsonResponse(data1, status=status.HTTP_201_CREATED)
#                 return JsonResponse({
#                     'error_messages': "Có lỗi gì đó đã sảy ra với bảng user",
#                     'error_code': 400
#                 }, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                     userDetails = UserDetails.objects.get(user_details_id=data.get('user_details_id'))
#                     serializerDetails = UserDetailsSerializer(instance=userDetails, data={'u_name': data.get('u_name'), 'u_gender': data.get('u_gender'), 'u_birthday': data.get('u_birthday'), 'u_address': data.get('u_address'), 'u_job': data.get('u_job')})
#                     if serializerDetails.is_valid():
#                         userDetails.u_name = data.get('u_name')
#                         userDetails.u_gender = data.get('u_gender')
#                         userDetails.u_birthday = data.get('u_birthday')
#                         userDetails.u_address = data.get('u_address')
#                         userDetails.u_job = data.get('u_job')
#                         userDetails.save()
#                     data1 = {
#                         'status': 1,
#                         'message': "Bạn đã cập nhật thông tin người dùng thành công"
#                     }
#                     return JsonResponse(data1, status=status.HTTP_200_OK)

