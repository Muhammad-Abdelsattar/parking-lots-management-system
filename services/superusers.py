from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException,status,Request
from starlette.responses import RedirectResponse
from sqladmin.authentication import AuthenticationBackend
from models.superuser import SuperUser
from schemas.superuser import *
from core.jwt import create_access_token,decode_access_token
from core.security import verify_password,hash_password
from schemas.jwt import JWTSchema,EnumUserRole
from repositories.superusers import SuperusersRepository


class AdminsService(AuthenticationBackend):
    def __init__(self,
                 secret_key: str = "temp",
                 ) -> None:
        super().__init__(secret_key)
        self.repo : SuperusersRepository = SuperusersRepository()
        print(self.repo)


    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]

        superuser = await self.repo.get_superuser_by_name(name=str(username))

        if(superuser):
            superuser = SuperuserDB.from_orm(superuser)
            if(superuser.password == str(password)):

                token = create_access_token(role=EnumUserRole.admin,
                                            subject=superuser.id,
                                            )

                request.session.update({"token":token})

                return True

        return False


    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True


    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        try:
            token_data = decode_access_token(token=token)
            token_data = JWTSchema(**token_data)
            if(token_data.role is not EnumUserRole.admin or token_data.expiration_date < datetime.now()):
                return RedirectResponse(request.url_for("admin:login"), status_code=302)

        except:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
