import os
import pytest
import tornado.ioloop
import tornado.web
from tornado.httpclient import HTTPClientError
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application

# Define the HTML template file
TEMPLATE_PATH = "template.html"

# Create Tornado request handler with violations
class OkHandler(tornado.web.RequestHandler):
    def get(self):
        # Set headers and status before calling render
        self.set_header("X-Initial-Header", "Set Before Render")
        self.add_header("X-Additional-Header", "Still Ok")
        self.clear_header("X-Initial-Header")
        self.set_status(200)  # Normal status before render

        # self.write("This will cause an error.")

        # Render the HTML template and implicitly finish the response
        self.render("template.html", message="Hello from Tornado!")

class ViolationHandler_1(tornado.web.RequestHandler):
    def get(self):
        # Set headers and status before calling render
        self.set_header("X-Initial-Header", "Set Before Render")
        self.set_status(200)  # Normal status before render

        # Render the HTML template and implicitly finish the response
        self.render("template.html", message="Hello from Tornado!")

        # Violations
        try:
            self.set_header("X-Extra-Header", "Not Allowed")
        except RuntimeError as e:
            print(f"Error: {e}")


class ViolationHandler_2(tornado.web.RequestHandler):
    def get(self):
        # Set headers and status before calling render
        self.set_header("X-Initial-Header", "Set Before Render")
        self.set_status(200)  # Normal status before render

        # Render the HTML template and implicitly finish the response
        self.render("template.html", message="Hello from Tornado!")

        # Violations
        try:
            self.write("This will cause an error.")
        except RuntimeError as e:
            print(f"Error: {e}")

        try:
            self.set_header("X-Extra-Header", "Not Allowed")
        except RuntimeError as e:
            print(f"Error: {e}")

        try:
            self.add_header("X-Additional-Header", "Not Allowed")
        except RuntimeError as e:
            print(f"Error: {e}")

        try:
            self.clear_header("X-Initial-Header")
        except RuntimeError as e:
            print(f"Error: {e}")

        try:
            self.set_status(404)
        except RuntimeError as e:
            print(f"Error: {e}")

# Create the Tornado application
def make_app():
    return Application(
        [
            (r"/ok", OkHandler),
            (r"/violation_1", ViolationHandler_1),
            (r"/violation_2", ViolationHandler_2)
        ],
        template_path="."
    )

@pytest.fixture(scope="module", autouse=True)
def setup_template():
    # Write the HTML template file before tests
    with open(TEMPLATE_PATH, "w") as f:
        f.write("<html><body><h1>{{ message }}</h1></body></html>")
    yield
    # Cleanup the HTML template file after tests
    if os.path.exists(TEMPLATE_PATH):
        os.remove(TEMPLATE_PATH)

# Create the test case
class TestTornadoServer(AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

    @gen_test
    async def test_ok_1(self):
        client = self.http_client
        response = await client.fetch(self.get_url("/ok"))

        print('all ok', response)

    @gen_test
    async def test_violation_1(self):
        client = self.http_client
        response = await client.fetch(self.get_url("/violation_1"))
        print("Response headers:") # Doesn't include the header we set after render because of the violation
        for header, value in response.headers.get_all():
            print(f"{header}: {value}")

    @gen_test
    async def test_violation_2(self):
        client = self.http_client
        response = await client.fetch(self.get_url("/violation_2"))
        print("Response status:", response.code) # Status still 200 although we later set to 404 because it was set after render
        print("Response headers:") # Doesn't include the headers we set after render also still have the header we cleard.
        for header, value in response.headers.get_all():
            print(f"{header}: {value}")


expected_violations_A = 5
expected_violations_B = [TestTornadoServer.test_violation_1, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2]
expected_violations_C = [TestTornadoServer.test_violation_1, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2]
expected_violations_C_plus = [TestTornadoServer.test_violation_1, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2]
expected_violations_D = [TestTornadoServer.test_violation_1, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2, TestTornadoServer.test_violation_2]
