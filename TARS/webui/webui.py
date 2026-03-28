# Part of TARS integrated web UI – prepared for HTMX + Tailwind

import typer
import uvicorn
from typing import Annotated

app = typer.Typer(
    name="TARS-WebUI",
    help="CLI for TARS Web UI.",
    no_args_is_help=True,
)

@app.command()
def start(
    host: Annotated[str, typer.Option(help="Binding host")] = "0.0.0.0",
    port: Annotated[int, typer.Option(help="Binding port")] = 18780,
    reload: Annotated[bool, typer.Option(help="Enable hot reload (dev mode)")] = True,
):
    """Start the TARS Web UI server (FastAPI + Uvicorn)."""
    print(f"🚀 Starting TARS Web UI at http://{host}:{port}")
    uvicorn.run(
        "TARS.webui.api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )

def main():
    """Script entry point."""
    app()

if __name__ == "__main__":
    main()
