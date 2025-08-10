import customtkinter as ctk
from tkinter import messagebox

class SerialEntryDialog(ctk.CTkToplevel):
    def __init__(self, parent, quantity):
        super().__init__(parent)
        self.transient(parent)
        self.title("Enter Serial Numbers")
        self.quantity = quantity
        self._serials = []
        self.entries = []

        # Center the dialog on the parent window
        parent_geo = parent.winfo_geometry()
        parent_x, parent_y, parent_width, parent_height = map(int, parent_geo.replace('x', '+').split('+'))
        dialog_width = 400
        dialog_height = 300
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")


        self.label = ctk.CTkLabel(self, text=f"Please enter {quantity} unique serial numbers:")
        self.label.pack(padx=20, pady=(20, 10))

        # Frame for scrollable entries
        self.scrollable_frame = ctk.CTkScrollableFrame(self, height=200)
        self.scrollable_frame.pack(padx=15, pady=5, fill="x", expand=True)

        for i in range(quantity):
            entry = ctk.CTkEntry(self.scrollable_frame, width=350)
            entry.pack(padx=10, pady=4)
            self.entries.append(entry)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=(10, 20), fill="x")

        self.ok_button = ctk.CTkButton(button_frame, text="OK", command=self.on_ok)
        self.ok_button.pack(side="left", padx=20, expand=True)

        self.cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.on_cancel)
        self.cancel_button.pack(side="right", padx=20, expand=True)

        self.grab_set() # Make the dialog modal
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.after(250, lambda: self.entries[0].focus()) # Set focus to the first entry
        self.wait_window() # Wait until the dialog is closed

    def on_ok(self):
        serials = [entry.get().strip() for entry in self.entries]

        # Validation
        if any(not sn for sn in serials):
            messagebox.showerror("Error", "All serial number fields must be filled.", parent=self)
            return

        if len(set(serials)) != len(serials):
            messagebox.showerror("Error", "All serial numbers must be unique within this entry.", parent=self)
            return

        self._serials = serials
        self.destroy()

    def on_cancel(self):
        self._serials = [] # Return empty list on cancel
        self.destroy()

    def get_serials(self):
        """Public method to get the result after the dialog is closed."""
        return self._serials
