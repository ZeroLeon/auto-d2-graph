"""
Web Framework Example - Flask-based web application
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Request:
    """HTTP Request object"""
    method: str
    path: str
    headers: Dict[str, str]
    body: str = ""
    query_params: Dict[str, str] = None

    def __post_init__(self):
        if self.query_params is None:
            self.query_params = {}


@dataclass
class Response:
    """HTTP Response object"""
    status_code: int
    headers: Dict[str, str]
    body: str = ""
    content_type: str = "text/html"

    def json(self, data: Dict) -> 'Response':
        self.body = json.dumps(data)
        self.content_type = "application/json"
        self.headers["Content-Type"] = self.content_type
        return self


class Middleware(ABC):
    """Base middleware class"""

    def __init__(self, app):
        self.app = app

    @abstractmethod
    def process_request(self, request: Request) -> Optional[Request]:
        pass

    @abstractmethod
    def process_response(self, request: Request, response: Response) -> Response:
        pass


class CORS(Middleware):
    """CORS middleware"""

    def process_request(self, request: Request) -> Optional[Request]:
        return None

    def process_response(self, request: Request, response: Response) -> Response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE"
        return response


class Logging(Middleware):
    """Logging middleware"""

    def process_request(self, request: Request) -> Optional[Request]:
        print(f"[{datetime.now()}] {request.method} {request.path}")
        return None

    def process_response(self, request: Request, response: Response) -> Response:
        print(f"[{datetime.now()}] {response.status_code} {request.path}")
        return response


class Route:
    """Route handler"""

    def __init__(self, path: str, handler, methods: List[str]):
        self.path = path
        self.handler = handler
        self.methods = methods


class Router:
    """URL Router"""

    def __init__(self):
        self.routes: List[Route] = []

    def add_route(self, path: str, methods: List[str], handler):
        route = Route(path, handler, methods)
        self.routes.append(route)

    def find_route(self, request: Request) -> Optional[Route]:
        for route in self.routes:
            if request.path == route.path and request.method in route.methods:
                return route
        return None


class Application:
    """Main application class"""

    def __init__(self):
        self.router = Router()
        self.middleware_stack: List[Middleware] = []

    def add_middleware(self, middleware: Middleware):
        self.middleware_stack.append(middleware)

    def route(self, path: str, methods: List[str] = None):
        if methods is None:
            methods = ["GET"]

        def decorator(handler):
            self.router.add_route(path, methods, handler)
            return handler
        return decorator

    def handle_request(self, request: Request) -> Response:
        # Process request through middleware
        for middleware in self.middleware_stack:
            request = middleware.process_request(request) or request

        # Find and execute route
        route = self.router.find_route(request)
        if route:
            response = route.handler(request)
        else:
            response = Response(404, {})
            response.body = "Not Found"

        # Process response through middleware
        for middleware in reversed(self.middleware_stack):
            response = middleware.process_response(request, response)

        return response


# Example usage
app = Application()
cors = CORS(app)
logging = Logging(app)
app.add_middleware(cors)
app.add_middleware(logging)

@app.route("/api/users", ["GET", "POST"])
def handle_users(request: Request) -> Response:
    users = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ]
    response = Response(200, {})
    return response.json(users)

@app.route("/api/posts/<int:post_id>", ["GET"])
def handle_post(request: Request) -> Response:
    return Response(200, {}, "Post details")

if __name__ == "__main__":
    # Create test request
    test_request = Request("GET", "/api/users", {"Host": "localhost"})
    response = app.handle_request(test_request)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.body}")