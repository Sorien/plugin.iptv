# -*- coding: utf-8 -*-
import datetime
import time
import iptv.exports
import xbmc
import xbmcgui

try:
    from typing import List, Dict, Callable
except:
    pass

from iptv.addon import IPTVAddon
from iptv.lang import _
from iptv.logger import log
from iptv.client import Channel, Programme, IPTVException, UserNotDefinedException, NetConnectionError


class PlaylistNotCreated(IPTVException):
    pass


class EpgNotCreated(IPTVException):
    pass


class IPTVUpdateService(xbmc.Monitor):

    def __init__(self):
        # type: () -> None
        self.updating = False
        self.pd = None
        xbmc.Monitor.__init__(self)
        log('service started')
        self.addon = self.create_addon()
        ts = self.addon.getSetting('__next_update')
        self._next_update = datetime.datetime.now() if ts == '' else datetime.datetime.fromtimestamp(float(ts))

    def __del__(self):
        log('service destroyed')

    def create_addon(self):
        # type: () -> IPTVAddon
        raise NotImplementedError("Should have implemented this")

    def notify(self, text, error=False):
        icon = 'DefaultIconError.png' if error else ''
        try:
            text = text.encode("utf-8") if type(text) is unicode else text
            xbmc.executebuiltin('Notification("%s","%s",5000,%s)' %
                                (self.addon.getAddonInfo('name').encode("utf-8"), text, icon))
        except NameError:
            xbmc.executebuiltin('Notification("%s","%s",5000,%s)' % (self.addon.getAddonInfo('name'), text, icon))

    def onSettingsChanged(self):
        if self.updating:
            return

        self.updating = True
        try:
            self.addon = self.create_addon()  # refresh for updated settings!
            if not self.abortRequested():
                try:
                    res = self._update(self.notification_process)
                    log(res)
                    if res == 1:
                        self.notify(_('playlist_created'), False)
                    if res == 2:
                        self.notify(_('playlist_and_epg_created'), False)
                except Exception as e:
                    log(str(e))
                    self.notify(_('playlist_or_epg_not_created'), True)
        finally:
            self.updating = False

    def _schedule_next(self, seconds):
        dt = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        log('Next update %s' % dt)
        self._next_update = dt

    def fetch_channels(self, progress):
        # type: (Callable[[None], int] or None) -> List[Channel]
        raise NotImplementedError("Should have implemented this")

    def fetch_epg(self, channels, progress):
        # type: (List[Channel], Callable[[None], int] or None) -> Dict[str, List[Programme]]
        raise NotImplementedError("Should have implemented this")

    def playlist_path(self):
        # type: () -> str
        raise NotImplementedError("Should have implemented this")

    def epg_path(self):
        # type: () -> str
        raise NotImplementedError("Should have implemented this")

    def make_url(self, channel, is_catchup):
        # type: (Channel, bool) -> str
        if not is_catchup:
            return self.addon.url_for(self.addon.play_channel_route, channel.id)
        return self.addon.url_for(self.addon.play_programme_by_time_route, channel.id, '${start}', '${stop}')

    def prepare_update(self):
        pass

    def notification_process(self, text, percent):
        if self.pd is None:
            if percent == 100:
                return
            self.pd = xbmcgui.DialogProgressBG()
            self.pd.create(self.addon.getAddonInfo('name'), text)

        self.pd.update(percent, self.addon.getAddonInfo('name'), text)

        if percent == 100:
            time.sleep(1)
            self.pd.close()
            self.pd = None

    def dummy_notification_progress(self, text, percent):
        pass

    def _update(self, callback=None):
        # type: (Callable[[str, int], None] or None) -> None or int
        if callback is None:
            callback = self.dummy_notification_progress

        result = None

        _playlist_path = self.playlist_path()
        _epg_path = self.epg_path()

        if not _playlist_path or (not (_playlist_path or _epg_path)):
            return result

        self.prepare_update()

        callback(_('updating_playlist'), 0)

        channels = self.fetch_channels(lambda percent: callback(_('updating_playlist'), percent // 2))

        try:
            log('Updating playlist [%d channels]' % len(channels))
            iptv.exports.create_m3u(_playlist_path, channels, self.make_url)

            result = 1
        except IOError as e:
            log(str(e))
            raise PlaylistNotCreated()

        if _epg_path:
            try:
                log('Updating Epg')

                callback(_('updating_epg'), 50)

                epg = self.fetch_epg(channels, lambda percent: callback(_('updating_epg'), 50 + (percent // 2)))
                iptv.exports.create_epg(_epg_path, epg)

                callback(_('updating_epg'), 100)

                result = 2
            except IOError as e:
                log(str(e))
                raise EpgNotCreated()

        return result

    def tick(self):
        if datetime.datetime.now() > self._next_update:
            try:
                self._schedule_next(12 * 60 * 60)
                self._update()
            except UserNotDefinedException:
                pass
            except NetConnectionError:
                self._schedule_next(60)
                log('Can''t update, no internet connection')
                pass
            except Exception as e:
                log(str(e))
                self.notify(_('playlist_or_epg_not_created'), True)

    def save(self):
        log('Saving next update %s' % self._next_update)
        self.addon.setSetting('__next_update', str(time.mktime(self._next_update.timetuple())))

    def run(self):
        while not self.abortRequested():
            if self.waitForAbort(10):
                self.save()
                break
            self.tick()
