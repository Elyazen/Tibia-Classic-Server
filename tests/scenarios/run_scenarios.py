#!/usr/bin/env python3
import socket
import time
import os
import json
import sys

def test_a_connect_disconnect():
    print("Running Scenario A: Connect and Disconnect")
    traces = []

    for i in range(5):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", 7171))
            traces.append({"event": "connect", "test": "A", "iter": i, "timestamp": time.time()})
            time.sleep(0.1)
            s.close()
            traces.append({"event": "disconnect", "test": "A", "iter": i, "timestamp": time.time()})
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    return traces

def test_b_handshake():
    print("Running Scenario B: Handshake")
    traces = []

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 7171))
        traces.append({"event": "connect", "test": "B", "timestamp": time.time()})

        # Packet length = 5, Payload: 0x01 + 4 bytes zeroes
        payload = b'\x05\x00' + b'\x01\x00\x00\x00\x00'
        s.sendall(payload)
        traces.append({"event": "send", "test": "B", "bytes": len(payload), "timestamp": time.time()})

        try:
            s.settimeout(2.0)
            resp = s.recv(1024)
            traces.append({"event": "recv", "test": "B", "bytes": len(resp), "timestamp": time.time()})
        except socket.timeout:
            traces.append({"event": "timeout", "test": "B", "timestamp": time.time()})

        s.close()
        traces.append({"event": "disconnect", "test": "B", "timestamp": time.time()})
    except Exception as e:
        print(f"Handshake failed: {e}")
        return False

    return traces

def test_c_fuzz():
    print("Running Scenario C: Fuzz Lite")
    traces = []

    malformed_packets = [
        b'\xFF\xFF' + b'A'*100, # huge length declared, less payload sent
        b'\x00\x00',            # zero length
        b'\x01\x00\x02',        # length 1, payload 1 (invalid command)
    ]

    for i, p in enumerate(malformed_packets):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(("127.0.0.1", 7171))
            traces.append({"event": "connect", "test": "C", "fuzz_iter": i, "timestamp": time.time()})

            s.sendall(p)
            traces.append({"event": "send", "test": "C", "fuzz_iter": i, "bytes": len(p), "timestamp": time.time()})

            s.settimeout(1.0)
            try:
                resp = s.recv(1024)
                if resp:
                    traces.append({"event": "recv", "test": "C", "fuzz_iter": i, "bytes": len(resp), "timestamp": time.time()})
            except socket.timeout:
                traces.append({"event": "timeout", "test": "C", "fuzz_iter": i, "timestamp": time.time()})

            s.close()
            traces.append({"event": "disconnect", "test": "C", "fuzz_iter": i, "timestamp": time.time()})
        except Exception as e:
            print(f"Fuzz failed: {e}")

    return traces

def test_d_ping():
    print("Running Scenario D: Ping")
    traces = []

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 7171))
        traces.append({"event": "connect", "test": "D", "timestamp": time.time()})

        # Packet length = 1, Command = 0x1E (30, CL_CMD_PING)
        payload = b'\x01\x00\x1E'
        s.sendall(payload)
        traces.append({"event": "send", "test": "D", "bytes": len(payload), "timestamp": time.time()})

        try:
            s.settimeout(2.0)
            resp = s.recv(1024)
            traces.append({"event": "recv", "test": "D", "bytes": len(resp), "timestamp": time.time()})
        except socket.timeout:
            traces.append({"event": "timeout", "test": "D", "timestamp": time.time()})

        s.close()
        traces.append({"event": "disconnect", "test": "D", "timestamp": time.time()})
    except Exception as e:
        print(f"Ping failed: {e}")
        return False

    return traces

def test_e_login():
    print("Running Scenario E: Login Request")
    traces = []

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 7171))
        traces.append({"event": "connect", "test": "E", "timestamp": time.time()})

        # Packet length = 1, Command = 0x0A (10, CL_CMD_LOGIN_REQUEST)
        payload = b'\x01\x00\x0A'
        s.sendall(payload)
        traces.append({"event": "send", "test": "E", "bytes": len(payload), "timestamp": time.time()})

        try:
            s.settimeout(2.0)
            resp = s.recv(1024)
            traces.append({"event": "recv", "test": "E", "bytes": len(resp), "timestamp": time.time()})
        except socket.timeout:
            traces.append({"event": "timeout", "test": "E", "timestamp": time.time()})

        s.close()
        traces.append({"event": "disconnect", "test": "E", "timestamp": time.time()})
    except Exception as e:
        print(f"Login request failed: {e}")
        return False

    return traces

if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."

    all_traces = []

    t_a = test_a_connect_disconnect()
    if t_a: all_traces.extend(t_a)

    t_b = test_b_handshake()
    if t_b: all_traces.extend(t_b)

    t_c = test_c_fuzz()
    if t_c: all_traces.extend(t_c)

    t_d = test_d_ping()
    if t_d: all_traces.extend(t_d)

    t_e = test_e_login()
    if t_e: all_traces.extend(t_e)

    with open(os.path.join(out_dir, "trace.json"), "w") as f:
        json.dump(all_traces, f, indent=2)

    print("Scenarios complete.")
