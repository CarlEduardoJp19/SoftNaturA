from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect

class AutoLogoutMiddleware:
    """
    Middleware para cerrar sesión automáticamente por inactividad.
    Redirige a login sin alertas ni mensajes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Excluir rutas de static, media y admin
        if request.path.startswith(("/static/", "/media/", "/admin/")):
            return self.get_response(request)

        # Si el usuario no está autenticado o es staff → continuar normal
        if not request.user.is_authenticated or request.user.is_staff:
            return self.get_response(request)

        now = timezone.now()
        last_activity = request.session.get("last_activity")

        max_inactive = 60  # Tiempo máximo en segundos (ajustable)

        if last_activity:
            last_activity = timezone.datetime.fromisoformat(last_activity)
            diff = (now - last_activity).total_seconds()

            if diff > max_inactive:
                logout(request)  # Cierra sesión automáticamente
                return redirect("/usuarios/login/")  # Redirige a login

        # Actualizar timestamp de última actividad
        request.session["last_activity"] = now.isoformat()

        return self.get_response(request)
