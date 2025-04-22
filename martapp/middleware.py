from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

class RestrictUnauthenticatedMiddleware(MiddlewareMixin):
    def process_request(self, request):
        public_paths = ['/login/','/register/','/admin/']

        if not request.user.is_authenticated:
            if request.path.startswith('/cart') or request.path.startswith('/dashboard/'):
                messages.error(request, "login required to access this page.")
                return redirect('/login/')

class UserActivityLoggerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        user = request.user
        path = request.path
        method = request.method

        print(f"[LOG] {user} visited {path} using {method}")

class RecentProductTrackerMiddleware(MiddlewareMixin):
    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path

        if path.startswith('/product/'):
            recent_products = request.session.get('recent_products',[])

            if path in recent_products:
                recent_products.remove(path)

            recent_products.insert(0, path)

            request.session['recent_products'] = recent_products[:3]