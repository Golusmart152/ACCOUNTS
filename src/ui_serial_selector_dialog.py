import customtkinter as ctk
from tkinter import ttk, messagebox

class SerialSelectorDialog(ctk.CTkToplevel):
    def __init__(self, parent, item_name, available_serials, quantity_needed):
        super().__init__(parent)
        self.transient(parent)
        self.title(f"Select Serials for {item_name}")
        self.geometry("400x500")

        self.available_serials = available_serials # List of (id, serial_number)
        self.quantity_needed = quantity_needed
        self._selected_serial_ids = []

        self.label = ctk.CTkLabel(self, text=f"Select {quantity_needed} serial number(s):")
        self.label.pack(padx=20, pady=(20, 10))

        self.tree = ttk.Treeview(self, columns=("id", "serial"), show="headings", selectmode="extended")
        self.tree.heading("id", text="ID")
        self.tree.heading("serial", text="Serial Number")
        self.tree.column("id", width=50)
        self.tree.pack(padx=20, pady=5, fill="both", expand=True)

        for serial_id, serial_number in self.available_serials:
            self.tree.insert("", "end", values=(serial_id, serial_number))

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=(10, 20), fill="x")

        self.ok_button = ctk.CTkButton(button_frame, text="OK", command=self.on_ok)
        self.ok_button.pack(side="left", padx=20, expand=True)

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side="right", padx=20, expand=True)

        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.wait_window()

    def on_ok(self):
        selected_items = self.tree.selection()
        if len(selected_items) != self.quantity_needed:
            messagebox.showerror("Selection Error", f"You must select exactly {self.quantity_needed} serial number(s).", parent=self)
            return

        self._selected_serial_ids = [self.tree.item(item, "values")[0] for item in selected_items]
        self.destroy()

    def on_cancel(self):
        self._selected_serial_ids = []
        self.destroy()

    def get_selected_ids(self):
        return self._selected_serial_ids
