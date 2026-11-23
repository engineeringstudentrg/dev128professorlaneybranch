"""
people_gui.py
Presentation Layer for the People Directory assignment.

This module builds the Tkinter interface and calls database_operations.py
for all data validation and database work. It does not contain SQL commands.

Academic integrity note: This project was prepared with AI assistance.
Review the code, understand each function, and follow your instructor's
disclosure requirements before submitting.
"""

import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

import database_operations as database


class PersonForm(tk.Toplevel):
    """Modal Add/Edit form containing all required fields and optional notes."""

    FIELD_LABELS = [
        ("first_name", "First name"),
        ("last_name", "Last name"),
        ("email", "Email address"),
        ("street", "Street address"),
        ("city", "City"),
        ("state", "State"),
        ("zipcode", "ZIP code"),
        ("job_title", "Job title"),
    ]

    def __init__(self, parent, title, person=None):
        """Build the form and wait for the user to Save or Cancel."""
        super().__init__(parent)
        self.parent = parent
        self.person = person or {}
        self.result = None
        self.title(title)
        self.configure(padx=22, pady=18)
        self.resizable(False, False)
        self.transient(parent)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        heading = ttk.Label(self, text=title, style="FormTitle.TLabel")
        heading.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

        hint = ttk.Label(
            self,
            text="Fields marked * are required. Notes are optional.",
            style="Muted.TLabel",
        )
        hint.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))

        self.inputs = {}
        for row, (key, label) in enumerate(self.FIELD_LABELS, start=2):
            ttk.Label(self, text=f"{label} *").grid(
                row=row, column=0, sticky="w", padx=(0, 18), pady=6
            )
            entry = ttk.Entry(self, width=38, font=("Arial", 11))
            entry.grid(row=row, column=1, sticky="ew", pady=6)
            entry.insert(0, self.person.get(key, "") or "")
            self.inputs[key] = entry

        notes_row = len(self.FIELD_LABELS) + 2
        ttk.Label(self, text="Notes").grid(
            row=notes_row, column=0, sticky="nw", padx=(0, 18), pady=6
        )
        self.notes_input = tk.Text(
            self, width=38, height=4, font=("Arial", 11),
            wrap="word", relief="solid", borderwidth=1
        )
        self.notes_input.grid(row=notes_row, column=1, sticky="ew", pady=6)
        self.notes_input.insert("1.0", self.person.get("notes", "") or "")

        buttons = ttk.Frame(self)
        buttons.grid(
            row=notes_row + 1, column=0, columnspan=2,
            sticky="e", pady=(16, 0)
        )
        ttk.Button(buttons, text="Cancel", command=self.cancel).pack(
            side="right", padx=(8, 0)
        )
        ttk.Button(
            buttons, text="Save", style="Accent.TButton", command=self.save
        ).pack(side="right")

        self.bind("<Escape>", lambda _event: self.cancel())
        self.bind("<Control-Return>", lambda _event: self.save())
        self.grab_set()
        self.inputs["first_name"].focus_set()
        self.update_idletasks()
        self.geometry(
            f"+{parent.winfo_rootx() + 80}+{parent.winfo_rooty() + 45}"
        )

    def save(self):
        """Collect form values and validate before returning them to the GUI."""
        data = {
            key: widget.get().strip()
            for key, widget in self.inputs.items()
        }
        data["notes"] = self.notes_input.get("1.0", "end-1c").strip()

        is_valid, message = database.validate_person_data(data)
        if not is_valid:
            messagebox.showerror("Please check the form", message, parent=self)
            # Focus the first required field that is missing.
            for key, label in database.REQUIRED_FIELDS.items():
                if not data.get(key, "").strip():
                    self.inputs[key].focus_set()
                    break
            return

        self.result = data
        self.destroy()

    def cancel(self):
        """Close the form without saving any changes."""
        self.result = None
        self.destroy()


class PeopleDirectory:
    """Main application window for listing and managing people records."""

    def __init__(self, root):
        """Initialize the database, configure the window, and load records."""
        self.root = root
        self.root.title("People Directory | Contact Manager")
        self.root.geometry("1120x690")
        self.root.minsize(900, 580)
        self.people = []

        self._configure_styles()
        database.create_database()
        self._build_interface()
        self.refresh_list()

    def _configure_styles(self):
        """Set consistent typography, spacing, and button styles."""
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("AppTitle.TLabel", font=("Arial", 23, "bold"))
        style.configure("Subtitle.TLabel", font=("Arial", 11))
        style.configure("Section.TLabel", font=("Arial", 13, "bold"))
        style.configure("FormTitle.TLabel", font=("Arial", 17, "bold"))
        style.configure("Muted.TLabel", font=("Arial", 10))
        style.configure("Treeview", font=("Arial", 11), rowheight=32)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("TButton", font=("Arial", 10), padding=(12, 8))
        style.configure("Accent.TButton", font=("Arial", 10, "bold"), padding=(14, 8))

    def _build_interface(self):
        """Create the menu, heading, people table, action buttons, and status."""
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="Refresh list", command=self.refresh_list)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

        outer = ttk.Frame(self.root, padding=(28, 22))
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 20))
        ttk.Label(header, text="People Directory", style="AppTitle.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="Manage contact details, addresses, and professional information.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        content = ttk.Frame(outer)
        content.pack(fill="both", expand=True)

        left = ttk.Frame(content)
        left.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="People", style="Section.TLabel").pack(
            anchor="w", pady=(0, 10)
        )

        columns = ("name", "email", "job_title", "city", "state")
        self.tree = ttk.Treeview(
            left, columns=columns, show="headings", selectmode="browse"
        )
        headings = {
            "name": ("Name", 190),
            "email": ("Email", 245),
            "job_title": ("Job title", 190),
            "city": ("City", 145),
            "state": ("State", 75),
        }
        for column, (label, width) in headings.items():
            self.tree.heading(column, text=label)
            self.tree.column(column, width=width, minwidth=70, anchor="w")

        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<Double-1>", lambda _event: self.view_person())

        side = ttk.Frame(content, padding=(22, 0, 0, 0))
        side.pack(side="right", fill="y")
        ttk.Label(side, text="Actions", style="Section.TLabel").pack(
            anchor="w", pady=(0, 10)
        )

        actions = [
            ("＋  Add person", self.add_person),
            ("View details", self.view_person),
            ("Edit person", self.edit_person),
            ("Delete person", self.delete_person),
            ("Refresh list", self.refresh_list),
        ]
        for label, command in actions:
            ttk.Button(side, text=label, command=command, width=19).pack(
                fill="x", pady=5
            )

        ttk.Separator(side, orient="horizontal").pack(fill="x", pady=14)
        ttk.Label(
            side,
            text="Tip: Double-click a row\n to view the full record.",
            style="Muted.TLabel",
            justify="left",
        ).pack(anchor="w")

        self.status = ttk.Label(
            outer, text="", style="Muted.TLabel", anchor="w"
        )
        self.status.pack(fill="x", pady=(16, 0))

    def _selected_person(self):
        """Return the selected person dictionary, or show a helpful prompt."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo(
                "Select a person", "Please select a person from the list first.",
                parent=self.root,
            )
            return None
        person_id = int(selection[0])
        person = database.get_person_by_id(person_id)
        if person is None:
            messagebox.showwarning(
                "Record not found",
                "This record may have been removed. The list will be refreshed.",
                parent=self.root,
            )
            self.refresh_list()
        return person

    def _open_person_form(self, title, person=None):
        """Open the modal form and return saved data, or None if cancelled."""
        form = PersonForm(self.root, title, person)
        self.root.wait_window(form)
        return form.result

    def add_person(self):
        """Create a person using validated form data and refresh the table."""
        data = self._open_person_form("Add a Person")
        if data is None:
            return
        try:
            database.add_person(data)
            self.refresh_list()
            messagebox.showinfo("Person added", "The person was added successfully.", parent=self.root)
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror("Unable to add person", str(error), parent=self.root)

    def view_person(self):
        """Display all fields for the selected person, including full address."""
        person = self._selected_person()
        if person is None:
            return

        details = (
            f"Name: {person['first_name']} {person['last_name']}\n"
            f"Email: {person['email']}\n"
            f"Street address: {person['street']}\n"
            f"City: {person['city']}\n"
            f"State: {person['state']}\n"
            f"ZIP code: {person['zipcode']}\n"
            f"Job title: {person['job_title']}\n"
            f"Notes: {person.get('notes') or '—'}"
        )
        messagebox.showinfo(
            f"{person['first_name']} {person['last_name']}", details,
            parent=self.root,
        )

    def edit_person(self):
        """Update the selected person's fields and reload the list after saving."""
        selected = self._selected_person()
        if selected is None:
            return
        data = self._open_person_form("Edit Person", selected)
        if data is None:
            return
        try:
            if database.update_person(selected["id"], data):
                self.refresh_list()
                messagebox.showinfo("Person updated", "Changes were saved successfully.", parent=self.root)
            else:
                messagebox.showwarning("Not found", "The selected record no longer exists.", parent=self.root)
                self.refresh_list()
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror("Unable to update person", str(error), parent=self.root)

    def delete_person(self):
        """Ask for confirmation, delete the selected person, and refresh the list."""
        person = self._selected_person()
        if person is None:
            return
        full_name = f"{person['first_name']} {person['last_name']}"
        confirmed = messagebox.askyesno(
            "Confirm deletion",
            f"Delete {full_name} from the directory? This cannot be undone.",
            parent=self.root,
        )
        if not confirmed:
            return
        try:
            if database.delete_person(person["id"]):
                self.refresh_list()
                messagebox.showinfo("Person deleted", f"{full_name} was deleted.", parent=self.root)
            else:
                messagebox.showwarning("Not found", "The record was already deleted.", parent=self.root)
                self.refresh_list()
        except sqlite3.Error as error:
            messagebox.showerror("Unable to delete person", str(error), parent=self.root)

    def refresh_list(self):
        """Reload all people from SQLite and display their key details."""
        self.people = database.get_all_people()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for person in self.people:
            full_name = f"{person['first_name']} {person['last_name']}"
            self.tree.insert(
                "", "end", iid=str(person["id"]),
                values=(
                    full_name,
                    person["email"],
                    person["job_title"],
                    person["city"],
                    person["state"],
                ),
            )
        count = len(self.people)
        self.status.config(
            text=f"{count} {'person' if count == 1 else 'people'} in the directory"
        )


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = PeopleDirectory(root)
        root.mainloop()
    except tk.TclError as error:
        print(
            "The People Directory requires a desktop environment with Tkinter "
            "window support. Please run it locally rather than in a headless compiler."
        )
        print(f"Tkinter details: {error}")
