def validate_input(value:any):
    """Update the treeview in the right sidebar.

    This method triggers an update of the treeview widget within the right sidebar.
    It calls the `update_treeview` method of the `right_sidebar` object.

    Args:
        self: The current instance of the class.

    Returns:
        None
    """

    return bool(value == "" or (value.isdigit() and 0 <= int(value) <= 1000))