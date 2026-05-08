"""
Interactive interfaces (terminal menu + Tk UI) and the command-line entry point.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Optional

from .core import TodoApp, TodoItem


def _format_task(task: TodoItem) -> str:
    status = "✓" if task.completed else " "
    due = f" (due {task.due_date:%Y-%m-%d %H:%M})" if task.due_date else ""
    return f"[{status}] #{task.task_id} {task.title}{due}"


def _print_tasks(tasks: Iterable[TodoItem]) -> None:
    task_list = list(tasks)
    for task in task_list:
        print(_format_task(task))
        if task.description:
            print(f"    {task.description}")
    if not task_list:
        print("No tasks found.")


def _prompt(prompt: str) -> str:
    return input(prompt).strip()


def _main_loop(app: Optional[TodoApp] = None) -> None:
    app = app or TodoApp()
    menu = {
        "1": "Add task",
        "2": "List tasks",
        "3": "Mark complete",
        "4": "Mark incomplete",
        "5": "Update task",
        "6": "Delete task",
        "7": "Search tasks",
        "8": "Purge completed",
        "9": "Exit",
    }

    while True:
        print("\nTodo App")
        for key, label in menu.items():
            print(f"{key}. {label}")

        choice = _prompt("Choose an option: ")

        try:
            if choice == "1":
                title = _prompt("Title: ")
                description = _prompt("Description (optional): ")
                due = _prompt("Due date YYYY-MM-DD or leave blank: ")
                task = app.add_task(title, description, due or None)
                print(f"Added task #{task.task_id}")
            elif choice == "2":
                status = _prompt("Status [all/pending/completed]: ").lower() or "all"
                _print_tasks(app.list_tasks(status))
            elif choice == "3":
                task_id = int(_prompt("Task id to complete: "))
                app.mark_complete(task_id)
                print("Task marked complete.")
            elif choice == "4":
                task_id = int(_prompt("Task id to mark incomplete: "))
                app.mark_incomplete(task_id)
                print("Task marked incomplete.")
            elif choice == "5":
                task_id = int(_prompt("Task id to update: "))
                title = _prompt("New title (leave blank to keep): ")
                description = _prompt("New description (leave blank to keep): ")
                due = _prompt("New due date (leave blank to keep): ")
                app.update_task(
                    task_id,
                    title=title or None,
                    description=description or None,
                    due_date=due or None,
                )
                print("Task updated.")
            elif choice == "6":
                task_id = int(_prompt("Task id to delete: "))
                app.delete_task(task_id)
                print("Task deleted.")
            elif choice == "7":
                keyword = _prompt("Keyword to search for: ")
                _print_tasks(app.search(keyword))
            elif choice == "8":
                removed = app.purge_completed()
                print(f"Removed {removed} completed tasks.")
            elif choice == "9":
                print("Goodbye!")
                break
            else:
                print("Invalid option.")
        except (ValueError, LookupError) as exc:
            print(f"Error: {exc}")


def _demo_run() -> None:
    print("Running todo demo (non-interactive mode).\n")
    app = TodoApp()
    first = app.add_task("Write documentation", "Update README with new instructions.")
    second = app.add_task("Plan sprint", due_date="2024-12-31")
    third = app.add_task("Refactor module", "Clean up utils package.")

    print("Initial tasks:")
    _print_tasks(app.list_tasks())

    print("\nMarking the second task complete and updating the third one...")
    app.mark_complete(second.task_id)
    app.update_task(third.task_id, title="Refactor auth module", description="Focus on login flow.")
    _print_tasks(app.list_tasks())

    print("\nSearching for 'auth':")
    _print_tasks(app.search("auth"))

    print("\nPurging completed tasks:")
    removed = app.purge_completed()
    print(f"Removed {removed} tasks.")
    _print_tasks(app.list_tasks())

    print("\nDemo finished. Run with --interactive to use the menu.")


def run_ui(storage_path: Optional[str | Path] = None) -> None:
    """Launch a Tkinter UI around the TodoApp core."""

    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ImportError as exc:  # pragma: no cover - only triggered in unusual envs
        raise SystemExit(
            "Tkinter is required for the UI. It ships with most Python installs."
        ) from exc

    class TodoUI:
        def __init__(self, root: tk.Tk) -> None:
            self.root = root
            self.app = TodoApp(storage_path=storage_path)
            self.selected_task_id: Optional[int] = None

            self.filter_var = tk.StringVar(value="all")
            self.search_var = tk.StringVar()
            self.title_var = tk.StringVar()
            self.due_var = tk.StringVar()
            self.status_var = tk.StringVar(value="Welcome! Add your first task.")

            self._build_ui()
            self.refresh_task_list()

        def _build_ui(self) -> None:
            self.root.title("Todo App")
            self.root.geometry("980x620")
            self.root.configure(padx=16, pady=16)
            self.root.grid_columnconfigure(0, weight=3)
            self.root.grid_columnconfigure(1, weight=2)
            self.root.grid_rowconfigure(1, weight=1)

            top = ttk.Frame(self.root)
            top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))
            top.grid_columnconfigure(3, weight=1)

            ttk.Label(top, text="Filter:").grid(row=0, column=0, sticky="w")
            filter_box = ttk.Combobox(
                top,
                textvariable=self.filter_var,
                values=("all", "pending", "completed"),
                state="readonly",
                width=12,
            )
            filter_box.grid(row=0, column=1, sticky="w", padx=(6, 0))
            filter_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_task_list())

            ttk.Label(top, text="Search:").grid(row=0, column=2, sticky="e", padx=(12, 6))
            search_entry = ttk.Entry(top, textvariable=self.search_var)
            search_entry.grid(row=0, column=3, sticky="ew")
            search_entry.bind("<KeyRelease>", lambda _event: self.refresh_task_list())
            ttk.Button(top, text="Clear", command=self._clear_search).grid(
                row=0, column=4, padx=(8, 0)
            )

            list_frame = ttk.LabelFrame(self.root, text="Tasks")
            list_frame.grid(row=1, column=0, sticky="nsew")
            list_frame.grid_rowconfigure(0, weight=1)
            list_frame.grid_columnconfigure(0, weight=1)

            columns = ("title", "status", "due")
            self.tree = ttk.Treeview(
                list_frame,
                columns=columns,
                show="headings",
                selectmode="browse",
            )
            self.tree.heading("title", text="Title")
            self.tree.heading("status", text="Status")
            self.tree.heading("due", text="Due")
            self.tree.column("title", width=340, anchor="w")
            self.tree.column("status", width=90, anchor="center")
            self.tree.column("due", width=150, anchor="center")
            self.tree.grid(row=0, column=0, sticky="nsew")

            scrollbar = ttk.Scrollbar(
                list_frame, orient="vertical", command=self.tree.yview
            )
            scrollbar.grid(row=0, column=1, sticky="ns")
            self.tree.configure(yscrollcommand=scrollbar.set)
            self.tree.bind("<<TreeviewSelect>>", self.on_task_select)

            form = ttk.LabelFrame(self.root, text="Task details")
            form.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
            form.grid_columnconfigure(1, weight=1)

            ttk.Label(form, text="Title").grid(row=0, column=0, sticky="w")
            ttk.Entry(form, textvariable=self.title_var).grid(
                row=0, column=1, sticky="ew", pady=4
            )

            ttk.Label(form, text="Due date (YYYY-MM-DD or YYYY-MM-DD HH:MM)").grid(
                row=1, column=0, columnspan=2, sticky="w", pady=(8, 0)
            )
            ttk.Entry(form, textvariable=self.due_var).grid(
                row=2, column=0, columnspan=2, sticky="ew", pady=4
            )

            ttk.Label(form, text="Description").grid(
                row=3, column=0, columnspan=2, sticky="w", pady=(8, 0)
            )
            self.desc_text = tk.Text(form, height=6, wrap="word")
            self.desc_text.grid(row=4, column=0, columnspan=2, sticky="nsew")
            form.grid_rowconfigure(4, weight=1)

            btn_frame = ttk.Frame(form)
            btn_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
            btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

            ttk.Button(btn_frame, text="Add task", command=self.add_task).grid(
                row=0, column=0, padx=4, sticky="ew"
            )
            ttk.Button(btn_frame, text="Update task", command=self.update_task).grid(
                row=0, column=1, padx=4, sticky="ew"
            )
            ttk.Button(btn_frame, text="Delete task", command=self.delete_task).grid(
                row=0, column=2, padx=4, sticky="ew"
            )

            actions = ttk.Frame(form)
            actions.grid(row=6, column=0, columnspan=2, sticky="ew")
            actions.grid_columnconfigure((0, 1, 2), weight=1)
            ttk.Button(
                actions, text="Mark complete", command=self.mark_complete
            ).grid(row=0, column=0, padx=4, pady=2, sticky="ew")
            ttk.Button(
                actions, text="Mark incomplete", command=self.mark_incomplete
            ).grid(row=0, column=1, padx=4, pady=2, sticky="ew")
            ttk.Button(
                actions, text="Purge completed", command=self.purge_completed
            ).grid(row=0, column=2, padx=4, pady=2, sticky="ew")

            ttk.Button(form, text="Clear form", command=self._clear_form).grid(
                row=7, column=0, columnspan=2, pady=(8, 0), sticky="ew"
            )

            ttk.Label(
                self.root,
                textvariable=self.status_var,
                anchor="w",
                foreground="#555555",
            ).grid(row=2, column=0, columnspan=2, sticky="ew", pady=(12, 0))

        def _clear_search(self) -> None:
            self.search_var.set("")
            self.refresh_task_list()

        def _clear_form(self) -> None:
            self.selected_task_id = None
            self.title_var.set("")
            self.due_var.set("")
            self.desc_text.delete("1.0", tk.END)
            self.tree.selection_remove(self.tree.selection())
            self.status_var.set("Form cleared.")

        def _filtered_tasks(self) -> list[TodoItem]:
            status = self.filter_var.get()
            if status not in {"pending", "completed"}:
                tasks = self.app.list_tasks("all")
            else:
                tasks = self.app.list_tasks(status)

            keyword = self.search_var.get().strip().lower()
            if keyword:
                tasks = [
                    task
                    for task in tasks
                    if keyword in task.title.lower()
                    or keyword in task.description.lower()
                ]
            return tasks

        def refresh_task_list(self) -> None:
            tasks = self._filtered_tasks()
            for item in self.tree.get_children():
                self.tree.delete(item)
            for task in tasks:
                due = task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else ""
                status_text = "Completed" if task.completed else "Pending"
                self.tree.insert(
                    "",
                    "end",
                    iid=str(task.task_id),
                    values=(task.title, status_text, due),
                )
            if self.selected_task_id and self.tree.exists(str(self.selected_task_id)):
                self.tree.selection_set(str(self.selected_task_id))
            else:
                self.selected_task_id = None
                self.tree.selection_remove(self.tree.selection())
            self.status_var.set(f"Showing {len(tasks)} task(s).")

        def _get_description_text(self) -> str:
            return self.desc_text.get("1.0", tk.END).strip()

        def on_task_select(self, _event=None) -> None:
            selection = self.tree.selection()
            if not selection:
                return
            task_id = int(selection[0])
            try:
                task = self.app.find_by_id(task_id)
            except LookupError:
                return
            self.selected_task_id = task_id
            self.title_var.set(task.title)
            self.due_var.set(
                task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else ""
            )
            self.desc_text.delete("1.0", tk.END)
            if task.description:
                self.desc_text.insert("1.0", task.description)
            self.status_var.set(f"Selected task #{task.task_id}.")

        def add_task(self) -> None:
            try:
                task = self.app.add_task(
                    self.title_var.get(),
                    self._get_description_text(),
                    self.due_var.get().strip() or None,
                )
            except ValueError as exc:
                messagebox.showerror("Cannot add task", str(exc))
                return
            self.status_var.set(f"Added task #{task.task_id}.")
            self._clear_form()
            self.refresh_task_list()

        def update_task(self) -> None:
            if self.selected_task_id is None:
                messagebox.showinfo("Select task", "Pick a task to update first.")
                return
            try:
                self.app.update_task(
                    self.selected_task_id,
                    title=self.title_var.get() or None,
                    description=self._get_description_text(),
                    due_date=self.due_var.get().strip() or None,
                )
            except (ValueError, LookupError) as exc:
                messagebox.showerror("Cannot update task", str(exc))
                return
            self.status_var.set("Task updated.")
            self.refresh_task_list()

        def delete_task(self) -> None:
            if self.selected_task_id is None:
                messagebox.showinfo("Select task", "Pick a task to delete first.")
                return
            if not messagebox.askyesno(
                "Delete task", "Are you sure you want to delete the selected task?"
            ):
                return
            try:
                self.app.delete_task(self.selected_task_id)
            except LookupError as exc:
                messagebox.showerror("Cannot delete task", str(exc))
                return
            self.status_var.set("Task deleted.")
            self._clear_form()
            self.refresh_task_list()

        def mark_complete(self) -> None:
            if self.selected_task_id is None:
                messagebox.showinfo("Select task", "Select a task to mark complete.")
                return
            try:
                self.app.mark_complete(self.selected_task_id)
            except LookupError as exc:
                messagebox.showerror("Cannot mark complete", str(exc))
                return
            self.status_var.set("Task marked complete.")
            self.refresh_task_list()

        def mark_incomplete(self) -> None:
            if self.selected_task_id is None:
                messagebox.showinfo("Select task", "Select a task to mark incomplete.")
                return
            try:
                self.app.mark_incomplete(self.selected_task_id)
            except LookupError as exc:
                messagebox.showerror("Cannot mark incomplete", str(exc))
                return
            self.status_var.set("Task marked incomplete.")
            self.refresh_task_list()

        def purge_completed(self) -> None:
            removed = self.app.purge_completed()
            self.status_var.set(f"Removed {removed} completed task(s).")
            if self.selected_task_id and not self.tree.exists(
                str(self.selected_task_id)
            ):
                self._clear_form()
            self.refresh_task_list()

    root = tk.Tk()
    TodoUI(root)
    root.mainloop()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple in-memory todo app.")
    parser.add_argument(
        "--mode",
        choices=("auto", "interactive", "demo", "ui"),
        default="auto",
        help="Select run mode: ui launches the Tkinter interface.",
    )
    parser.add_argument(
        "--storage",
        default=str(Path(__file__).resolve().parents[2] / "todo_data.json"),
        help="Path to persist tasks (use 'none' to disable persistence).",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    storage_path: Optional[Path]
    if args.storage.lower() == "none":
        storage_path = None
    else:
        storage_path = Path(args.storage).expanduser()

    if args.mode == "interactive":
        _main_loop(TodoApp(storage_path=storage_path))
    elif args.mode == "demo":
        _demo_run()
    elif args.mode == "ui":
        run_ui(storage_path)
    else:  # auto
        if sys.stdin.isatty():
            _main_loop(TodoApp(storage_path=storage_path))
        else:
            _demo_run()


__all__ = ["main", "run_ui", "_main_loop"]
