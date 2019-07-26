import configparser
import requests

class JiraXrayRobot:

    def __init__(self):
        self.jira_server = None
        self.jira_username = None
        self.jira_password = None

    def get_jira_cred(self, path):
        config = configparser.ConfigParser()
        config.read(path)
        self.jira_server = config['JIRA_CREDENTIALS']['server']
        self.jira_username = config['JIRA_CREDENTIALS']['username']
        self.jira_password = config['JIRA_CREDENTIALS']['password']

    def get_test_cases_list(self, testcase_path):
        readTestCase = open(testcase_path)
        return (str(readTestCase.read()).strip())

    def CreateTestPlan(self, cred_path, project_key, testplan_summary='', testplan_description=''):
        # Keyword to create a test Plan
        # jira_server, jira_username, jira_password = JiraXrayRobot.get_jira_cred()
        JiraXrayRobot.get_jira_cred(self, cred_path)
        createPlan = '''{
            "fields": {
               "project":
               {
                  "key": "''' + project_key + '''"

               },
               "summary": "[''' + testplan_summary + ''']",
               "description": "[''' + testplan_description + ''']",
               "issuetype": {
                  "name": "Test Plan"
               }
           }
        }'''
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.jira_server + "/rest/api/2/issue", headers=headers, data=createPlan,
                                 auth=(self.jira_username, self.jira_password), verify=False)
        responseJson = response.json()
        return (responseJson['key'])

    def AddTestsToTestPlan(self, testcase_path, cred_path, testPlanId):
        # Add Test Cases to Test Plan
        JiraXrayRobot.get_jira_cred(self, cred_path)
        testCaseIds = JiraXrayRobot.get_test_cases_list(self, testcase_path)
        testCaseList = ""
        for testCase in testCaseIds.split(','):
            testCaseList = testCaseList + '"' + testCase + '"' + ","

        print(testCaseList)
        addTests = '''
        {
            "add": [''' + testCaseList[:-1] + ''']
        }'''
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.jira_server + "/rest/raven/1.0/api/testplan/" + testPlanId + "/test",
                                 headers=headers, data=addTests, auth=(self.jira_username, self.jira_password),
                                 verify=False)
        return (response.text)

    def UploadRobotFrameworkReportToJira(self, cred_path, project_key, testplan_key, resultxml):
        JiraXrayRobot.get_jira_cred(self, cred_path)
        params = (
            ("projectKey", project_key),
            ("testPlanKey", testplan_key)
        )

        files = {
            'file': ('output.xml', open(resultxml, 'rb'))
        }

        response = requests.post(self.jira_server + '/rest/raven/1.0/import/execution/robot', params=params,
                                 files=files, auth=(self.jira_username, self.jira_password))
        responseJson = response.json()
        return (responseJson['testExecIssue']['key'])