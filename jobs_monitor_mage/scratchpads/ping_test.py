"""
NOTE: Scratchpad blocks are used only for experimentation and testing out code.
The code written here will not be executed as part of the pipeline.
"""
import socket
import os

def check_db():
    target_host = "data-controller"
    target_host_1 = os.getenv('POSTGRES_HOST')
    port = 5432
    try:
        socket.create_connection((target_host_1, port), timeout=5)
        print(f"\t\t {target_host_1} on {port}")
    except Exception as e:
        print(f"\t\t FAILURE: {e}")

check_db()