from abc import abstractmethod, ABCMeta


class Destination(metaclass=ABCMeta):
    '''
    A destination is a way to save a song. For example, adding a track
    to a playlist, downloading a file, or opening a web browser to a
    purchase URL.
    '''
    name = "Destination"
    
    @abstractmethod
    def __init__(self, config):
        '''
        Destinations' constructors will be passed their section of the
        configuration file. This is where credentials, api keys, playlist
        identifiers, folder paths, and so on can be stored.
        
        The `config` param functions like a dictionary.
        The keys are up to the destination implementation.
        '''
        pass
    
    @abstractmethod
    def save(self, track):
        '''
        Attempt to save a track. If saving is successful, no other destinations
        will be attempted.
        
        @param track A pylast track object
        @return (success, message)
            success: True iff saving was successful
            message: str describing what went right or wrong
                "Saved to dir/file.mp3"
                "Added to playlist 'New Music'"
                "Spotify search returned no results"
        '''
        pass