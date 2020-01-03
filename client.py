# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime

try:
    from typing import List, Dict
except:
    pass


class Base:
    def __repr__(self):
        return str(self.__dict__)


class Channel(Base):
    def __init__(self):
        # channel Unique Id
        self.id = ''  # type: str
        # channel name
        self.name = ''
        # channel icon absolute url
        self.logo = ''
        # marks channel as pin protected
        self.is_pin_protected = False
        # if not 0 channel supports archive/catchup/replay
        self.archive_days = 0
        # channel metadata
        self.metadata = {}  # type: Dict[str, int]


class StreamInfo(Base):
    def __init__(self):
        self.protocol = ''
        self.url = ''
        self.drm = ''
        self.key = ''
        self.max_bandwidth = None


class Programme(Base):
    def __init__(self):
        self.id = ''  # type: str
        # Programme Start Time in UTC
        self.start_time = None  # type: datetime or None
        # Programme End Time in UTC
        self.end_time = None # type: datetime or None
        self.title = ''
        self.description = ''
        self.cover = ''
        self.duration = 0
        self.genres = []  # type: List[str]
        self.actors = []  # type: List[str]
        self.directors = []  # type: List[str]
        self.writers = []  # type: List[str]
        self.producers = []  # type: List[str]
        self.seasonNo = None
        self.episodeNo = None

        self.is_replyable = False
        # programme metadata
        self.metadata = {}  # type: Dict[str, int]


class IPTVException(Exception):
    pass


class UserNotDefinedException(IPTVException):
    pass


class UserInvalidException(IPTVException):
    pass


class StreamNotResolvedException(IPTVException):
    pass


class NetConnectionError(IPTVException):
    pass


UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'


class IPTVClient(object):
    def __init__(self, storage_dir, file_name):
        self._storage_path = storage_dir
        self._storage_file = os.path.join(self._storage_path, file_name)

    def channels(self):
        # type: () -> List[Channel]
        raise NotImplementedError("Should have implemented this")

    def channel_stream_info(self, channel_id):
        # type: (str) -> StreamInfo
        raise NotImplementedError("Should have implemented this")

    def programme_stream_info(self, programme_id):
        # type: (str) -> StreamInfo
        raise NotImplementedError("Should have implemented this")

    def epg(self, channels, from_date, to_date):
        # type: (List[str],datetime,datetime) -> Dict[str, List[Programme]]
        raise NotImplementedError("Should have implemented this")

    def archive_days(self):
        # type: () -> int
        raise NotImplementedError("Should have implemented this")

    def _store_session(self, data):
        if not os.path.exists(self._storage_path):
            os.makedirs(self._storage_path)
        with open(self._storage_file, 'w') as f:
            json.dump(data.__dict__, f)

    def _load_session(self, data):
        if os.path.exists(self._storage_file):
            with open(self._storage_file, 'r') as f:
                data.__dict__ = json.load(f)
