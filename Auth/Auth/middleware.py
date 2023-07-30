from asgiref.sync import sync_to_async
from django.middleware.clickjacking import XFrameOptionsMiddleware

class CustomXFrameOptionsMiddleware(XFrameOptionsMiddleware):
    async def process_response(self, request, response):
        async_get = sync_to_async(response.get)
        x_frame_options = await async_get("X-Frame-Options")
        if x_frame_options is not None:
            return response
        return await super().process_response(request, response)

    async def __call__(self, request):
        response = await super().__call__(request)
        response.close = sync_to_async(response.close)
        return response
