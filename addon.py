# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys
import xbmcaddon
import xbmcgui
import xbmcplugin
import routing

try:
    from typing import Callable, List, Dict
except:
    pass

from datetime import datetime, timedelta
from iptv.lang import _
from iptv.client import StreamInfo, IPTVClient, Channel, Programme


class IPTVAddon(xbmcaddon.Addon):
    _handle = int(sys.argv[1]) if len(sys.argv) > 1 else -1

    def __init__(self):
        xbmcaddon.Addon.__init__(self)
        self.client = self.create_client()
        self._router = routing.Plugin()
        self.register_routes()

    def register_routes(self):
        self._router.route("/")(self.index_route)
        self._router.route("/play-channel/<channel_id>")(self.play_channel_route)
        self._router.route("/play-programme/<programme_id>")(self.play_programme_route)
        self._router.route("/play-programme-catchup/<channel_id>-<start>-<stop>")(self.play_programme_by_time_route)
        self._router.route('/channels')(self.channels_route)
        self._router.route('/archive')(self.archive_route)
        self._router.route('/archive/<channel_id>-<channel_name>')(self.archive_days_route)
        self._router.route('/archive/<channel_id>-<channel_name>/<day>')(self.archive_programmes_route)

    def create_client(self):
        # type: () -> IPTVClient
        raise NotImplementedError("Should have implemented this")

    def run(self, args):
        self._router.run(args)

    def url_for(self, func, *args, **kwargs):
        return self._router.url_for(func, *args, **kwargs)

    def channels(self):
        # type: () -> List[Channel]
        return self.client.channels()

    def epg(self, channels, from_date, to_date):
        # type: (List[str],datetime,datetime) -> Dict[str, List[Programme]]
        return self.client.epg(channels, from_date, to_date)

    def channel_stream_info(self, channel_id):
        # type: (str) -> StreamInfo
        return self.client.channel_stream_info(channel_id)

    def programme_stream_info(self, programme_id):
        # type: (str) -> StreamInfo
        return self.client.programme_stream_info(programme_id)

    def _play(self, stream_info):
        # type: (StreamInfo) -> None
        if not stream_info:
            xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())
            return

        if stream_info.drm == 'widevine':
            import inputstreamhelper
            is_helper = inputstreamhelper.Helper(stream_info.protocol, drm=stream_info.drm)
            if is_helper.check_inputstream():
                item = xbmcgui.ListItem(path=stream_info.url)
                item.setProperty('inputstreamaddon', is_helper.inputstream_addon)
                item.setProperty('inputstream.adaptive.manifest_type', stream_info.protocol)
                item.setProperty('inputstream.adaptive.license_type', stream_info.drm)
                item.setProperty('inputstream.adaptive.license_key', stream_info.key)
                if stream_info.max_bandwidth:
                    item.setProperty('inputstream.adaptive.max_bandwidth', stream_info.max_bandwidth)
                if stream_info.user_agent:
                    item.setProperty('inputstream.adaptive.stream_headers', 'User-Agent=' + stream_info.user_agent)
                xbmcplugin.setResolvedUrl(self._handle, True, item)
                return

        if stream_info.drm == '':
            user_agent = ('|' + stream_info.user_agent) if stream_info.user_agent else ''
            item = xbmcgui.ListItem(path=stream_info.url + user_agent)
            xbmcplugin.setResolvedUrl(self._handle, True, item)
            return

        xbmcplugin.setResolvedUrl(self._handle, False, xbmcgui.ListItem())

    def play_channel_route(self, channel_id):
        self._play(self.channel_stream_info(channel_id))

    def play_programme_route(self, programme_id):
        self._play(self.programme_stream_info(programme_id))

    def play_programme_by_time_route(self, channel_id, start, stop):
        epg = self.epg([channel_id], start, stop)
        for program in epg[channel_id]:
            if start <= program.start_time and program.end_time <= stop:
                self.play_programme_route(program.id)

    def add_index_directory_items(self):
        xbmcplugin.addDirectoryItem(self._handle, self.url_for(self.channels_route), xbmcgui.ListItem(label=_('live_tv')), True)
        xbmcplugin.addDirectoryItem(self._handle, self.url_for(self.archive_route), xbmcgui.ListItem(label=_('archive')), True)

    def index_route(self):
        xbmcplugin.setPluginCategory(self._handle, '')
        xbmcplugin.setContent(self._handle, 'videos')

        self.add_index_directory_items()

        xbmcplugin.endOfDirectory(self._handle)

    def channels_route(self):
        channels = self.channels()
        xbmcplugin.setPluginCategory(self._handle, _('live_tv'))
        for channel in channels:
            list_item = xbmcgui.ListItem(label=channel.name)
            list_item.setInfo('video', {'title': channel.name})
            list_item.setArt({'thumb': channel.logo})
            list_item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(self._handle, self.url_for(self.play_channel_route, channel.id), list_item, False)
        xbmcplugin.endOfDirectory(self._handle)

    def archive_route(self):
        channels = self.channels()
        xbmcplugin.setPluginCategory(self._handle, _('archive'))
        for channel in channels:
            if channel.archive_days > 0:
                list_item = xbmcgui.ListItem(label=channel.name)
                list_item.setInfo('video', {'title': channel.name})
                list_item.setArt({'thumb': channel.logo})
                xbmcplugin.addDirectoryItem(self._handle, self.url_for(self.archive_days_route, channel.id, channel.name), list_item, True)
        xbmcplugin.endOfDirectory(self._handle)

    def archive_days_route(self, channel_id, channel_name):
        now = datetime.now()
        xbmcplugin.setPluginCategory(self._handle, 'Replay' + ' / ' + channel_name)
        for day in range(0, self.client.archive_days() + 1):
            d = now - timedelta(days=day)
            title = _('today') if day == 0 else _('yesterday') if day == 1 else d.strftime('%d. %m.')
            list_item = xbmcgui.ListItem(label=_('day_%d' % (d.weekday() + 1)) + ', ' + title)
            list_item.setArt({'icon': 'DefaultAddonPVRClient.png'})
            url = self.url_for(self.archive_programmes_route, channel_id, channel_name, d.strftime("%m-%d-%Y"))
            xbmcplugin.addDirectoryItem(self._handle, url, list_item, True)
        xbmcplugin.endOfDirectory(self._handle)

    @staticmethod
    def _strptime(date_string, format):
        # https://forum.kodi.tv/showthread.php?tid=112916 it's insane !!!
        try:
            return datetime.strptime(date_string, format)
        except TypeError:
            import time as ptime
            return datetime(*(ptime.strptime(date_string, format)[0:6]))

    def archive_programmes_route(self, channel_id, channel_name, day):
        day = self._strptime(day, '%m-%d-%Y')
        next_day = day + timedelta(days=1)
        prev_day = day + timedelta(days=-1)

        epg = self.epg([channel_id], day, day)

        xbmcplugin.setPluginCategory(self._handle, _('archive') + ' / ' + channel_name)

        if day > datetime.today() - timedelta(days=self.client.archive_days()):
            list_item = xbmcgui.ListItem(label=_('day_before'))
            list_item.setArt({'icon': 'DefaultVideoPlaylists.png'})
            url = self.url_for(self.archive_programmes_route, channel_id, channel_name, prev_day.strftime("%m-%d-%Y"))
            xbmcplugin.addDirectoryItem(self._handle, url, list_item, True)

        if epg:
            for programme in epg[channel_id]:
                if programme.is_replyable:
                    title = programme.start_time.strftime('%H:%M')
                    title = title + ' - ' + programme.title
                    list_item = xbmcgui.ListItem(label=title)
                    list_item.setInfo('video', {
                        'title': programme.title,
                        'plot': programme.description,
                        'duration': programme.duration
                    })
                    if programme.cover:
                        list_item.setArt({'thumb': programme.cover, 'icon': programme.cover})

                    url = self.url_for(self.play_programme_route, programme.id)
                    list_item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(self._handle, url, list_item, False)

        if day.date() < datetime.today().date():
            list_item = xbmcgui.ListItem(label=_('day_after'))
            list_item.setArt({'icon': 'DefaultVideoPlaylists.png'})
            url = self.url_for(self.archive_programmes_route, channel_id, channel_name, next_day.strftime("%m-%d-%Y"))
            xbmcplugin.addDirectoryItem(self._handle, url, list_item, True)

        xbmcplugin.endOfDirectory(self._handle)
