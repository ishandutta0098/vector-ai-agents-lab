#!/usr/bin/env python3
"""
CrewAI Memory Explorer

A unified, user-friendly script to explore and visualize CrewAI memory storage.
Simply provide the path to your CrewAI memory folder and get a comprehensive overview.

Usage:
    python crewai_memory_explorer.py [memory_folder_path]

If no path is provided, it will use the default location.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from rich.align import Align
from rich.box import DOUBLE, ROUNDED, SIMPLE
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.padding import Padding
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class CrewAIMemoryExplorer:
    """Explores and visualizes CrewAI memory storage in a user-friendly way."""

    def __init__(self, memory_path=None):
        """
        Initialize the memory explorer.

        Args:
            memory_path (str, optional): Path to the CrewAI memory directory
        """
        self.console = Console()

        if memory_path:
            self.memory_dir = Path(memory_path)
        else:
            # Default path - assumes script is run from the agents directory
            self.memory_dir = Path("beginner/crewai_memory")

        self.stats = {
            "task_outputs": 0,
            "long_term_memories": 0,
            "agents": set(),
            "total_embeddings": 0,
        }

    def normalize_agent_name(self, agent_name):
        """Normalize agent names to handle variations like spaces vs underscores."""
        return agent_name.replace("_", " ").strip()

    def print_header(self, title, style="bold magenta"):
        """Print a formatted header using Rich."""
        self.console.print()
        header_panel = Panel(
            Align.center(Text(title, style=style)),
            box=DOUBLE,
            border_style="bright_blue",
            padding=(1, 2),
        )
        self.console.print(header_panel)

    def print_section(self, title, style="bold cyan"):
        """Print a formatted section header using Rich."""
        self.console.print()
        self.console.print(Rule(title, style=style))

    def print_explanation(self, text, style="dim italic"):
        """Print explanation text with proper formatting using Rich."""
        explanation_panel = Panel(
            Text(f"💭 {text}", style=style),
            box=ROUNDED,
            border_style="dim blue",
            padding=(0, 1),
        )
        self.console.print(Padding(explanation_panel, (0, 2)))
        self.console.print()

    def explore_task_outputs(self):
        """Explore and display task execution outputs."""
        self.print_section("📋 TASK EXECUTION HISTORY", "bold green")
        self.print_explanation(
            "This section shows the actual task executions that have been run. Each execution "
            "includes the input data, expected output, actual result, and which agent performed the task. "
            "This is your execution log - a record of what your CrewAI agents have actually done."
        )

        kickoff_db = self.memory_dir / "latest_kickoff_task_outputs.db"

        if not kickoff_db.exists():
            self.console.print(
                Panel(
                    "❌ No task outputs database found.",
                    border_style="red",
                    box=ROUNDED,
                )
            )
            return

        try:
            conn = sqlite3.connect(str(kickoff_db))
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM latest_kickoff_task_outputs ORDER BY timestamp DESC"
            )
            outputs = cursor.fetchall()

            if not outputs:
                self.console.print(
                    Panel(
                        "📭 No task executions recorded yet.",
                        border_style="yellow",
                        box=ROUNDED,
                    )
                )
                conn.close()
                return

            self.stats["task_outputs"] = len(outputs)

            # Summary panel
            summary_text = Text(
                f"🎯 Total Task Executions: {len(outputs)}", style="bold green"
            )
            self.console.print(Panel(summary_text, border_style="green"))
            self.console.print()

            # Create table for task executions
            table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
            table.add_column("#", style="dim", width=4)
            table.add_column("Agent", style="cyan", width=15)
            table.add_column("Expected", style="yellow", width=25)
            table.add_column("Result", style="green", width=25)
            table.add_column("Status", style="blue", width=10)

            for i, output in enumerate(outputs, 1):
                (
                    task_id,
                    expected_output,
                    task_output,
                    task_index,
                    inputs,
                    was_replayed,
                    timestamp,
                ) = output

                # Parse task output
                try:
                    output_data = json.loads(task_output)
                    actual_output = output_data.get("raw", "N/A")
                    agent_name = output_data.get("agent", "Unknown")
                    task_desc = output_data.get("description", "N/A")

                    # Normalize agent name for counting
                    normalized_agent = self.normalize_agent_name(agent_name)
                    self.stats["agents"].add(normalized_agent)

                except json.JSONDecodeError:
                    actual_output = task_output
                    agent_name = "Unknown"

                # Truncate long text for table display
                expected_display = (
                    expected_output[:22] + "..."
                    if len(expected_output) > 25
                    else expected_output
                )
                result_display = (
                    actual_output[:22] + "..."
                    if len(actual_output) > 25
                    else actual_output
                )
                status = "🔄 Replayed" if was_replayed else "✅ Fresh"

                table.add_row(
                    str(i), agent_name, expected_display, result_display, status
                )

            self.console.print(table)

            # Show detailed view for recent executions
            if outputs:
                self.console.print()
                self.console.print(Rule("Recent Execution Details", style="dim cyan"))

                for i, output in enumerate(outputs[:3], 1):  # Show top 3
                    (
                        task_id,
                        expected_output,
                        task_output,
                        task_index,
                        inputs,
                        was_replayed,
                        timestamp,
                    ) = output

                    execution_tree = Tree(f"🔸 [bold]Execution #{i}[/bold]")

                    try:
                        output_data = json.loads(task_output)
                        actual_output = output_data.get("raw", "N/A")
                        agent_name = output_data.get("agent", "Unknown")
                        task_desc = output_data.get("description", "N/A")

                        execution_tree.add(f"🤖 [cyan]Agent:[/cyan] {agent_name}")
                        execution_tree.add(
                            f"🎯 [yellow]Expected:[/yellow] {expected_output}"
                        )
                        execution_tree.add(f"✅ [green]Result:[/green] {actual_output}")

                        if len(task_desc) > 100:
                            execution_tree.add(
                                f"📝 [blue]Task:[/blue] {task_desc[:100]}..."
                            )
                        else:
                            execution_tree.add(f"📝 [blue]Task:[/blue] {task_desc}")

                    except json.JSONDecodeError:
                        execution_tree.add(f"✅ [green]Result:[/green] {task_output}")

                    # Parse inputs
                    try:
                        input_data = json.loads(inputs)
                        if "text" in input_data:
                            input_text = input_data["text"]
                            if len(input_text) > 150:
                                execution_tree.add(
                                    f'📥 [dim]Input:[/dim] "{input_text[:150]}..."'
                                )
                            else:
                                execution_tree.add(
                                    f'📥 [dim]Input:[/dim] "{input_text}"'
                                )
                    except:
                        if len(inputs) > 100:
                            execution_tree.add(
                                f"📥 [dim]Input:[/dim] {inputs[:100]}..."
                            )
                        else:
                            execution_tree.add(f"📥 [dim]Input:[/dim] {inputs}")

                    if was_replayed:
                        execution_tree.add(
                            "🔄 [yellow]Note: This was a replayed execution[/yellow]"
                        )

                    self.console.print(execution_tree)
                    self.console.print()

            conn.close()

        except Exception as e:
            error_panel = Panel(
                f"❌ Error reading task outputs: {e}", border_style="red", box=ROUNDED
            )
            self.console.print(error_panel)

    def explore_long_term_memory(self):
        """Explore and display long-term memory."""
        self.print_section("🧠 LONG-TERM MEMORY & LEARNING", "bold purple")
        self.print_explanation(
            "Long-term memory stores lessons learned from past task executions. CrewAI's AI system "
            "analyzes each task performance and generates quality scores (0-10) and improvement suggestions. "
            "This helps agents get better over time by learning from experience. Higher quality scores "
            "indicate better task performance."
        )

        long_term_db = self.memory_dir / "long_term_memory_storage.db"

        if not long_term_db.exists():
            self.console.print(
                Panel(
                    "❌ No long-term memory database found.",
                    border_style="red",
                    box=ROUNDED,
                )
            )
            return

        try:
            conn = sqlite3.connect(str(long_term_db))
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM long_term_memories ORDER BY datetime DESC")
            memories = cursor.fetchall()

            if not memories:
                self.console.print(
                    Panel(
                        "🧭 No long-term memories stored yet.",
                        border_style="yellow",
                        box=ROUNDED,
                    )
                )
                conn.close()
                return

            self.stats["long_term_memories"] = len(memories)

            # Summary panel
            summary_text = Text(
                f"💾 Total Memories Stored: {len(memories)}", style="bold purple"
            )
            self.console.print(Panel(summary_text, border_style="purple"))
            self.console.print()

            # Create table for memories with quality scores
            table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
            table.add_column("#", style="dim", width=4)
            table.add_column("Agent", style="cyan", width=15)
            table.add_column(
                "Quality Score", style="yellow", width=12, justify="center"
            )
            table.add_column("Task Description", style="green", width=40)
            table.add_column("Suggestions", style="blue", width=10, justify="center")

            for i, memory in enumerate(memories, 1):
                id_val, task_desc, metadata, datetime_str, score = memory

                # Parse metadata for insights
                try:
                    meta_data = json.loads(metadata)
                    agent_name = meta_data.get("agent", "Unknown")

                    # Normalize agent name for counting
                    normalized_agent = self.normalize_agent_name(agent_name)
                    self.stats["agents"].add(normalized_agent)

                    # Count suggestions
                    suggestions_count = 0
                    if "suggestions" in meta_data and meta_data["suggestions"]:
                        suggestions_count = len(meta_data["suggestions"])

                except json.JSONDecodeError:
                    agent_name = "Unknown"
                    suggestions_count = 0

                # Format quality score with color coding
                score_color = "red" if score < 4 else "yellow" if score < 7 else "green"
                score_display = f"[{score_color}]{score}/10.0[/{score_color}]"

                # Truncate task description for table
                task_display = (
                    task_desc[:37] + "..." if len(task_desc) > 40 else task_desc
                )

                table.add_row(
                    str(i),
                    agent_name,
                    score_display,
                    task_display,
                    str(suggestions_count) if suggestions_count > 0 else "-",
                )

            self.console.print(table)

            # Show detailed view for top memories
            if memories:
                self.console.print()
                self.console.print(
                    Rule("Memory Details & AI Insights", style="dim purple")
                )

                for i, memory in enumerate(memories[:3], 1):  # Show top 3
                    id_val, task_desc, metadata, datetime_str, score = memory

                    # Create a tree for each memory
                    score_color = (
                        "red" if score < 4 else "yellow" if score < 7 else "green"
                    )
                    memory_tree = Tree(
                        f"🔸 [bold]Memory #{i}[/bold] - [bold {score_color}]Score: {score}/10.0[/bold {score_color}]"
                    )

                    # Show task description
                    if len(task_desc) > 120:
                        memory_tree.add(f"📝 [blue]Task:[/blue] {task_desc[:120]}...")
                    else:
                        memory_tree.add(f"📝 [blue]Task:[/blue] {task_desc}")

                    # Parse metadata for insights
                    try:
                        meta_data = json.loads(metadata)
                        agent_name = meta_data.get("agent", "Unknown")
                        expected = meta_data.get("expected_output", "N/A")

                        memory_tree.add(f"🤖 [cyan]Agent:[/cyan] {agent_name}")
                        memory_tree.add(
                            f"🎯 [yellow]Expected Output:[/yellow] {expected}"
                        )

                        # Show AI suggestions for improvement
                        if "suggestions" in meta_data and meta_data["suggestions"]:
                            suggestions = meta_data["suggestions"]
                            suggestions_node = memory_tree.add(
                                f"💡 [green]AI Suggestions ({len(suggestions)}):[/green]"
                            )

                            for j, suggestion in enumerate(suggestions[:3], 1):
                                suggestions_node.add(f"{j}. {suggestion}")

                            if len(suggestions) > 3:
                                suggestions_node.add(
                                    f"... and {len(suggestions) - 3} more suggestions"
                                )

                    except json.JSONDecodeError:
                        memory_tree.add(
                            f"📊 [dim]Raw Metadata:[/dim] {metadata[:100]}..."
                        )

                    self.console.print(memory_tree)
                    self.console.print()

            conn.close()

        except Exception as e:
            error_panel = Panel(
                f"❌ Error reading long-term memory: {e}",
                border_style="red",
                box=ROUNDED,
            )
            self.console.print(error_panel)

    def explore_vector_memory(self):
        """Explore vector embeddings and semantic memory."""
        self.print_section("🔍 VECTOR MEMORY & SEMANTIC STORAGE", "bold blue")
        self.print_explanation(
            "Vector memory stores semantic embeddings (mathematical representations) of concepts, entities, "
            "and context from your tasks. This allows agents to understand relationships between ideas and "
            "retrieve relevant context. Entity Memory persists across sessions, while Short-term Memory "
            "is cleared after each run. The embeddings help agents understand meaning, not just exact text matches."
        )

        memory_types = [
            ("🏛️ Entity Memory", "entities", "bright_yellow"),
            ("⚡ Short-term Memory", "short_term", "bright_cyan"),
        ]

        total_embeddings = 0
        memory_summary = []

        for mem_type_name, mem_dir_name, color_style in memory_types:
            mem_path = self.memory_dir / mem_dir_name

            if not mem_path.exists():
                self.console.print(
                    f"[red]{mem_type_name}: ❌ Directory not found[/red]"
                )
                continue

            # Create a panel for each memory type
            self.console.print(f"\n[{color_style}]{mem_type_name}[/{color_style}]")

            agent_dirs = [d for d in mem_path.iterdir() if d.is_dir()]

            if not agent_dirs:
                self.console.print(
                    Panel("📭 No agent memory found", border_style="yellow", box=SIMPLE)
                )
                continue

            # Create table for this memory type
            table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
            table.add_column("Agent", style="cyan", width=20)
            table.add_column("Embeddings", style="yellow", width=12, justify="right")
            table.add_column("Vector Files", style="green", width=12, justify="right")
            table.add_column("Sample Content", style="blue", width=50)

            for agent_dir in agent_dirs:
                agent_name = agent_dir.name
                display_name = self.normalize_agent_name(agent_name)

                # Normalize agent name for counting
                self.stats["agents"].add(display_name)

                embedding_count = 0
                sample_content = "No content"
                vector_file_count = 0

                # Check ChromaDB for embeddings
                chroma_db = agent_dir / "chroma.sqlite3"
                if chroma_db.exists():
                    try:
                        conn = sqlite3.connect(str(chroma_db))
                        cursor = conn.cursor()

                        # Count embeddings
                        cursor.execute("SELECT COUNT(*) FROM embeddings")
                        embedding_count = cursor.fetchone()[0]
                        total_embeddings += embedding_count

                        # Get sample content from metadata
                        cursor.execute(
                            """
                            SELECT string_value 
                            FROM embedding_metadata 
                            WHERE key = 'chroma:document' 
                            LIMIT 1
                        """
                        )
                        sample = cursor.fetchone()
                        if sample:
                            content = sample[0]
                            sample_content = (
                                content[:47] + "..." if len(content) > 50 else content
                            )

                        conn.close()

                    except Exception as e:
                        sample_content = f"Error: {str(e)[:30]}..."

                # Count vector index files
                vector_dirs = [
                    d
                    for d in agent_dir.iterdir()
                    if d.is_dir() and d.name != "__pycache__"
                ]
                for vec_dir in vector_dirs:
                    try:
                        vector_file_count += len(list(vec_dir.iterdir()))
                    except:
                        pass

                # Add row to table
                embedding_display = (
                    f"[green]{embedding_count}[/green]"
                    if embedding_count > 0
                    else "[dim]0[/dim]"
                )
                files_display = (
                    f"[green]{vector_file_count}[/green]"
                    if vector_file_count > 0
                    else "[dim]0[/dim]"
                )

                table.add_row(
                    display_name, embedding_display, files_display, sample_content
                )

                memory_summary.append(
                    {
                        "type": mem_type_name,
                        "agent": display_name,
                        "embeddings": embedding_count,
                        "files": vector_file_count,
                    }
                )

            self.console.print(table)

        self.stats["total_embeddings"] = total_embeddings

        # Show vector memory tree summary
        if memory_summary:
            self.console.print()
            self.console.print(Rule("Vector Memory Structure", style="dim blue"))

            memory_tree = Tree("🧠 [bold blue]Vector Memory Overview[/bold blue]")

            entity_node = memory_tree.add(
                "🏛️ [bright_yellow]Entity Memory (Persistent)[/bright_yellow]"
            )
            short_term_node = memory_tree.add(
                "⚡ [bright_cyan]Short-term Memory (Session)[/bright_cyan]"
            )

            for item in memory_summary:
                if "Entity" in item["type"]:
                    node = entity_node
                else:
                    node = short_term_node

                agent_info = f"🤖 {item['agent']}: {item['embeddings']} embeddings, {item['files']} files"
                if item["embeddings"] > 0:
                    node.add(f"[green]{agent_info}[/green]")
                else:
                    node.add(f"[dim]{agent_info}[/dim]")

            self.console.print(memory_tree)

    def show_summary_statistics(self):
        """Display overall statistics and insights."""
        self.print_section("📊 MEMORY STATISTICS & INSIGHTS", "bold yellow")
        self.print_explanation(
            "This summary shows the overall health and activity of your CrewAI memory system. "
            "It counts total executions, stored memories, vector embeddings, and active agents. "
            "The health check verifies that all memory components are working properly. More "
            "executions and memories indicate a more experienced and capable AI system."
        )

        # Create statistics table
        stats_table = Table(show_header=True, header_style="bold magenta", box=DOUBLE)
        stats_table.add_column("Metric", style="cyan", width=25)
        stats_table.add_column("Count", style="yellow", width=15, justify="right")
        stats_table.add_column("Status", style="green", width=20)

        # Add statistics rows
        stats_table.add_row(
            "🎯 Task Executions",
            str(self.stats["task_outputs"]),
            "✅ Active" if self.stats["task_outputs"] > 0 else "⚠️ None recorded",
        )
        stats_table.add_row(
            "🧠 Long-term Memories",
            str(self.stats["long_term_memories"]),
            "✅ Learning" if self.stats["long_term_memories"] > 0 else "⚠️ No memories",
        )
        stats_table.add_row(
            "🔍 Vector Embeddings",
            str(self.stats["total_embeddings"]),
            (
                "✅ Functioning"
                if self.stats["total_embeddings"] > 0
                else "⚠️ No embeddings"
            ),
        )
        stats_table.add_row(
            "🤖 Active Agents",
            str(len(self.stats["agents"])),
            "✅ Memory enabled" if len(self.stats["agents"]) > 0 else "⚠️ No agents",
        )

        self.console.print(stats_table)

        # Show agent names if available
        if self.stats["agents"]:
            self.console.print()
            agents_panel = Panel(
                f"Agent Names: {', '.join(sorted(self.stats['agents']))}",
                title="🤖 Active Agents",
                border_style="cyan",
            )
            self.console.print(agents_panel)

        self.console.print()

        # Memory health check with visual indicators
        health_tree = Tree("🏥 [bold red]Memory Health Check[/bold red]")

        if self.stats["task_outputs"] > 0:
            health_tree.add("✅ [green]Task execution tracking is working[/green]")
        else:
            health_tree.add("⚠️ [yellow]No task executions recorded[/yellow]")

        if self.stats["long_term_memories"] > 0:
            health_tree.add("✅ [green]Long-term learning is active[/green]")
        else:
            health_tree.add("⚠️ [yellow]No long-term memories stored[/yellow]")

        if self.stats["total_embeddings"] > 0:
            health_tree.add("✅ [green]Vector memory is functioning[/green]")
        else:
            health_tree.add("⚠️ [yellow]No vector embeddings found[/yellow]")

        if len(self.stats["agents"]) > 0:
            health_tree.add(
                f"✅ [green]{len(self.stats['agents'])} agent(s) have memory enabled[/green]"
            )
        else:
            health_tree.add("⚠️ [yellow]No agents found with memory[/yellow]")

        self.console.print(health_tree)

        # Overall health score
        health_score = 0
        max_score = 4

        if self.stats["task_outputs"] > 0:
            health_score += 1
        if self.stats["long_term_memories"] > 0:
            health_score += 1
        if self.stats["total_embeddings"] > 0:
            health_score += 1
        if len(self.stats["agents"]) > 0:
            health_score += 1

        health_percentage = (health_score / max_score) * 100
        health_color = (
            "red"
            if health_percentage < 50
            else "yellow" if health_percentage < 80 else "green"
        )

        self.console.print()
        health_panel = Panel(
            f"Overall Health Score: [{health_color}]{health_score}/{max_score} ({health_percentage:.0f}%)[/{health_color}]",
            title="🎯 System Health",
            border_style=health_color,
        )
        self.console.print(health_panel)

    def explore_memory(self):
        """Main method to explore all memory components."""
        if not self.memory_dir.exists():
            error_panel = Panel(
                f"❌ Memory directory not found: {self.memory_dir}\nPlease check the path and try again.",
                title="Error",
                border_style="red",
            )
            self.console.print(error_panel)
            return

        self.print_header("🧠 CrewAI Memory Explorer")

        # Show memory location with nice formatting
        location_panel = Panel(
            f"📁 Memory Location: [cyan]{self.memory_dir}[/cyan]", border_style="blue"
        )
        self.console.print(location_panel)

        self.print_explanation(
            "This tool analyzes your CrewAI memory storage to show what your agents have learned "
            "and remembered. Memory helps agents improve performance over time by storing execution "
            "history, learning from mistakes, and building contextual understanding."
        )

        # Add a progress indicator for the exploration
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:

            # Explore all memory components
            task1 = progress.add_task("Analyzing task execution history...", total=None)
            self.explore_task_outputs()
            progress.remove_task(task1)

            task2 = progress.add_task("Examining long-term memory...", total=None)
            self.explore_long_term_memory()
            progress.remove_task(task2)

            task3 = progress.add_task("Scanning vector embeddings...", total=None)
            self.explore_vector_memory()
            progress.remove_task(task3)

            task4 = progress.add_task("Generating statistics...", total=None)
            self.show_summary_statistics()
            progress.remove_task(task4)

        # Final completion message
        self.print_header("✨ Analysis Complete!", "bold green")

        completion_panel = Panel(
            "💡 [yellow]Tip:[/yellow] Run your CrewAI script more times to see memory evolution!\n"
            "🔄 [cyan]Re-run this explorer after each execution to track learning progress.[/cyan]",
            title="Next Steps",
            border_style="green",
        )
        self.console.print(completion_panel)


def main():
    """Main function to handle command line arguments and run the explorer."""
    console = Console()

    # Welcome banner
    welcome_panel = Panel(
        Align.center("🚀 [bold magenta]CrewAI Memory Explorer[/bold magenta] 🚀"),
        box=DOUBLE,
        border_style="bright_blue",
        padding=(1, 2),
    )
    console.print(welcome_panel)

    # Handle command line arguments
    if len(sys.argv) > 1:
        memory_path = sys.argv[1]
        console.print(
            f"📁 [green]Using provided path:[/green] [cyan]{memory_path}[/cyan]"
        )
    else:
        memory_path = None
        console.print("📁 [yellow]Using default memory location[/yellow]")

    console.print()

    # Create and run explorer
    explorer = CrewAIMemoryExplorer(memory_path)
    explorer.explore_memory()


if __name__ == "__main__":
    main()
