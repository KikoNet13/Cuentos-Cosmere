from __future__ import annotations

import argparse
import sys

from app.config import APP_TITLE


def cmd_runserver(host: str, port: int, debug: bool) -> None:
    from app import create_app

    app = create_app()
    app.run(host=host, port=port, debug=debug)


def main() -> None:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("runserver", help="Ejecutar servidor de desarrollo Flask")
    run.add_argument("--host", default="127.0.0.1", help="Host de escucha")
    run.add_argument("--port", type=int, default=5000, help="Puerto de escucha")
    run.add_argument("--debug", action="store_true", help="Activar modo depuracion")

    args = parser.parse_args()

    if args.command == "runserver":
        cmd_runserver(host=args.host, port=args.port, debug=args.debug)
    else:
        print(f"ERROR: comando no soportado: {args.command}")
        sys.exit(2)


if __name__ == "__main__":
    main()
