"""Middleware d'identification de requete (X-Request-ID).

Associe un identifiant unique a chaque requete entrante (genere si absent),
le rend disponible dans `request.state.request_id` et le renvoie dans
l'en-tete de reponse `X-Request-ID` pour le tracing de bout en bout.
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_STATE = "request_id"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Injecte un X-Request-ID unique et coherent sur toute la requete."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response
