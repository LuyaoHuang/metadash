from flask import Blueprint
from flask_restful import Resource, Api, abort

from ..models import TestResult, TestCase, TestRun
from metadash.models import db, get_or_create
from metadash.apis import EntityParser, pager, envolop

TestCaseParser = EntityParser(TestCase)
TestRunParser = EntityParser(TestRun)
TestResultParser = EntityParser(TestResult)

Blueprint = Blueprint('test-results', __name__)

Api = Api(Blueprint)


def create_testcase(result, args):
    testcase_name = args['testcase_name']
    testcase, _ = get_or_create(db.session, TestCase, name=testcase_name)
    result.testcase = testcase


class TestCaseList(Resource):
    def get(self):
        args = TestCaseParser.parse_args()
        return envolop([result.as_dict() for result in pager(TestCase.query.filter_by(**args)).all()])

    def post(self):
        args = TestCaseParser.parse_args()
        testcase = TestCase.from_dict(args)
        db.session.add(testcase)
        db.session.commit()
        db.session.refresh(testcase)
        return testcase.as_dict()


class TestCaseDetail(Resource):
    def get(self, uuid_):
        testcase = TestCase.query.get(uuid_) or abort(
            404, message="TestResult {} doesn't exist".format(uuid_))
        return testcase.as_dict()

    def put(self, uuid_):
        args = TestCaseParser.parse_args()
        testcase = TestCase.query.get(uuid_) or abort(
            404, message="TestResult {} doesn't exist".format(uuid_))
        testcase.from_dict(args)
        db.session.commit()
        db.session.refresh(testcase)
        return testcase.as_dict()


class TestResultList(Resource):
    def get(self):
        args = TestResultParser.parse_args()
        return envolop([result.as_dict() for result in
                        pager(TestResult.query.filter_by(**args)).all()])

    def post(self):
        args = TestResultParser.parse_args()
        result = TestResult.from_dict(args)
        create_testcase(result, args)
        db.session.add(result)
        db.session.commit()
        db.session.refresh(result)
        return result.as_dict()


class TestResultDetail(Resource):
    def get(self, uuid_):
        result = TestResult.query.filter_by(uuid=uuid_).first() or abort(
            404, message="TestResult {} doesn't exist".format(uuid_))
        return result.as_dict()


class TestRunList(Resource):
    def get(self):
        args = TestRunParser.parse_args()
        return envolop([testrun.as_dict() for testrun in
                        pager(TestRun.query.filter_by(**args)).all()])

    def post(self):
        args = TestRunParser.parse_args()
        testrun = TestRun.from_dict(args)
        # testrun.tags.append("statistic")
        db.session.add(testrun)
        db.session.commit()
        db.session.refresh(testrun)
        return testrun.as_dict()


class TestRunDetail(Resource):
    def put(self, uuid_):
        testrun = TestRun.query.filter_by(uuid=uuid_).first() or abort(
            404, message="TestRun {} doesn't exist".format(uuid_))
        args = TestRunParser.parse_args()
        testrun.from_dict(args)
        db.session.commit()
        return testrun.as_dict(detail=True)

    def get(self, uuid_):
        testrun = TestRun.query.filter_by(uuid=uuid_).first() or abort(
            404, message="TestRun {} doesn't exist".format(uuid_))
        return testrun.as_dict(detail=True)


Api.add_resource(TestCaseList, '/testcases/', endpoint='testcases')
Api.add_resource(TestCaseDetail, '/testcases/<uuid_>', endpoint='testcase')
Api.add_resource(TestResultList, '/testresults/', endpoint='testresults')
Api.add_resource(TestResultDetail, '/testresults/<uuid_>', endpoint='testresult')
Api.add_resource(TestRunList, '/testruns/', endpoint='testruns')
Api.add_resource(TestRunDetail, '/testruns/<uuid_>', endpoint='testrun')