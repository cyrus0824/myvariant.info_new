# -*- coding: utf-8 -*-
from biothings.www.api.es import ESQuery
import re

class ESQuery(ESQuery):
    def _use_hg38(self):
        self._index = self._settings.es_hg38_index

    def _parse_interval_query(self, query):
        '''Check if the input query string matches interval search regex,
           if yes, return a dictionary with three key-value pairs:
              chr
              gstart
              gend
            , otherwise, return None.
        '''
        pattern = r'chr(?P<chr>\w+):(?P<gstart>[0-9,]+)-(?P<gend>[0-9,]+)'
        if query:
            mat = re.search(pattern, query)
            if mat:
                return mat.groupdict()

    def query(self, q, **kwargs):
        # Check if special interval query pattern exists
        interval_query = self._parse_interval_query(q)
        facets = self._parse_facets_option(kwargs)
        options = self._get_cleaned_query_options(kwargs)
        scroll_options = {}
        if options.fetch_all:
            scroll_options.update({'search_type': 'scan', 'size': self._scroll_size, 'scroll': self._scroll_time})
        options['kwargs'].update(scroll_options)
        if interval_query:
            options['kwargs'].update(interval_query)
            res = self.query_interval(**options.kwargs)
        else:
            _query = {
                "query": {
                    "query_string": {
                        #"default_field" : "content",
                        "query": q
                    }
                }
            }
            if facets:
                _query['facets'] = facets
            try:
                res = self._es.search(index=self._index, doc_type=self._doc_type, body=_query, **options.kwargs)
            except RequestError:
                return {"error": "invalid query term.", "success": False}

        if not options.raw:
            res = self._cleaned_res2(res, options=options)
        return res

    def query_interval(self, chr, gstart, gend, **kwargs):
        #gstart = safe_genome_pos(gstart)
        #gend = safe_genome_pos(gend)
        if chr.lower().startswith('chr'):
            chr = chr[3:]

        _query = {
            "query": {
                "bool": {
                    "should": []
                }
            }
        }
        hg19_interval_fields = ['dbnsfp.hg19', 'dbsnp.hg19', 'evs.hg19', 'mutdb.hg19', 'docm.hg19']
        for field in hg19_interval_fields:
            _q = {
                "bool": {
                    "must": [
                        {
                            "term": {"chrom": chr.lower()}
                        },
                        {
                            "range": {field + ".start": {"lte": gend}}
                        },
                        {
                            "range": {field + ".end": {"gte": gstart}}
                        }
                    ]
                }
            }
            _query["query"]["bool"]["should"].append(_q)
        return self._es.search(index=self._index, doc_type=self._doc_type, body=_query, **kwargs)

    def _get_options(self, options, kwargs):
        options.jsonld = kwargs.pop('jsonld', False)
        return options

    def _modify_biothingdoc(self, doc, options=None):
        # Subclass to insert cadd key
        if 'cadd' in doc:
            doc['cadd']['_license'] = 'http://goo.gl/bkpNhq'
        if options and options.jsonld:
            doc['@context'] = 'http://' + options.host + '/context/variant.jsonld'
        return doc