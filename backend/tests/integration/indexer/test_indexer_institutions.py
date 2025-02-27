# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.


import orjson
from helpers.utils import create_record, es_search
from marshmallow import utils

from inspirehep.records.marshmallow.institutions import InstitutionsElasticSearchSchema


def test_index_institutions_record(inspire_app, datadir):
    data = orjson.loads((datadir / "902725.json").read_text())
    record = create_record("ins", data=data)

    expected_count = 1
    expected_metadata = InstitutionsElasticSearchSchema().dump(record).data
    expected_metadata["affiliation_suggest"] = {
        "input": [
            "CERN, Geneva",
            "CERN",
            "European Organization for Nuclear Research",
            "CERN",
            "Centre Européen de Recherches Nucléaires",
            "01631",
            "1211",
        ]
    }
    expected_metadata["number_of_papers"] = 0
    expected_metadata["_created"] = utils.isoformat(record.created)
    expected_metadata["_updated"] = utils.isoformat(record.updated)

    response = es_search("records-institutions")

    assert response["hits"]["total"]["value"] == expected_count
    assert response["hits"]["hits"][0]["_source"] == expected_metadata
