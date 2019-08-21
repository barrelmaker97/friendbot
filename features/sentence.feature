Feature: Generating Sentences

	Scenario: Request a sentence
		Given friendbot is running
		When we make a POST request for channel all user all at the /sentence endpoint
		Then we will get a 200 status code

	Scenario: Request a sentence for a missing channel
		Given friendbot is running
		When we make a POST request for channel TEST user all at the /sentence endpoint
		Then we will get a 200 status code
		And we will receive "Error: Channel not found"

	Scenario: Request a sentence for a missing user
		Given friendbot is running
		When we make a POST request for channel all user TEST at the /sentence endpoint
		Then we will get a 200 status code
		And we will receive "Error: User not found"

	Scenario: Request a sentence with the wrong method
		Given friendbot is running
		When we make a GET request at the /sentence endpoint
		Then we will get a 405 status code
