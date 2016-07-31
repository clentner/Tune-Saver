from bs4 import BeautifulSoup
import requests
import webbrowser

from services.service import Service


class LastFmPurchase(Service):
    name = 'Last.fm Purchase link'
    
    def __init__(self, config):
        self.config = config
        
    def search(self, track):
        '''
        Checks the Last.fm track webpage for a purchase link.
        
        @param track A pylast track object
        @return The purchase URL and the price
        '''
        r = requests.get(track.get_url())
        soup = BeautifulSoup(r.text, "html.parser")
        buy_links = soup.find_all('a', attrs={'data-analytics-action': 'Buy|Direct'})
        if len(buy_links) == 0:
            return None
        return buy_links[0].get('href'), buy_links[0].get_text().strip()
    
    def save(self, track):
        '''
        Checks the Last.fm track webpage for a purchase link.
        
        @param track A pylast track object
        '''
        buy_link, price = self.search(track)
        if not buy_link:
            return (False, 'No buy link from Last.fm')
        if 'y' != input('Buy track for {}? y/n '.format(price)):
            return (False, 'Opted to not purchase track')
        webbrowser.open(buy_link)
        return (True, 'Purchase this track at {}'.format(buy_link))