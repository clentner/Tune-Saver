from bs4 import BeautifulSoup
import re
import requests
from urllib.parse import urlparse
import webbrowser

from services.service import Service
from servicetrack import ServiceTrack


class LastFmPurchase(Service):
    name = 'Last.fm Purchase link'
    
    def __init__(self, config):
        self.config = config
        
    def search(self, track):
        '''
        Checks the Last.fm track webpage for a purchase link.
        
        @param track A pylast track object
        @return A list containing up to one ServiceTrack
        '''
        r = requests.get(track.get_url())
        soup = BeautifulSoup(r.text, "html.parser")
        buy_links = soup.find_all('a', attrs={'data-analytics-action': 'Buy|Direct'})
        if len(buy_links) == 0:
            return []
        buy_link = buy_links[0].get('href')
        price = buy_links[0].get_text().strip()
        try:
            price = re.search(r'(\$\d*\.\d+)', price).group(0)
        except AttributeError:
            pass
        st = ServiceTrack('Buy "{} - {}" from {} for {}'.format(
            track.artist.name,
            track.title,
            urlparse(buy_link).hostname,
            price))
        st.buy_link, st.price = buy_link, price
        return [st]
    
    def save(self, servicetrack):
        '''
        Opens the user's webbrowser to Last.fm's provided purchase link
        
        @param servicetrack A ServiceTrack object, generated from search()
        @return (success, message)
        '''
        webbrowser.open(servicetrack.buy_link)
        return (True, 'Purchase this track at {}'.format(servicetrack.buy_link))