import customtkinter as ctk

class CTkCardWidget(ctk.CTkFrame):
    """Widget personalizado tipo tarjeta."""
    
    def __init__(self, master, title="Card", content="", **kwargs):
        super().__init__(master, **kwargs)
        
        self.title_text = title
        self.content_text = content
        
        # Configurar grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Título
        self.title_label = ctk.CTkLabel(
            self, text=title, font=("Arial", 14, "bold"),
            text_color="white", fg_color="transparent"
        )
        self.title_label.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        # Contenido
        self.content_label = ctk.CTkLabel(
            self, text=content, font=("Arial", 11),
            text_color="gray80", fg_color="transparent", wraplength=250
        )
        self.content_label.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
    
    def cget(self, key):
        if key == "title":
            return self.title_text
        elif key == "content":
            return self.content_text
        return super().cget(key)
    
    def configure(self, **kwargs):
        if "title" in kwargs:
            self.title_text = kwargs.pop("title")
            self.title_label.configure(text=self.title_text)
        if "content" in kwargs:
            self.content_text = kwargs.pop("content")
            self.content_label.configure(text=self.content_text)
        super().configure(**kwargs)