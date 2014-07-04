class Bot(object):
    """
    Base class for a bot. An instance of a Bot class has to respond to
    the ``guess[1]`` function

    [1] ``guess`` will be called every time
    [2] ``get``
    """
    def guess(self, game):
        """
        Make a guess for given game
        """
        raise Exception("Not implemented!")
