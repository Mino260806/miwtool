class Logger:
    @classmethod
    def info(cls, msg: str, *args):
        print(msg.format(*args))

    @classmethod
    def warn(cls, msg: str, *args):
        print(msg.format(*args))
