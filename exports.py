# -*- coding: utf-8 -*-
import io
try:
    from typing import List, Dict, Callable
except:
    pass

from iptv.client import Channel, Programme

try:
    # Python 3.x
    from urllib.parse import urlencode as comp_urlencode
except ImportError:
    # Python 2.5+
    from urllib import urlencode as comp_urlencode

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}


def html_escape(text):
    return "".join(html_escape_table.get(c, c) for c in text)


def build_url(channel, catchup):
    pass


def create_m3u(file_name, channels, url_callback=build_url):
    # type: (str, List[Channel], Callable[[Channel, bool], str]) -> None
    with io.open(file_name, 'w', encoding='utf8') as file:
        file.write(u'#EXTM3U\n')

        for c in channels:
            live_url = url_callback(c, False)
            if live_url:
                file.write(u'#EXTINF:-1')
                file.write(u' tvg-id="%s"' % c.id)
                if c.logo:
                    file.write(u' tvg-logo="%s"' % c.logo)

                catchup_url = url_callback(c, True)
                if catchup_url and c.archive_days > 0:
                    file.write(u' catchup-days="%d" catchup-source="%s"' % (c.archive_days, catchup_url))

                file.write(u',%s\n' % c.name)
                file.write(u'%s\n' % live_url)


def create_epg(file_name, epg):
    # type: (str, Dict[str, List[Programme]]) -> None
    with io.open(file_name, 'w', encoding='utf8') as file:
        file.write(u'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        file.write(u'<tv>\n')

        for channel_id in epg:
            file.write(u'<channel id="%s">\n' % channel_id)
            # file.write(u'<display-name>%s</display-name>\n' % c['title'])
            file.write(u'</channel>\n')

        for channel_id in epg:
            for p in epg[channel_id]:
                file.write(u'<programme channel="%s" start="%s" stop="%s">\n' % (
                    channel_id, p.start_time.strftime('%Y%m%d%H%M%S'), p.end_time.strftime('%Y%m%d%H%M%S')))
                if p.title:
                    file.write(u'<title>%s</title>\n' % html_escape(p.title))
                if p.description:
                    file.write(u'<desc>%s</desc>\n' % html_escape(p.description))
                if p.cover:
                    file.write(u'<icon src="%s"/>\n' % html_escape(p.cover))
                if p.genres:
                    file.write('<category>%s</category>\n' % ', '.join(p.genres))
                if p.actors or p.directors or p.writers or p.producers:
                    file.write(u'<credits>\n')
                    for actor in p.actors:
                        file.write(u'<actor>%s</actor>\n' % html_escape(actor))
                    for director in p.directors:
                        file.write(u'<director>%s</director>\n' % html_escape(director))
                    for writer in p.writers:
                        file.write(u'<writer>%s</writer>\n' % html_escape(writer))
                    for producer in p.producers:
                        file.write(u'<producer>%s</producer>\n' % html_escape(producer))
                    file.write(u'</credits>\n')
                if p.seasonNo and p.episodeNo:
                    file.write(u'<episode-num system="xmltv_ns">%d.%d.</episode-num>\n' %
                               (p.seasonNo - 1, p.episodeNo - 1))
                file.write(u'</programme>\n')
        file.write(u'</tv>\n')
