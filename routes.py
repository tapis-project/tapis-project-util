from controllers import System, Service, Project, Clean


routes = [
    ("system", System),
    ("service", Service),
    ("project", Project),
    ("clean", Clean)
]