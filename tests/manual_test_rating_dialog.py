import customtkinter as ctk
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from moval.views.rating_dialog import VentanaValoracion

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("400x300")
        self.title("Main Window Test")

        self.btn = ctk.CTkButton(self, text="Open Rating Dialog", command=self.open_dialog)
        self.btn.pack(pady=50)

        self.label = ctk.CTkLabel(self, text="No rating yet")
        self.label.pack()

    def open_dialog(self):
        VentanaValoracion(self, callback=self.on_rating_received)

    def on_rating_received(self, rating, comment):
        print(f"Rating: {rating}, Comment: {comment}")
        self.label.configure(text=f"Rated: {rating} stars\nComment: {comment}")

if __name__ == "__main__":
    app = App()
    app.mainloop()

