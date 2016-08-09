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
        # Download the Last.fm webpage for this track.
        r = requests.get(track.get_url())
        # Parse out the purchase link tags, <a data-analytics-action="Buy|Direct">
        soup = BeautifulSoup(r.text, "html.parser")
        buy_links = soup.find_all('a', attrs={'data-analytics-action': 'Buy|Direct'})
        # Some tracks do not have this information.
        if len(buy_links) == 0:
            return []
        # Extrack the URL from the <a> tag
        buy_link = buy_links[0].get('href')
        # The price will be in the text of the tag. Strip surrounding whitespace.
        price = buy_links[0].get_text().strip()
        # Match out the price, to remove extraneous text.
        try:
            price = re.search(r'(\$\d*\.\d+)', price).group(0)
        except AttributeError:
            pass  # Better to have extra text than no price.
        # Prompt to be displayed to user
        st = ServiceTrack('Buy "{} - {}" from {} for {}'.format(
            track.artist.name,
            track.title,
            urlparse(buy_link).hostname,
            price))
        # Save the link to be opened if the user chooses this option.
        st.buy_link = buy_link
        return [st]
    
    def save(self, servicetrack):
        '''
        Opens the user's webbrowser to Last.fm's provided purchase link
        
        @param servicetrack A ServiceTrack object, generated from search()
        @return (success, message)
        '''
        webbrowser.open(servicetrack.buy_link)
        return (True, 'Purchase this track at {}'.format(servicetrack.buy_link))