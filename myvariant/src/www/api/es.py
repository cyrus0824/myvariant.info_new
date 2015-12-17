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

    def query_interval(self, chr, gstart, gend, **kwargs):
        #gstart = safe_genome_pos(gstart)
        #gend = safe_genome_pos(gend)
        if chr.lower().startswith('chr'):
            chr = chr[3:]
        # _query = {
        #     "query": {
        #         "bool": {
        #             "should": [
        #                 {
        #                     "bool": {
        #                         "must": [
        #                             {
        #                                 "term": {"chrom": chr.lower()}
        #                             },
        #                             {
        #                                 "range": {"chromStart": {"lte": gend}}
        #                             },
        #                             {
        #                                 "range": {"chromEnd": {"gte": gstart}}
        #                             }
        #                         ]
        #                     }
        #                 },
        #                 {
        #                     "bool": {
        #                         "must": [
        #                             {
        #                                 "term": {"chrom": chr.lower()}
        #                             },
        #                             {
        #                                 "range": {"dbnsfp.hg19.start": {"lte": gend}}
        #                             },
        #                             {
        #                                 "range": {"dbnsfp.hg19.end": {"gte": gstart}}
        #                             }
        #                         ]
        #                     }
        #                 }
        #             ]
        #         }
        #     }
        # }
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

    def _modify_biothing_doc(self, doc):
        # Subclass to insert cadd key
        if 'cadd' in doc:
            doc['cadd']['_license'] = 'http://goo.gl/bkpNhq'