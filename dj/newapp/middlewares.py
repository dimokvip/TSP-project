from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed

class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Список маршрутов, не требующих токена
        unauthenticated_endpoints = [
            '/api/login/',
            '/api/register/',
            '/api/refreshToken/',
        ]

        # Проверка, если маршрут в исключениях
        if any(request.path.startswith(endpoint) for endpoint in unauthenticated_endpoints):
            return None

        # Проверяем токен на защищённых маршрутах
        jwt_auth = JWTAuthentication()
        try:
            user, token = jwt_auth.authenticate(request)
            if user and token:
                request.user = user
                return None
        except AuthenticationFailed:
            return JsonResponse({'error': 'Недействительный токен'}, status=401)

        return JsonResponse({'error': 'Аутентификация требуется'}, status=401)
