def enable_resizable_highlight(canvas, widget, left_sidebar, color="blue"):
    """Dibuja un remarco alrededor del widget en un canvas para remarcarlo y permitir manipulación."""

    def draw_remark():
        """Dibuja el remarco alrededor del widget."""
        x = widget.winfo_x()
        y = widget.winfo_y()
        width = widget.winfo_width()
        height = widget.winfo_height()

        if getattr(widget, "_highlight_id", None):
            remove_remark()

        widget._highlight_id = canvas.create_rectangle(
            x - 2, y - 2, x + width + 2, y + height + 2,
            outline=color, width=2, tags="highlight"
        )

        create_resize_handles(x, y, width, height)

    def create_resize_handles(x, y, width, height):
        """Crea y posiciona las manijas de redimensionamiento en las esquinas."""
        size = 6
        corners = [
            (x - size, y - size),  # Esquina superior izquierda
            (x + width - size, y - size),  # Esquina superior derecha
            (x - size, y + height - size),  # Esquina inferior izquierda
            (x + width - size, y + height - size)  # Esquina inferior derecha
        ]

        if not hasattr(widget, "_resize_handles") or not widget._resize_handles:
            widget._resize_handles = []

            for i in range(4):
                handle_id = canvas.create_rectangle(
                    0, 0, size, size,
                    fill="gray", outline="black", tags="resize_handle"
                )
                widget._resize_handles.append(handle_id)
                canvas.tag_bind(handle_id, "<B1-Motion>", lambda e, idx=i: resize_widget(e, idx))

        if len(widget._resize_handles) < 4:
            return

        for i, (hx, hy) in enumerate(corners):
            canvas.coords(widget._resize_handles[i], hx, hy, hx + size, hy + size)

    def resize_widget(event, handle_index):
        """Redimensiona el widget arrastrando una de las manijas."""
        x = event.x
        y = event.y

        rect_coords = canvas.coords(widget._highlight_id)
        rect_x1, rect_y1, rect_x2, rect_y2 = rect_coords

        if handle_index == 0:  # Esquina superior izquierda
            rect_x1 = x
            rect_y1 = y
        elif handle_index == 1:  # Esquina superior derecha
            rect_x2 = x
            rect_y1 = y
        elif handle_index == 2:  # Esquina inferior izquierda
            rect_x1 = x
            rect_y2 = y
        elif handle_index == 3:  # Esquina inferior derecha
            rect_x2 = x
            rect_y2 = y

        new_width = max(10, rect_x2 - rect_x1 - 4)
        new_height = max(10, rect_y2 - rect_y1 - 4)

        canvas.coords(widget._highlight_id, rect_x1, rect_y1, rect_x2, rect_y2)

        widget.place(x=rect_x1 + 2, y=rect_y1 + 2)

        left_sidebar.update_weights(new_width, new_height)
        left_sidebar.update_positions(x=rect_x1 + 2, y=rect_y1 + 2)

        if hasattr(widget, "_set_dimensions"):
            widget._set_dimensions(new_width, new_height)

        create_resize_handles(rect_x1, rect_y1, new_width, new_height)

    def remove_remark(event=None):
        """Elimina el remarco del widget."""
        if getattr(widget, "_highlight_id", None):
            canvas.delete(widget._highlight_id)
            widget._highlight_id = None

        if hasattr(widget, "_resize_handles"):
            for handle_id in widget._resize_handles:
                canvas.delete(handle_id)
            widget._resize_handles = []  # Vacia la lista para evitar errores

    def toggle_remark(event):
        """Activa o desactiva el remarco según el estado del widget."""
        if getattr(widget, "_highlight_id", None):
            remove_remark()
        else:
            draw_remark()

    widget.bind("<Button-3>", toggle_remark)
