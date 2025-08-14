
def group_by_prefix(endpoints):
    """
    Automatically assign tags based on the first part of the URL path.
    Example: /users/... -> tag 'Users'
    """
    new_endpoints = []
    for (path, path_regex, method, callback) in endpoints:
        prefix = path.strip("/").split("/")[0] or "General"
        prefix_tag = prefix.capitalize()

        if not hasattr(callback, 'tags'):
            callback.tags = [prefix_tag]

        new_endpoints.append((path, path_regex, method, callback))
    return new_endpoints
