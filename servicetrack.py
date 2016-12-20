class ServiceTrack():
    '''
    A potential source for a specific track, which has yet to be saved.
    
    For example, a download URL with accompanying website credentials, or the
    ID of a song on a streaming service.
    
    A ServiceTrack must:
    - Have prompt text, e.g. 'Buy this track for $1.29' or 'Save this track to playlist'
    This will be displayed to the user.
    - Be accepted by the save() method of the service from which it was generated
    
    A ServiceTrack may also include:
    - Any private implementation data, e.g. URL or UID
    '''
    
    def __init__(self, service, prompt):
        '''
        @param service the Service which accepts this track for save()ing
        @param prompt The text displayed to the user. Should take the form of an action sentence,
        e.g. 'Buy "Freebird" for $1.29' or 'Save "Too Close" to playlist'.
        Do include the title and/or artist of the track, if available.
        Do not use a question, e.g. "Do you want to favorite this track?"
        Do not include the name of the service.
        '''
        self.service = service
        self.prompt = prompt