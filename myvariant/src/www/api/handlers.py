# -*- coding: utf-8 -*-
from biothings.www.api.handlers import MetaDataHandler, BiothingHandler, QueryHandler, StatusHandler, FieldsHandler
from www.api.es import ESQuery
import config

class VariantHandler(BiothingHandler):
    ''' This class is for the /variant endpoint. '''
    settings = config.MyVariantSettings()
    esq = ESQuery(settings)

class QueryHandler(QueryHandler):
    ''' This class is for the /query endpoint. '''
    settings = config.MyVariantSettings()
    esq = ESQuery(settings)

class StatusHandler(StatusHandler):
    ''' This class is for the /status endpoint. '''
    settings = config.MyVariantSettings()
    esq = ESQuery(settings)

class FieldsHandler(FieldsHandler):
    ''' This class is for the /metadata/fields endpoint. '''
    settings = config.MyVariantSettings()
    esq = ESQuery(settings)

class MetaDataHandler(MetaDataHandler):
    ''' This class is for the /metadata endpoint. '''
    settings = config.MyVariantSettings()
    esq = ESQuery(settings)


def return_applist():
    return [
        (r"/variant/(.+)/?", VariantHandler),
        (r"/variant/?$", VariantHandler),
        (r"/query/?", QueryHandler),
        (r"/status", StatusHandler),
        (r"/metadata", MetaDataHandler),
        (r"/metadata/fields", FieldsHandler),
    ]