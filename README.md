# JiraXrayRobot
Robot Framework Library to interact with Jira Xray

Sample Test Case

*** Settings ***
Library           JiraXrayRobot

*** Test Cases ***
CreateTestPlan
    ${testPlanId}    CreateTestPlan    <ConfigFilePath/JiraUserCredentials>.config    <Project_Key>    <test Plan Summay>     <Test Plan Description>
    Log To Console    ${testPlanId}

Config File Should be as below


[JIRA_CREDENTIALS]
server = <JIRA Server only>
username = XXXXX
password = XXXXX
  
Add Test Case
    AddTestsToTestPlan    <List Of Test Caes file>      <Config File Credentials as shown above>    <TEst Plan Id>
  
Sample TEst Case list below

<TestCaseKey>,<TestCaseKey>




