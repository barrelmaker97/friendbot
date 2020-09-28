@PostStartNoRedis
Feature: Generating Sentences without Redis

	Scenario: Request a sentence with no selections
		Given friendbot is running
		When we make a blank POST request at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header
		And we will get a Friendbot-Channel: None header
		And we will get a Friendbot-User: None header

	Scenario: Request a sentence with a bad user_id
		Given friendbot is running
		When we make a blank POST request at /sentence as nobody
		Then we will get a 200 status code
		And we will get a Friendbot-Error: True header

	Scenario: Request a sentence with no user_id
		Given friendbot is running
		When we make a blank POST request at /sentence with no user_id
		Then we will get a 200 status code
		And we will get a Friendbot-Error: True header

	Scenario: Request a sentence with an unsigned request
		Given friendbot is running
		When we make a blank POST request at /sentence that isn't signed
		Then we will get a 400 status code

	Scenario: Request a sentence with an old request
		Given friendbot is running
		When we make a blank POST request at /sentence that is too old
		Then we will get a 400 status code

	Scenario: Request a sentence using a specific channel
		Given friendbot is running
		When we make a POST request for <#CCF28A75J|channel> at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header
		And we will get a Friendbot-Channel: CCF28A75J header
		And we will get a Friendbot-User: None header

	Scenario: Request a sentence using a specific channel with different formatting
		Given friendbot is running
		When we make a POST request for &lt;#CCF28A75J|channel&gt; at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header
		And we will get a Friendbot-Channel: CCF28A75J header
		And we will get a Friendbot-User: None header

	Scenario: Request a sentence using a specific user
		Given friendbot is running
		When we make a POST request for <@UCF55PTPV|user> at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header
		And we will get a Friendbot-Channel: None header
		And we will get a Friendbot-User: UCF55PTPV header

	Scenario: Request a sentence using a specific channel and user
		Given friendbot is running
		When we make a POST request for <#CCF28A75J|channel> and <@UCF55PTPV|user> at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header
		And we will get a Friendbot-Channel: CCF28A75J header
		And we will get a Friendbot-User: UCF55PTPV header

	Scenario: Request a sentence using a specific user and channel
		Given friendbot is running
		When we make a POST request for <@UCF55PTPV|user> and <#CCF28A75J|channel> at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header
		And we will get a Friendbot-Channel: CCF28A75J header
		And we will get a Friendbot-User: UCF55PTPV header

	Scenario: Request a sentence using a specific channel and user with different formatting
		Given friendbot is running
		When we make a POST request for &lt;#CCF28A75J|channel&gt; and <@UCF55PTPV|user> at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header
		And we will get a Friendbot-Channel: CCF28A75J header
		And we will get a Friendbot-User: UCF55PTPV header

	Scenario: Request a sentence using a specific user and channel with different formatting
		Given friendbot is running
		When we make a POST request for <@UCF55PTPV|user> and &lt;#CCF28A75J|channel&gt; at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header
		And we will get a Friendbot-Channel: CCF28A75J header
		And we will get a Friendbot-User: UCF55PTPV header

	Scenario: Request a sentence with an incorrectly formatted parameter
		Given friendbot is running
		When we make a POST request for TEST at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: True header

	Scenario: Request a sentence with two incorrectly formatted parameters
		Given friendbot is running
		When we make a POST request for TEST and TEST at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: True header

	Scenario: Request a sentence for a non existent channel
		Given friendbot is running
		When we make a POST request for <#C12345678|channel> at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: True header

	Scenario: Request a sentence for a non existent user
		Given friendbot is running
		When we make a POST request for <@U12345678|user> at /sentence as UCF55PTPV
		Then we will get a 200 status code
		And we will get a Friendbot-Error: True header

	Scenario: Request a sentence with the wrong method
		Given friendbot is running
		When we make a GET request at /sentence
		Then we will get a 405 status code
