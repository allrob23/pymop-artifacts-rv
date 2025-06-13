import asyncio
import pytest

async def handle_client(reader, writer):
    try:
        data = await reader.read(10000000)  # Increase buffer size for larger messages
        message = data.decode()
        if message:
            print(f"Server received: {message[:50]}... (truncated)")
            print(f"Message size: {len(message)}")
        else:
            print("Server: No data received (or incomplete data).")
    except Exception as e:
        print(f"Server encountered an error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def start_server():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    async with server:
        await server.serve_forever()

@pytest.mark.asyncio
async def test_ok_1():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
    writer.write(large_message)
    await writer.drain()  # Ensure data is flushed properly

    writer.close()
    await writer.wait_closed()

    server_task.cancel()

@pytest.mark.asyncio
async def test_ok_2():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    for i in range(5):
        large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
        writer.write(large_message)
        await writer.drain()  # Ensure data is flushed properly
    writer.close()
    await writer.wait_closed()

    server_task.cancel()

@pytest.mark.asyncio
async def test_ok_3():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
    writer.writelines([large_message])
    await writer.drain()  # Ensure data is flushed properly

    writer.close()
    await writer.wait_closed()

    server_task.cancel()

@pytest.mark.asyncio
async def test_ok_4():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    for i in range(5):
        large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
        writer.writelines([large_message])
        await writer.drain()  # Ensure data is flushed properly
    writer.close()
    await writer.wait_closed()

    server_task.cancel()

@pytest.mark.asyncio
async def test_ok_5():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    writer.close()
    await writer.wait_closed()

    server_task.cancel()

@pytest.mark.asyncio
async def test_violation_1():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
    writer.write(large_message)
    # Violation: Skip `await writer.drain()`

    writer.close()
    await writer.wait_closed()

    server_task.cancel()

@pytest.mark.asyncio
async def test_violation_2():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    for i in range(5):
        large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
        writer.write(large_message)
        # Violation: Skip `await writer.drain()`
    writer.close()
    await writer.wait_closed()

    server_task.cancel()

@pytest.mark.asyncio
async def test_violation_3(): #?
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    for i in range(5):
        large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
        writer.write(large_message)
        await writer.drain()
    writer.close()
    # Violation: Skip `await writer.wait_closed()`

    server_task.cancel()

@pytest.mark.asyncio
async def test_violation_4(): #?
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    for i in range(5):
        large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
        writer.write(large_message)
        await writer.drain()
    # Violation: Skip `writer.close()`
    await writer.wait_closed()

    server_task.cancel()


@pytest.mark.asyncio
async def test_violation_5():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
    writer.writelines([large_message])
    # Violation: Skip `await writer.drain()`

    writer.close()
    await writer.wait_closed()

    server_task.cancel()

@pytest.mark.asyncio
async def test_violation_6():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    for i in range(5):
        large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
        writer.writelines([large_message])
        # Violation: Skip `await writer.drain()`
    writer.close()
    await writer.wait_closed()

    server_task.cancel()

@pytest.mark.asyncio
async def test_violation_7(): #?
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    for i in range(5):
        large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
        writer.writelines([large_message])
        await writer.drain()
    writer.close()
    # Violation: Skip `await writer.wait_closed()`

    server_task.cancel()

@pytest.mark.asyncio
async def test_violation_8():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    for i in range(5):
        large_message = b"A" * 1000 + b"Hello, Server! This is a larger message to test partial data transmission."
        writer.writelines([large_message])
        await writer.drain()
    # Violation: Skip `writer.close()`
    await writer.wait_closed()

    server_task.cancel()

# test_violation_3, test_violation_4, and test_violation_7 would appear as test_violation_8 because they all depend on End event
# Flakiness: this spec seems to be flaky: sometimes we get 3 or 2 test_violation_8, also sometimes we get test_violation_4
expected_violations_A = 20
expected_violations_B = [test_violation_1, test_violation_2, test_violation_4, test_violation_5, test_violation_6, test_violation_8, test_violation_8, test_violation_8]
expected_violations_C = [test_violation_1, test_violation_2, test_violation_4, test_violation_5, test_violation_6, test_violation_8, test_violation_8, test_violation_8]
expected_violations_C_plus = [test_violation_1, test_violation_2, test_violation_4, test_violation_5, test_violation_6, test_violation_8, test_violation_8, test_violation_8]
expected_violations_D = [test_violation_1, test_violation_2, test_violation_4, test_violation_5, test_violation_6, test_violation_8, test_violation_8, test_violation_8]
