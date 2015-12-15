from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from pyga.requests import (Tracker, Page, Session, Visitor,
                           Event, PageViewRequest, EventRequest)

class GAMixIn:
    def ga_track(self, settings, event={}):
        _req_list = []
        no_tracking = self.get_argument('no_tracking', None)
        is_prod = settings.ga_is_prod
        if not no_tracking and is_prod and settings.ga_account:
            _req = self.request
            remote_ip = _req.headers.get("X-Real-Ip",
                        _req.headers.get("X-Forwarded-For",
                        _req.remote_ip))
            user_agent = _req.headers.get("User-Agent", None)
            visitor = Visitor()
            visitor.ip_address = remote_ip
            visitor.user_agent = user_agent
            #get visitor.locale
            visitor.extract_from_server_meta(
                {"HTTP_ACCEPT_LANGUAGE": _req.headers.get("Accept-Language", None)}
            )
            session = Session()
            page = Page(_req.path)
            tracker = Tracker(settings.ga_account, settings.ga_tracker_url)
            # tracker.track_pageview(page, session, visitor)  #this is non-async request
            pvr = PageViewRequest(config=tracker.config,
                                  tracker=tracker,
                                  visitor=visitor,
                                  session=session,
                                  page=page)
            r = pvr.build_http_request()
            _req_list.append(HTTPRequest(r.get_full_url(),
                                         "POST" if (r.data) else "GET",
                                         headers=r.headers,
                                         body=r.data))
            if event:
                evt = Event(**event)
                #tracker.track_event(evt, session, visitor)  #this is non-async request
                er = EventRequest(config=tracker.config,
                                  tracker=tracker,
                                  visitor=visitor,
                                  session=session,
                                  event=evt)
                r = er.build_http_request()
                _req_list.append(HTTPRequest(r.get_full_url(),
                                             "POST" if (r.data) else "GET",
                                             headers=r.headers,
                                             body=r.data))

            #now send actual async requests
            http_client = AsyncHTTPClient()
            for _req in _req_list:
                http_client.fetch(_req)
