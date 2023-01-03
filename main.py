import sys

from routes import routes

class Main:
    def __call__(self, args):
        if len(args) < 1: args = [""]

        command = args[0]

        controller = self._get_controller(command)
        
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
        Controller = next(filter(lambda route: route[0] == command, routes), None)[1]
        if Controller == None:
            print(f"Unrecognized command '{command}'")
            sys.exit(1)

        return Controller()

Main()(sys.argv[1:])