'''
This modules refer to
Petter Kraabøl's Twitch-Chat-Downloader
https://github.com/PetterKraabol/Twitch-Chat-Downloader
(MIT License)
'''


class Singleton(type):
    """
    Abstract class for singletons
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    def get_instance(cls, *args, **kwargs):
        cls.__call__(*args, **kwargs)
