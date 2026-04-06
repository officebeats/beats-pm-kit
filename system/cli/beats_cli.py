import typer
from rich.console import Console

app = typer.Typer(help="Beats PM Kit CLI - powered by Antigravity")
console = Console()

@app.command()
def dashboard():
    """Launch the Beats PM Kit TUI Dashboard"""
    # We will hook this up to Textual later
    console.print("[bold cyan]Launching the Beats PM TUI Dashboard...[/bold cyan]")
    try:
        from tui import BeatsDashboard
        app_tui = BeatsDashboard()
        app_tui.run()
    except ImportError:
        console.print("[bold yellow]TUI modules not fully implemented yet.[/bold yellow]")

@app.command()
def discover():
    """Run the discover workflow"""
    console.print("[bold green]Starting /discover workflow...[/bold green]")
    from router import execute_prompt
    response = execute_prompt("Run the /discover workflow on the current backlog.")
    console.print(response)

@app.command()
def retro():
    """Run the retro workflow"""
    console.print("[bold green]Starting /retro workflow...[/bold green]")
    from router import execute_prompt
    response = execute_prompt("Facilitate a retrospective on the active sprint.")
    console.print(response)

if __name__ == "__main__":
    app()
