import pytest
import http.client
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# Dummy server implementation
class DummyServer(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        print(f"Server received: {post_data.decode('utf-8')}")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "success", "received": true}')


@pytest.fixture(scope="session", autouse=True)
def server():
    """Fixture to start and stop the dummy server."""
    server_address = ("localhost", 8000)
    httpd = HTTPServer(server_address, DummyServer)
    thread = Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    print("Dummy server started on http://localhost:8000")
    yield
    httpd.shutdown()
    print("Dummy server stopped")


def test_ok_1():
    """Test correct usage of HTTPConnection.send()."""
    data = {"key": "value"}
    encoded_data = json.dumps(data).encode("utf-8")

    conn = http.client.HTTPConnection("localhost", 8000)
    conn.putrequest("POST", "/")
    conn.putheader("Content-Type", "application/json")
    conn.putheader("Content-Length", str(len(encoded_data)))

    conn.endheaders()
    conn.send(encoded_data)
    response = conn.getresponse()

    assert response.status == 200
    assert json.loads(response.read()) == {"status": "success", "received": True}
    conn.close()

def test_ok_2():
    """resuse the connection"""
    data = {"key": "value"}
    encoded_data = json.dumps(data).encode("utf-8")

    conn = http.client.HTTPConnection("localhost", 8000)
    conn.putrequest("POST", "/")
    conn.putheader("Content-Type", "application/json")
    conn.putheader("Content-Length", str(len(encoded_data)))

    conn.endheaders()
    conn.send(encoded_data)
    response = conn.getresponse()

    assert response.status == 200
    assert json.loads(response.read()) == {"status": "success", "received": True}

    conn.putrequest("POST", "/")
    conn.putheader("Content-Type", "application/json")
    conn.putheader("Content-Length", str(len(encoded_data)))
    conn.endheaders()
    conn.send(encoded_data)
    response = conn.getresponse()

    assert response.status == 200
    assert json.loads(response.read()) == {"status": "success", "received": True}
    conn.close()

def test_ok_3():
    """Test using request() instead of manually constructing the request."""
    data = {"key": "value"}
    encoded_data = json.dumps(data).encode("utf-8")

    conn = http.client.HTTPConnection("localhost", 8000)
    conn.request("POST", "/", body=encoded_data, headers={"Content-Type": "application/json", "Content-Length": str(len(encoded_data))})
    response = conn.getresponse()

    assert response.status == 200
    assert json.loads(response.read()) == {"status": "success", "received": True}
    conn.close()

def test_violation_1():
    """Test calling send() before endheaders()."""
    data = {"key": "value"}
    encoded_data = json.dumps(data).encode("utf-8")

    conn = http.client.HTTPConnection("localhost", 8000)
    conn.putrequest("POST", "/")
    conn.putheader("Content-Type", "application/json")
    conn.putheader("Content-Length", str(len(encoded_data)))

    # conn.endheaders() # <------------ VIOLATION: Missing endheaders()

    conn.send(encoded_data)
    # response = conn.getresponse() # commented out because it's gonna get stuck
    conn.close()


def test_violation_2():
    """Test calling send() after getresponse()."""

    def run_test():
        data = {"key": "value"}
        encoded_data = json.dumps(data).encode("utf-8")

        conn = http.client.HTTPConnection("localhost", 8000, timeout=1)
        conn.putrequest("POST", "/")
        conn.putheader("Content-Type", "application/json")
        conn.putheader("Content-Length", str(len(encoded_data)))
        conn.endheaders()

        print("getresponse")
        try:
            conn.getresponse()  # <------------ VIOLATION: Prematurely fetch the response.
        except:
            pass

        conn.send(encoded_data)  # This will not be reached due to the stuck line.
        conn.close()

    try:
        thread = Thread(target=run_test)
        thread.start()
        thread.join(timeout=5)  # Set timeout of 5 seconds
    except Exception as e:
        pytest.fail(f"Test failed with exception: {e}")

expected_violations_A = 2
expected_violations_B = [test_violation_1, test_violation_2]
expected_violations_C = [test_violation_1, test_violation_2]
expected_violations_C_plus = [test_violation_1, test_violation_2]
expected_violations_D = [test_violation_1, test_violation_2]
