Feature: Generating Sentences

	Scenario: Request a sentence using all data
		Given friendbot is running
		When we make a POST request for channel all user all at /sentence
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header

	Scenario: Get corpus size in response
		Given friendbot is running
		When we make a POST request for channel all user all at /sentence
		Then we will get a 200 status code
		And we will get a Friendbot-Corpus-Lines: 18 header

	Scenario: Request a sentence with no selections
		Given friendbot is running
		When we make a blank POST request at /sentence
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header

	Scenario: Request a sentence using a specific channel
		Given friendbot is running
		When we make a POST request for channel general user all at /sentence
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header

	Scenario: Request a sentence using a specific user
		Given friendbot is running
		When we make a POST request for channel all user <@UCF55PTPV> at /sentence
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header

	Scenario: Request a sentence using a specific channel and user
		Given friendbot is running
		When we make a POST request for channel general user <@UCF55PTPV> at /sentence
		Then we will get a 200 status code
		And we will get a Friendbot-Error: False header

	Scenario: Request a sentence for a missing channel
		Given friendbot is running
		When we make a POST request for channel TEST user all at /sentence
		Then we will get a 200 status code
		And we will get a Friendbot-Error: True header

	Scenario: Request a sentence for a missing user
		Given friendbot is running
		When we make a POST request for channel all user TEST at /sentence
		Then we will get a 200 status code
		And we will get a Friendbot-Error: True header

	Scenario: Request a sentence with the wrong method
		Given friendbot is running
		When we make a GET request at /sentence
		Then we will get a 405 status code
