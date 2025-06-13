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
async def test_violation_1():
    server_task = asyncio.create_task(start_server())
    await asyncio.sleep(0.1)  # Ensure server starts

    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)

    print('\n\n\n\n\n WILL CREATE THE STREAM WRITERRRR \n\n\n\n\n')
    asyncio.StreamWriter(writer._transport, writer._protocol, writer._reader, writer._loop) # <----------- VIOLATION

    writer.close()
    await writer.wait_closed()

    server_task.cancel()


expected_violations_A = 1
expected_violations_B = [test_violation_1]
expected_violations_C = [test_violation_1]
expected_violations_C_plus = [test_violation_1]
expected_violations_D = [test_violation_1]
