import configparser
import datetime
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

    def AddTestsToTestPlan(self, cred_path, testcase_path, testPlanId):
        # Add Test Cases to Test Plan provide test Case list path, credential config and testPlanKey
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

    def GetTestCasesAssociatedToTestPlan(self, cred_path, testPlanId):
        # Get List of Test Cases attached to a test plan, provide credentials config and testPlanKey
        JiraXrayRobot.get_jira_cred(self, cred_path)
        headers = {'Content-Type': 'application/json'}
        rsp=requests.get(self.jira_server + "/rest/raven/1.0/api/testplan/"+testPlanId+"/test",headers=headers, auth=(self.jira_username, self.jira_password), verify=False)
        return(rsp.json())

    def DeleteTestCaseFromTestPlan(self, cred_path, testPlanId, *testCaseIds):
        # Delete Test Cases attached to a test plan, provide credentials config and testPlanKey and TestKeys to be deleted
        JiraXrayRobot.get_jira_cred(self, cred_path)
        headers = {'Content-Type': 'application/json'}
        for testCaseId in testCaseIds:
            rsp = requests.delete(self.jira_server + "/rest/raven/1.0/api/testplan/"+testPlanId+"/test/"+testCaseId, headers=headers, auth=(self.jira_username, self.jira_password), verify=False)
            if (rsp.status_code == 200):
                print("Successfully Deleted "+ testCaseId)

    def GetTestExecutionAssociatedWithTestPlan(self, cred_path, testPlanId):
        # Get List of Test Execution attached to a test plan, provide credentials config and testPlanKey
        JiraXrayRobot.get_jira_cred(self, cred_path)
        headers = {'Content-Type': 'application/json'}
        response = requests.get(self.jira_server + "/rest/raven/1.0/api/testplan/"+testPlanId+"/testexecution",headers=headers, auth=(self.jira_username, self.jira_password), verify=False)
        return(response.json())

    def AssociateTestExecutionWithTestPLan(self, cred_path, testPlanId, *testExecutionIds):
        # Attach  Test Executions to a test plan, provide credentials config and testPlanKey and TestExecutionKeys
        JiraXrayRobot.get_jira_cred(self, cred_path)
        testExecutionLists = ""
        for testExecutionId in testExecutionIds:
            testExecutionLists = testExecutionLists + '"' + testExecutionId + '"' + ","
        addExecutions = '''
        {
            "add": [''' + testExecutionLists[:-1] + ''']
        }'''
        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.jira_server + "/rest/raven/1.0/api/testplan/" + testPlanId + "/testexecution",
                                 headers=headers, data=addExecutions, auth=(self.jira_username, self.jira_password), verify=False)
        return (response.text)

    def DeleteTestExecutionFromTestPLan(self, cred_path, testPlanId, *testExecutionIds):
        # Delete Test Execution from a test plan, provide credentials config and testPlanKey and testExecutionKeys
        JiraXrayRobot.get_jira_cred(self, cred_path)
        headers = {'Content-Type': 'application/json'}
        for testExecutionId in testExecutionIds:
            rsp = requests.delete(self.jira_server + "/rest/raven/1.0/api/testplan/"+testPlanId+"/testexecution/"+testExecutionId, headers=headers, auth=(self.jira_username, self.jira_password), verify=False)
            if (rsp.status_code == 200):
                print("Successfully Deleted "+ testExecutionId)



    def UploadRobotFrameworkReportToJira(self, cred_path, project_key, testplan_key, resultxml):
        # Upload Robot Execution Report to a test Plan , provide credentials config, ProjectKey, testPlanKey, and full path of output.xml
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

    def ImportSingleTestResult(self, cred_path, testExecutionId, testCaseId, status, releaseNumber='', comment=''):
        JiraXrayRobot.get_jira_cred(self, cred_path)
        testCaseString = ''
        start_Date = str(datetime.datetime.now().isoformat()).split('.')[0] + '+01:00'
        end_Date = str(datetime.datetime.now().isoformat()).split('.')[0] + '+01:00'
        run_date = str(datetime.datetime.now().isoformat()).split('.')[0] + '+01:00'
        headers = {'Content-Type': 'application/json'}
        infoSection = '"info" : {"summary" : "Updated Test Results for Release' + releaseNumber + '","description" : "Updated From Automation", "user" : "' + self.jira_username + '","startDate" : "' + start_Date + '","finishDate" : "' + end_Date + '"}'
        testCaseString = testCaseString + '{'
        testCaseString = testCaseString + '"start" : "'+run_date+'",'+'"finish" : "'+run_date+'",'+'"testKey" : "'+testCaseId+'", "status" :"'+status+'", "comment" : "'+comment+'"},'
        testCaseDetails = '[' + testCaseString[:-1] + ']'
        completeRequest = '{"testExecutionKey" : "' + testExecutionId + '",' + infoSection + ',"tests" : ' + testCaseDetails + '}'
        response = requests.post(self.jira_server+"/rest/raven/1.0/import/execution", headers=headers,
                                 data=completeRequest, auth=(self.jira_username, self.jira_password), verify=False)
        return(response.text)