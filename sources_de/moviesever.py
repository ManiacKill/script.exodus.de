# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Viper2k4

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re, urllib, urlparse

from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['moviesever.com/']
        self.base_link = 'http://moviesever.com/'
        self.search_link = '/?s=%s'

        self.get_link = 'http://play.seriesever.net/me/moviesever.php'

    def movie(self, imdb, title, localtitle, year):
        try:
            url = self.__search(title, year)
            if not url and title != localtitle: url = self.__search(localtitle, year)
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []

        try:
            if url == None:
                return sources

            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            rels = client.parseDOM(r, 'nav', attrs={'class': 'player'})
            rels = client.parseDOM(rels, 'ul', attrs={'class': 'idTabs'})
            rels = client.parseDOM(rels, 'li')
            rels = [(client.parseDOM(i, 'a', attrs={'class': 'options'}, ret='href'), client.parseDOM(i, 'img', ret='src')) for i in rels]
            rels = [(i[0][0][1:], re.findall('\/flags\/(\w+)\.png$', i[1][0])) for i in rels if len(i[0]) > 0 and len(i[1]) > 0]
            rels = [i[0] for i in rels if len(i[1]) > 0 and i[1][0].lower() == 'de']

            r = [client.parseDOM(r, 'div', attrs={'id': i}) for i in rels]
            r = [(re.findall('link"?\s*:\s*"(.+?)"', i[0]), client.parseDOM(i, 'iframe', attrs={'class': '[^\'"]*metaframe[^\'"]*'}, ret='src')) for i in r]
            r = [i[0][0] if len(i[0]) > 0 else i[1][0] for i in r if len(i[0]) > 0 or len(i[1]) > 0]

            for i in r:
                try:
                    result = client.request(self.get_link, post=urllib.urlencode({'link': i}), referer=url)

                    result = re.findall('"?link"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?[^"]*"', result)

                    links = [(x[0], '4K') for x in result if int(x[1]) >= 2160]
                    links += [(x[0], '1440') for x in result if int(x[1]) >= 1440]
                    links += [(x[0], '1080p') for x in result if int(x[1]) >= 1080]
                    links += [(x[0], 'HD') for x in result if 720 <= int(x[1]) < 1080]
                    links += [(x[0], 'SD') for x in result if 480 <= int(x[1]) < 720]

                    for link, quality in links:
                        link = link.replace('\/', '/')
                        link = client.replaceHTMLCodes(link)

                        sources.append({'source': 'cdn', 'quality': quality, 'language': 'de', 'url': link, 'direct': True, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            return sources

    def resolve(self, url):
        return url

    def __search(self, title, year):
        try:
            query = self.search_link % (urllib.quote_plus(cleantitle.query(title)))
            query = urlparse.urljoin(self.base_link, query)

            t = cleantitle.get(title)
            y = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1), '0']

            r = client.request(query)

            r = client.parseDOM(r, 'div', attrs={'class': 'details'})
            r = [(client.parseDOM(i, 'div', attrs={'class': 'title'}), client.parseDOM(i, 'span', attrs={'class': 'year'})) for i in r]
            r = [(client.parseDOM(i[0][0], 'a', ret='href'), client.parseDOM(i[0][0], 'a'), i[1][0]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            r = [(i[0][0], i[1][0], i[2]) for i in r if len(i[0]) > 0 and len(i[1]) > 0]
            r = [i[0] for i in r if t == cleantitle.get(i[1]) and i[2] in y][0]

            url = re.findall('(?://.+?|)(/.+)', r)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return