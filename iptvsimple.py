# -*- coding: utf-8 -*-
# Author: cache-sk
import os
import xbmcgui
import xbmcaddon

def configure_iptvsimple(m3u_path, xmltv_file):
    _self = xbmcaddon.Addon(id='plugin.video.sl')
    try:
        _pisc = xbmcaddon.Addon(id='pvr.iptvsimple')
    except:
        xbmcgui.Dialog().ok(_self.getAddonInfo('name'), _self.getLocalizedString(30392))
        return

    _playlist_generate = 'true' == _self.getSetting('playlist_generate')
    _epg_generate = 'true' == _self.getSetting('epg_generate')

    if not _playlist_generate and not _epg_generate:
        xbmcgui.Dialog().ok(_self.getAddonInfo('name'), _self.getLocalizedString(30393))
        return

    if not xbmcgui.Dialog().yesno(_self.getAddonInfo('name'), _self.getLocalizedString(30394)):
        return

    if m3u_path:
        path = os.path.join(_self.getSetting('playlist_folder'), _self.getSetting('playlist_file'))
        _pisc.setSetting('m3uPathType','0')
        _pisc.setSetting('m3uPath',path)
        _pisc.setSetting('startNum','1')

    if xmltv_file:
        path = os.path.join(_self.getSetting('epp_folder'), _self.getSetting('epg_file'))
        _pisc.setSetting('epgPath',path)
        _pisc.setSetting('epgPathType','0')
        _pisc.setSetting('epgTimeShift','0')
        _pisc.setSetting('epgTSOverride','false')
        _pisc.setSetting('logoPathType','1')
        _pisc.setSetting('logoBaseUrl','')
        _pisc.setSetting('logoFromEpg','2')

set_pisc()
