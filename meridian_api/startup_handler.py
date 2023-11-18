class StartupHandler:
    instance = None

    def __init__(self):
        self.commands_executed = False

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = StartupHandler()
        return cls.instance

    def execute_commands(self):
        if not self.commands_executed:
            # Execute your commands here
            print("Executing start up commands...")

            # Set the flag to indicate that the commands have been executed
            self.commands_executed = True