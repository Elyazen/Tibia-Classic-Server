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
            traces.append({"event": "connect", "test": "A", "iter": i})
            time.sleep(0.1)
            s.close()
            traces.append({"event": "disconnect", "test": "A", "iter": i})
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
        traces.append({"event": "connect", "test": "B"})

        # Packet length = 5, Payload: 0x01 + 4 bytes zeroes
        payload = b'\x05\x00' + b'\x01\x00\x00\x00\x00'
        s.sendall(payload)
        traces.append({"event": "send", "test": "B", "bytes": len(payload)})

        try:
            s.settimeout(2.0)
            resp = s.recv(1024)
            traces.append({"event": "recv", "test": "B", "bytes": len(resp)})
        except socket.timeout:
            traces.append({"event": "timeout", "test": "B"})

        s.close()
        traces.append({"event": "disconnect", "test": "B"})
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
            traces.append({"event": "connect", "test": "C", "fuzz_iter": i})

            s.sendall(p)
            traces.append({"event": "send", "test": "C", "fuzz_iter": i, "bytes": len(p)})

            s.settimeout(1.0)
            try:
                resp = s.recv(1024)
                if resp:
                    traces.append({"event": "recv", "test": "C", "fuzz_iter": i, "bytes": len(resp)})
            except socket.timeout:
                traces.append({"event": "timeout", "test": "C", "fuzz_iter": i})

            s.close()
            traces.append({"event": "disconnect", "test": "C", "fuzz_iter": i})
        except Exception as e:
            print(f"Fuzz failed: {e}")

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

    with open(os.path.join(out_dir, "trace.json"), "w") as f:
        json.dump(all_traces, f, indent=2)

    print("Scenarios complete.")
