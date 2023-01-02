import sys

from routes import routes
from controllers.index import Index


class Main:
    def __call__(self, args):
        if len(args) < 1: args = [""]

        command = args[0]

        controller = self._get_controller(command)
        # Insert 'index' as the command if the controller returned is Index
        if type(controller) == Index:
            args.insert(0, "index")
        
        action_name = args[1] if len(args) > 1 else "index"
        action_args = args[2:]
        action = getattr(controller, action_name, None)
        if action == None:
            print(f"Unrecognized argument '{action_name}' for command '{command}'")
            sys.exit(1)

        try:
            action(*action_args)
        except Exception as e:
            print(e)
            sys.exit(1)

    def _get_controller(self, command):
        route = next(filter(lambda route: route[0] == command, routes), None)

        # Fallback to the index controller
        if route == None:
            route = next(filter(lambda route: route[0] == "index", routes), None)

        return route[1]()


Main()(sys.argv[1:])

