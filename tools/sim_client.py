"""Execute project files through NVIDIA's Isaac Sim 5.1 VS Code server."""
import argparse
import json
from pathlib import Path
import socket


def execute(source, port=8226):
    # The 5.1 server treats each TCP receive as a complete source submission.
    # Send only a short loader, never the contents of a large project file.
    if len(source.encode()) > 4096:
        raise ValueError("Use a project file instead of a large inline command")
    with socket.create_connection(("127.0.0.1", port), timeout=10) as connection:
        connection.settimeout(30)
        connection.sendall(source.encode())
        chunks = []
        while True:
            chunk = connection.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
    reply = json.loads(b"".join(chunks))
    print(reply.get("output", ""))
    if reply.get("status") != "ok":
        raise RuntimeError(json.dumps(reply, indent=2))
    return reply


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", nargs="?", type=Path)
    parser.add_argument("--port", type=int, default=8226)
    args = parser.parse_args()
    if args.file:
        path = args.file.resolve(strict=True)
        source = (f"import sys, runpy; sys.path.insert(0, {str(Path(__file__).resolve().parents[1] / 'navigation')!r}); "
                  f"sys.path.insert(0, {str(path.parent)!r}); "
                  f"runpy.run_path({str(path)!r}, run_name='__main__')")
    else:
        source = ("import omni.usd, omni.timeline; "
                  "print('ISAAC_CONNECTION_VERIFIED'); "
                  "print('Stage:', omni.usd.get_context().get_stage()); "
                  "print('Playing:', omni.timeline.get_timeline_interface().is_playing())")
    try:
        execute(source, args.port)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Isaac Sim execution failed: {error}\n")


if __name__ == "__main__":
    main()
