"""CLI entry point for CodeLens"""

import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import settings
from app.database import init_db

# Create CLI app
app = typer.Typer(
    name="codelens",
    help="CodeLens - Intelligent Repository Analysis Platform",
    add_completion=False
)

console = Console()


@app.command()
def version():
    """Show CodeLens version"""
    console.print(f"[bold blue]CodeLens[/bold blue] version {settings.app_version}")


@app.command()
def init():
    """Initialize CodeLens database"""
    console.print("[yellow]Initializing database...[/yellow]")
    try:
        init_db()
        console.print("[green]✓ Database initialized successfully![/green]")
    except Exception as e:
        console.print(f"[red]✗ Error initializing database: {e}[/red]")
        raise typer.Exit(code=1)


@app.command()
def analyze(
    repo_path: str = typer.Argument(..., help="Repository path or GitHub URL"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Project name")
):
    """Analyze a repository"""
    from cli.commands.analyze import analyze_command
    analyze_command(repo_path, name)


@app.command()
def serve(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run server on"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to")
):
    """Start the CodeLens web server"""
    console.print(f"[yellow]Starting CodeLens server on {host}:{port}...[/yellow]")
    console.print("[blue]Press Ctrl+C to stop[/blue]")
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=settings.debug
        )
    except ImportError:
        console.print("[red]✗ uvicorn not installed. Run: pip install -r requirements.txt[/red]")
        raise typer.Exit(code=1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")


@app.command()
def list():
    """List all analyzed projects"""
    from cli.commands.analyze import list_command
    list_command()


@app.command()
def export(
    project_id: int = typer.Argument(..., help="Project ID to export"),
    format: str = typer.Option("json", "--format", "-f", help="Export format (json/pdf)")
):
    """Export project analysis (Phase 6 - Coming soon)"""
    console.print(f"[yellow]Exporting project {project_id} as {format}...[/yellow]")
    console.print("[blue]This feature will be implemented in Phase 6[/blue]")


@app.command()
def delete(
    project_id: int = typer.Argument(..., help="Project ID to delete")
):
    """Delete a project"""
    from cli.commands.analyze import delete_command
    delete_command(project_id)


def main():
    """Main entry point"""
    app()


if __name__ == "__main__":
    main()

# Made with Bob
