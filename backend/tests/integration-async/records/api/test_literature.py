# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.
import copy

from helpers.providers.faker import faker
from helpers.utils import retry_until_pass
from invenio_db import db

from inspirehep.records.api import ConferencesRecord, LiteratureRecord
from inspirehep.records.api.base import InspireRecord
from inspirehep.records.models import RecordsAuthors


def test_authors_signature_blocks_and_uuids_added_after_create_and_update(
    inspire_app, clean_celery_session
):
    data = {
        "$schema": "http://localhost:5000/schemas/records/hep.json",
        "titles": [{"title": "Test a valid record"}],
        "document_type": ["article"],
        "_collections": ["Literature"],
        "authors": [{"full_name": "Doe, John"}],
    }

    record = LiteratureRecord.create(data)
    db.session.commit()

    record_control_number = record["control_number"]
    record = LiteratureRecord.get_record_by_pid_value(record_control_number)
    expected_signature_block = "Dj"

    assert expected_signature_block == record["authors"][0]["signature_block"]
    assert "uuid" in record["authors"][0]

    expected_versions_len = 1
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record

    expected_signature_block = "ELj"
    data.update(
        {
            "authors": [{"full_name": "Ellis, Jane"}],
            "control_number": record["control_number"],
        }
    )
    record.update(data)
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)

    assert expected_signature_block == record["authors"][0]["signature_block"]

    expected_versions_len = 2
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record


def test_conference_paper_get_updated_reference_when_adding_new_record(
    inspire_app, clean_celery_session
):
    conference_1 = ConferencesRecord.create(faker.record("con"))
    conference_1_control_number = conference_1["control_number"]
    ref_1 = f"http://localhost:8000/api/conferences/{conference_1_control_number}"

    expected_result = [conference_1.id]

    data = {
        "publication_info": [{"conference_record": {"$ref": ref_1}}],
        "document_type": ["conference paper"],
    }

    record = LiteratureRecord.create(faker.record("lit", data))
    record_control_number = record["control_number"]
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)

    assert expected_result == record.get_newest_linked_conferences_uuid()

    expected_versions_len = 1
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record


def test_conference_paper_get_updated_reference_when_replacing_conference(
    inspire_app, clean_celery_session
):
    conference_1 = ConferencesRecord.create(faker.record("con"))
    conference_1_control_number = conference_1["control_number"]
    ref_1 = f"http://localhost:8000/api/conferences/{conference_1_control_number}"

    conference_2 = ConferencesRecord.create(faker.record("con"))
    conference_2_control_number = conference_2["control_number"]
    ref_2 = f"http://localhost:8000/api/conferences/{conference_2_control_number}"

    expected_result = sorted([conference_2.id, conference_1.id])

    data = {
        "publication_info": [{"conference_record": {"$ref": ref_1}}],
        "document_type": ["conference paper"],
    }

    record = LiteratureRecord.create(faker.record("lit", data))
    record_control_number = record["control_number"]
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)
    expected_versions_len = 1
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record

    data = copy.deepcopy(dict(record))
    data["publication_info"] = [{"conference_record": {"$ref": ref_2}}]
    record.update(data)
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)
    assert expected_result == sorted(record.get_newest_linked_conferences_uuid())

    expected_versions_len = 2
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record


def test_conference_paper_get_updated_reference_conference_when_updates_one_conference(
    inspire_app, clean_celery_session
):
    conference_1 = ConferencesRecord.create(faker.record("con"))
    conference_1_control_number = conference_1["control_number"]
    ref_1 = f"http://localhost:8000/api/conferences/{conference_1_control_number}"

    conference_2 = ConferencesRecord.create(faker.record("con"))
    conference_2_control_number = conference_2["control_number"]
    ref_2 = f"http://localhost:8000/api/conferences/{conference_2_control_number}"

    expected_result = [conference_2.id]

    data = {
        "publication_info": [{"conference_record": {"$ref": ref_1}}],
        "document_type": ["conference paper"],
    }

    record = LiteratureRecord.create(faker.record("lit", data))
    record_control_number = record["control_number"]
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)
    expected_versions_len = 1
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record

    data = copy.deepcopy(dict(record))
    data["publication_info"].append({"conference_record": {"$ref": ref_2}})
    record.update(data)
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)

    assert expected_result == sorted(record.get_newest_linked_conferences_uuid())

    expected_versions_len = 2
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record


def test_conference_paper_get_updated_reference_conference_returns_nothing_when_not_updating_conference(
    inspire_app, clean_celery_session
):
    conference_1 = ConferencesRecord.create(faker.record("con"))
    conference_1_control_number = conference_1["control_number"]
    ref_1 = f"http://localhost:8000/api/conferences/{conference_1_control_number}"

    expected_result = []

    data = {
        "publication_info": [{"conference_record": {"$ref": ref_1}}],
        "document_type": ["conference paper"],
    }

    record = LiteratureRecord.create(faker.record("lit", data))
    record_control_number = record["control_number"]
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)

    expected_versions_len = 1
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record

    data = copy.deepcopy(dict(record))
    expected_result = []
    record.update(data)
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)
    assert expected_result == record.get_newest_linked_conferences_uuid()

    expected_versions_len = 2
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record


def test_conference_paper_get_updated_reference_conference_returns_all_when_deleting_lit_record(
    inspire_app, clean_celery_session
):
    conference_1 = ConferencesRecord.create(faker.record("con"))
    conference_1_control_number = conference_1["control_number"]
    ref_1 = f"http://localhost:8000/api/conferences/{conference_1_control_number}"

    expected_result = [conference_1.id]

    data = {
        "publication_info": [{"conference_record": {"$ref": ref_1}}],
        "document_type": ["conference paper"],
    }

    record = LiteratureRecord.create(faker.record("lit", data))
    record_control_number = record["control_number"]
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)
    expected_versions_len = 1
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record

    record.delete()
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)

    assert expected_result == sorted(record.get_newest_linked_conferences_uuid())

    expected_versions_len = 2
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record


def test_conference_paper_get_updated_reference_conference_returns_nothing_when_conf_doc_type_stays_intact(
    inspire_app, clean_celery_session
):
    conference_1 = ConferencesRecord.create(faker.record("con"))
    conference_1_control_number = conference_1["control_number"]
    ref_1 = f"http://localhost:8000/api/conferences/{conference_1_control_number}"

    expected_result = []

    data = {
        "publication_info": [{"conference_record": {"$ref": ref_1}}],
        "document_type": ["conference paper"],
    }

    record = LiteratureRecord.create(faker.record("lit", data))
    record_control_number = record["control_number"]
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)

    expected_versions_len = 1
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record

    data = copy.deepcopy(dict(record))
    data["document_type"].append("article")
    record.update(data)
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)

    assert expected_result == sorted(record.get_newest_linked_conferences_uuid())

    expected_versions_len = 2
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record


def test_conference_paper_get_updated_reference_conference_when_document_type_changes_to_non_conf_related(
    inspire_app, clean_celery_session
):
    conference_1 = ConferencesRecord.create(faker.record("con"))
    conference_1_control_number = conference_1["control_number"]
    ref_1 = f"http://localhost:8000/api/conferences/{conference_1_control_number}"

    expected_result = [conference_1.id]

    data = {
        "publication_info": [{"conference_record": {"$ref": ref_1}}],
        "document_type": ["conference paper"],
    }

    record = LiteratureRecord.create(faker.record("lit", data))
    record_control_number = record["control_number"]
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)
    expected_versions_len = 1
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record

    data = copy.deepcopy(dict(record))
    data["document_type"] = ["article"]
    record.update(data)
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)
    assert expected_result == sorted(record.get_newest_linked_conferences_uuid())

    expected_versions_len = 2
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record


def test_conference_paper_get_updated_reference_conference_when_document_type_changes_to_other_conf_related(
    inspire_app, clean_celery_session
):
    conference_1 = ConferencesRecord.create(faker.record("con"))
    conference_1_control_number = conference_1["control_number"]
    ref_1 = f"http://localhost:8000/api/conferences/{conference_1_control_number}"

    expected_result = [conference_1.id]

    data = {
        "publication_info": [{"conference_record": {"$ref": ref_1}}],
        "document_type": ["conference paper"],
    }

    record = LiteratureRecord.create(faker.record("lit", data))
    record_control_number = record["control_number"]
    db.session.commit()

    expected_versions_len = 1
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record

    data = copy.deepcopy(dict(record))
    data["document_type"] = ["proceedings"]
    record.update(data)
    db.session.commit()

    record = LiteratureRecord.get_record_by_pid_value(record_control_number)

    assert expected_result == sorted(record.get_newest_linked_conferences_uuid())

    expected_versions_len = 2
    results = record.model.versions.all()
    result_latest_version = results[-1].json

    assert expected_versions_len == len(results)
    assert result_latest_version == record


def test_literature_get_modified_authors_after_ref_update(inspire_app):
    data = {
        "authors": [
            {
                "full_name": "Brian Gross",
                "ids": [
                    {"schema": "INSPIRE ID", "value": "INSPIRE-00304313"},
                    {"schema": "INSPIRE BAI", "value": "J.M.Maldacena.1"},
                ],
                "emails": ["test@test.com"],
                "record": {"$ref": "https://inspirehep.net/api/authors/1028900"},
            }
        ]
    }
    data = faker.record("lit", with_control_number=True, data=data)

    record = LiteratureRecord.create(data)
    db.session.commit()

    assert len(list(record.get_modified_authors())) == 1

    data["authors"][0]["record"]["$ref"] = "https://inspirehep.net/api/authors/9999999"
    record.update(data)
    db.session.commit()

    assert len(list(record.get_modified_authors())) == 0


def test_fix_entries_by_update_date(inspire_app, clean_celery_session):
    literature_data = faker.record("lit", with_control_number=True)
    literature_data.update(
        {
            "authors": [
                {
                    "full_name": "George, Smith",
                    "ids": [{"value": "Smith.G.1", "schema": "INSPIRE BAI"}],
                }
            ]
        }
    )
    record_1 = InspireRecord.create(literature_data)
    literature_data_2 = faker.record("lit", with_control_number=True)
    literature_data_2.update(
        {
            "authors": [
                {
                    "full_name": "Xiu, Li",
                    "ids": [{"value": "X.Liu.1", "schema": "INSPIRE BAI"}],
                }
            ]
        }
    )
    record_2 = InspireRecord.create(literature_data_2)
    db.session.add(
        RecordsAuthors(
            author_id="A.Test.1",
            id_type="INSPIRE BAI",
            record_id=record_1.id,
        )
    )
    db.session.add(
        RecordsAuthors(
            author_id="A.Test.2",
            id_type="INSPIRE BAI",
            record_id=record_2.id,
        )
    )
    db.session.commit()

    def assert_all_entries_in_db():
        assert len(RecordsAuthors.query.all()) == 4

    retry_until_pass(assert_all_entries_in_db)

    LiteratureRecord.fix_entries_by_update_date()

    def assert_all_entries_in_db():
        assert len(RecordsAuthors.query.all()) == 2

    retry_until_pass(assert_all_entries_in_db, retry_interval=3)
