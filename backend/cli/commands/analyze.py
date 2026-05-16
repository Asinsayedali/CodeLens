"""CLI command for analyzing repositories"""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.services.analysis_service import AnalysisService

console = Console()


def analyze_command(
    path: str = typer.Argument(..., help="Local path or GitHub URL to analyze"),
    name: str = typer.Option(None, "--name", "-n", help="Project name (optional)")
):
    """
    Analyze a repository and extract its structure
    
    Examples:
        codelens analyze /path/to/local/repo
        codelens analyze https://github.com/user/repo
        codelens analyze /path/to/repo --name "My Project"
    """
    console.print(f"\n[bold blue]🔍 CodeLens Analysis[/bold blue]")
    console.print(f"[dim]Analyzing: {path}[/dim]\n")
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Create analysis service
        service = AnalysisService(db)
        
        # Run analysis
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Analyzing repository...", total=None)
            
            try:
                project = service.analyze_repository(path, name)
                
                progress.update(task, completed=True)
                
                # Display results
                console.print("\n[bold green]✅ Analysis Complete![/bold green]\n")
                console.print(f"[bold]Project:[/bold] {project.name}")
                console.print(f"[bold]ID:[/bold] {project.id}")
                console.print(f"[bold]Language:[/bold] {project.language}")
                console.print(f"[bold]Files:[/bold] {project.total_files}")
                console.print(f"[bold]Lines of Code:[/bold] {project.total_lines:,}")
                console.print(f"[bold]Status:[/bold] {project.status}")
                
                console.print(f"\n[dim]View results: codelens serve[/dim]")
                
            except Exception as e:
                progress.update(task, completed=True)
                console.print(f"\n[bold red]❌ Analysis Failed[/bold red]")
                console.print(f"[red]Error: {str(e)}[/red]")
                raise typer.Exit(code=1)
    
    finally:
        db.close()


def list_command():
    """List all analyzed projects"""
    console.print("\n[bold blue]📋 Projects[/bold blue]\n")
    
    db: Session = SessionLocal()
    
    try:
        service = AnalysisService(db)
        projects = service.list_projects()
        
        if not projects:
            console.print("[dim]No projects found. Run 'codelens analyze' to get started.[/dim]")
            return
        
        for project in projects:
            status_color = {
                'completed': 'green',
                'analyzing': 'yellow',
                'failed': 'red',
                'pending': 'blue'
            }.get(project.status, 'white')
            
            console.print(f"[bold]{project.id}.[/bold] {project.name}")
            console.print(f"   Status: [{status_color}]{project.status}[/{status_color}]")
            console.print(f"   Language: {project.language}")
            console.print(f"   Files: {project.total_files} | Lines: {project.total_lines:,}")
            console.print(f"   Path: [dim]{project.local_path}[/dim]")
            console.print()
    
    finally:
        db.close()


def delete_command(
    project_id: int = typer.Argument(..., help="Project ID to delete")
):
    """Delete a project and all its data"""
    
    db: Session = SessionLocal()
    
    try:
        service = AnalysisService(db)
        
        # Get project first to show name
        project = service.get_project(project_id)
        
        if not project:
            console.print(f"[red]❌ Project {project_id} not found[/red]")
            raise typer.Exit(code=1)
        
        # Confirm deletion
        confirm = typer.confirm(f"Delete project '{project.name}' (ID: {project_id})?")
        
        if not confirm:
            console.print("[dim]Deletion cancelled[/dim]")
            return
        
        # Delete project
        success = service.delete_project(project_id)
        
        if success:
            console.print(f"[green]✅ Project '{project.name}' deleted successfully[/green]")
        else:
            console.print(f"[red]❌ Failed to delete project[/red]")
            raise typer.Exit(code=1)
    
    finally:
        db.close()

# Made with Bob
