# -*- coding: utf-8 -*-
from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, StatusHandler, FieldsHandler
from www.api.es import ESQuery
import config

class VariantHandler(BiothingHandler):
    ''' This class is for the /variant endpoint. '''
    _settings = config.MyVariantSettings()
    esq = ESQuery(_settings)

    def _examine_kwargs(self, action, kwargs):
        if kwargs.pop('hg38', False):
            self.esq._use_hg38()
        #if action == 'GET':
        #    pass
        #elif action == 'POST':
        #    pass
        #pass


class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    _settings = config.MyVariantSettings()
    esq = ESQuery(_settings)

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    _settings = config.MyVariantSettings()
    esq = ESQuery(_settings)

class FieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''
    _settings = config.MyVariantSettings()
    esq = ESQuery(_settings)

class MetaDataHandler(MetaDataHandler):
    ''' This class is for the /metadata endpoint. '''
    _settings = config.MyVariantSettings()
    esq = ESQuery(_settings)

    disable_caching = True

    def get(self):
        # For now, just return a hardcoded object, later we'll actually query the ES db for this information
        self.return_json({
            "stats": {
                "total": 316403311,
                "cadd": 163690986,
                "clinvar": 114627,
                "cosmic": 1024498,
                "dbnsfp": 82030830,
                "dbsnp": 145132257,
                "docm": 1119,
                "emv": 12066,
                "evs": 1977300,
                "exac": 10195872,
                "grasp": 2212148,
                "gwassnps": 15243,
                "mutdb": 420221,
                "snpedia": 5907,
                "snpeff": 313576885,
                "wellderly": 21240519
            },
            "src_version": {
                "cadd": "1.2",
                "clinvar": "201509",
                "cosmic": "68",
                "dbnsfp": "3.0c",
                "dbsnp": "144",
                "evs": "2",
                "exac": "0.3",
                "grasp": "2.0.0.0"
            },
            "timestamp": "2015-10-21T07:02:18.178506"
        })

def return_applist():
    _settings = config.MyVariantSettings()
    ret = [
        (r"/status", StatusHandler),
        (r"/metadata", MetaDataHandler),
        (r"/metadata/fields", FieldsHandler),
    ]
    if _settings._api_version:
        ret += [
            (r"/" + _settings._api_version + "/metadata", MetaDataHandler),
            (r"/" + _settings._api_version + "/metadata/fields", FieldsHandler),
            (r"/" + _settings._api_version + "/variant/(.+)/?", VariantHandler),
            (r"/" + _settings._api_version + "/variant/?$", VariantHandler),
            (r"/" + _settings._api_version + "/query/?", QueryHandler),
        ]
    else:
        ret += [
            (r"/variant/(.+)/?", VariantHandler),
            (r"/variant/?$", VariantHandler),
            (r"/query/?", QueryHandler),
        ]
    return ret