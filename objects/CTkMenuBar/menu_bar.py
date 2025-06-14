"""
Customtkinter Menu Bar
Author: Akash Bora
"""

import customtkinter

class CTkMenuBar(customtkinter.CTkFrame):
        
    def __init__(
        self,
        master,
        bg_color = ["white","black"],
        height: int = 25,
        width: int = 10,
        padx: int = 5,
        pady: int = 2,
        **kwargs):

        if master.winfo_name().startswith("!ctkframe"):
            bg_corners = ["", "", bg_color, bg_color]
            corner = master.cget("corner_radius")
        else:
            bg_corners = ["", "", "", ""]
            corner = 0
            
        super().__init__(master, fg_color=bg_color, corner_radius=corner, height=height, background_corner_colors=bg_corners, **kwargs)
        self.height = height
        self.width = width
        self.after(10)
        self.num = 0
        self.menu = []
        self.padx = padx
        self.pady = pady

        super().pack(anchor="n", fill="x")

    def add_cascade(self, text=None, postcommand=None, **kwargs):

        fg_color = kwargs.pop("fg_color") if "fg_color" in kwargs else "transparent"
        if "text_color" not in kwargs:
            text_color = customtkinter.ThemeManager.theme["CTkLabel"]["text_color"]
        else:
            text_color = kwargs.pop("text_color")
            
        anchor = "w" if "anchor" not in kwargs else kwargs.pop("anchor")
        if text is None:
            text = f"Menu {self.num+1}"

        self.menu_button = customtkinter.CTkButton(self, text=text, fg_color=fg_color,
                                                   text_color=text_color, width=self.width,
                                                   height=self.height, anchor=anchor, **kwargs)
        self.menu_button.grid(row=0, column=self.num, padx=(self.padx,0), pady=self.pady)

        if postcommand:
            self.menu_button.bind("<Button-1>", lambda event: postcommand(), add="+")

        self.num += 1

        return self.menu_button
        
    def configure(self, **kwargs):
        if "bg_color" in kwargs:
           super().configure(fg_color=kwargs.pop("bg_color"))
        super().configure(**kwargs)
        
    def remove_button(self, text: str) -> bool:
        """Remove a button from the menu bar by its text
    
        Args:
            text (str): Text of the button to remove
            
        Returns:
            bool: True if button was found and removed, False otherwise
        """
        for button in self.winfo_children():
            if isinstance(button, customtkinter.CTkButton) and button.cget("text") == text:
                button.destroy()
                self.num -= 1
                # Reposition remaining buttons
                for i, remaining_button in enumerate(self.winfo_children()):
                    remaining_button.grid(row=0, column=i, padx=(self.padx,0), pady=self.pady)
                return True
        return False

    def change_button_text(self, old_text: str, new_text: str) -> bool:
        """Change the text of a button in the menu bar
    
        Args:
            old_text (str): Current text of the button
            new_text (str): New text to set
            
        Returns:
            bool: True if button was found and modified, False otherwise
        """
        for button in self.winfo_children():
            if isinstance(button, customtkinter.CTkButton) and button.cget("text") == old_text:
                button.configure(text=new_text)
                return True
        return False
