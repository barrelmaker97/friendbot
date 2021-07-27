@PostStart
Feature: Responding to Actions

	Scenario: Send button is pressed
		Given friendbot is running
		When we make a POST request at /action using ./test_data/actions/send.json
		Then we will get a 200 status code

	Scenario: Shuffle button is pressed
		Given friendbot is running
		When we make a POST request at /action using ./test_data/actions/shuffle.json
		Then we will get a 200 status code

	Scenario: Cancel button is pressed
		Given friendbot is running
		When we make a POST request at /action using ./test_data/actions/cancel.json
		Then we will get a 200 status code

	Scenario: Bad data is received
		Given friendbot is running
		When we make a POST request at /action using ./test_data/actions/bad.json
		Then we will get a 200 status code

	Scenario: Request at /action with the wrong method
		Given friendbot is running
		When we make a GET request at /action
		Then we will get a 405 status code
