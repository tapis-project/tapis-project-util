def label_deployment(project, service):
    return f"tp-{project.name}-{service.name}-{service.version}"

def get_name_version(name):
    parts = name.split(":")
    return (parts[0], None) if len(parts) < 2 else (parts[0], parts[1])