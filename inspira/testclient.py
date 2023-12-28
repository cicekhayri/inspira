from httpx import AsyncClient

from inspira.enums import HttpMethod


class TestClient:
    __test__ = False

    def __init__(self, app):
        self.app = app

    async def request(self, method, path, **kwargs):
        async with AsyncClient(app=self.app, base_url="http://testserver") as client:
            return await getattr(client, method.lower())(path, **kwargs)

    async def get(self, path, **kwargs):
        return await self.request(HttpMethod.GET.value, path, **kwargs)

    async def post(self, path, **kwargs):
        return await self.request(HttpMethod.POST.value, path, **kwargs)

    async def put(self, path, **kwargs):
        return await self.request(HttpMethod.PUT.value, path, **kwargs)

    async def delete(self, path, **kwargs):
        return await self.request(HttpMethod.DELETE.value, path, **kwargs)

    async def patch(self, path, **kwargs):
        return await self.request(HttpMethod.PATCH.value, path, **kwargs)

    async def options(self, path, **kwargs):
        return await self.request(HttpMethod.OPTIONS.value, path, **kwargs)
