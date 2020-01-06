# -*- coding: utf-8 -*-
import xbmc

_lang = {}
_lang['en'] = {}
_lang['en']['playlist_created'] = 'M3U Playlist created'
_lang['en']['playlist_and_epg_created'] = 'M3U Playlist and EPG created'
_lang['en']['playlist_or_epg_not_created'] = 'M3U Playlist or EPG not created'
_lang['en']['live_tv'] = 'Live TV'
_lang['en']['archive'] = 'Archive'
_lang['en']['today'] = 'today'
_lang['en']['yesterday'] = 'yesterday'
_lang['en']['day_1'] = 'monday'
_lang['en']['day_2'] = 'tuesday'
_lang['en']['day_3'] = 'wednesday'
_lang['en']['day_4'] = 'thursday'
_lang['en']['day_5'] = 'friday'
_lang['en']['day_6'] = 'saturday'
_lang['en']['day_7'] = 'sunday'
_lang['en']['day_after'] = 'the day after'
_lang['en']['day_before'] = 'the day before'
_lang['en']['creating_playlist'] = 'Creating M3U Playlist'
_lang['en']['creating_epg'] = 'Creating EPG'
_lang['en']['iptv_not_installed'] = 'IPTV Simple Client add-on is not installed'
_lang['en']['iptv_configure'] = 'Change configuration of IPTV Simple Client add-on according {}'

_lang['sk'] = {}
_lang['sk']['playlist_created'] = 'M3U Playlist bol vytvorený'
_lang['sk']['playlist_and_epg_created'] = 'M3U Playlist a EPG boli vytvorené'
_lang['sk']['playlist_or_epg_not_created'] = 'M3U Playlist alebo EPG sa nepodarilo vytvoriť'
_lang['sk']['live_tv'] = 'Živé vysielanie'
_lang['sk']['archive'] = 'Archív'
_lang['sk']['today'] = 'dnes'
_lang['sk']['yesterday'] = 'včera'
_lang['sk']['day_1'] = 'pondelok'
_lang['sk']['day_2'] = 'utorok'
_lang['sk']['day_3'] = 'streda'
_lang['sk']['day_4'] = 'štvrtok'
_lang['sk']['day_5'] = 'piatok'
_lang['sk']['day_6'] = 'sobota'
_lang['sk']['day_7'] = 'nedeľa'
_lang['sk']['day_after'] = 'nasledujúci deň'
_lang['sk']['day_before'] = 'predošlý deň'
_lang['sk']['creating_playlist'] = 'Vytváram M3U Playlist'
_lang['sk']['creating_epg'] = 'Vytváram EPG'
_lang['sk']['iptv_not_installed'] = 'Doplnok IPTV Simple Client nie je nainštalovaný'
_lang['sk']['iptv_configure'] = 'Upraviť konfiguráciu doplnku IPTV Simple Client podľa {}'

_code = xbmc.getLanguage(xbmc.ISO_639_1)


def _(key):
    # type: (str) -> str
    code = _code if _code in _lang else 'en'
    return _lang[code][key] if key in _lang[code] else 'Unknown Translation: [%s] %s' % (code, key)
