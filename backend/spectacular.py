from drf_spectacular.views import SpectacularAPIView as BaseSpectacularAPIView


class SpectacularAPIView(BaseSpectacularAPIView):
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request,
            response,
            *args,
            **kwargs
        )
        response['Content-Disposition'] = 'attachment; filename="schema.yml"'
        return response