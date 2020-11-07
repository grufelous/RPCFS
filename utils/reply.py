class Reply():
    def __init__(self, success: str, data: str='', message: str=''):
        self.success = success
        self.data = data
        self.message = message
