"""Command-line entry point for policyrag."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from policyrag import __version__
from policyrag.answer import synthesize
from policyrag.chunking import chunk_directory
from policyrag.index import TfidfIndex

console = Console()
DEFAULT_POLICIES_DIR = "policies"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="policyrag",
        description="Ask questions about your policy documents; get cited excerpts back.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ask = subparsers.add_parser("ask", help="Ask a question against the policy corpus.")
    ask.add_argument("question", help="The question to ask.")
    ask.add_argument(
        "--policies-dir",
        default=DEFAULT_POLICIES_DIR,
        help=f"Directory of *.md policy documents (default: {DEFAULT_POLICIES_DIR})",
    )
    ask.add_argument("--top-k", type=int, default=3, help="Number of excerpts to retrieve (default: 3)")
    ask.add_argument(
        "--synthesize",
        action="store_true",
        help="Also synthesize a cited answer via the Claude API (requires ANTHROPIC_API_KEY).",
    )

    list_cmd = subparsers.add_parser("list", help="List indexed policy documents and chunk counts.")
    list_cmd.add_argument("--policies-dir", default=DEFAULT_POLICIES_DIR)

    parser.add_argument("--version", action="version", version=f"policyrag {__version__}")
    return parser


def _run_ask(args: argparse.Namespace) -> int:
    policies_dir = Path(args.policies_dir)
    if not policies_dir.is_dir():
        console.print(f"[bold red]No such directory: {policies_dir}[/bold red]")
        return 1

    chunks = chunk_directory(policies_dir)
    if not chunks:
        console.print(f"[yellow]No *.md policy documents found under '{policies_dir}'.[/yellow]")
        return 0

    index = TfidfIndex.from_chunks(chunks)
    results = index.search(args.question, top_k=args.top_k)

    if not results:
        console.print("[yellow]No policy excerpts matched that question.[/yellow]")
        return 0

    table = Table(show_lines=True, title=f"Top {len(results)} matching excerpt(s)")
    table.add_column("Score", no_wrap=True)
    table.add_column("Source")
    table.add_column("Excerpt")

    for chunk, score in results:
        preview = chunk.text if len(chunk.text) <= 320 else chunk.text[:317] + "..."
        table.add_row(f"{score:.3f}", chunk.citation, preview)

    console.print(table)

    if args.synthesize:
        answer = synthesize(args.question, results)
        if answer:
            console.print(Panel(answer, title="Synthesized answer", border_style="green"))
        else:
            console.print(
                "[yellow]--synthesize requested but no answer was produced "
                "(ANTHROPIC_API_KEY not set, or the API call failed) — "
                "showing retrieved excerpts only.[/yellow]"
            )

    return 0


def _run_list(args: argparse.Namespace) -> int:
    policies_dir = Path(args.policies_dir)
    if not policies_dir.is_dir():
        console.print(f"[bold red]No such directory: {policies_dir}[/bold red]")
        return 1

    table = Table(title="Indexed policy documents")
    table.add_column("File")
    table.add_column("Title")
    table.add_column("Chunks", justify="right")

    for path in sorted(policies_dir.glob("*.md")):
        from policyrag.chunking import chunk_document

        chunks = chunk_document(path)
        title = chunks[0].title if chunks else path.stem
        table.add_row(path.name, title, str(len(chunks)))

    console.print(table)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "ask":
        return _run_ask(args)
    if args.command == "list":
        return _run_list(args)

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
