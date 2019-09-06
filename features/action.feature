@PostStart
Feature: Responding to Actions

	Scenario: POST an action
		Given friendbot is running
		When we make a POST request at /action using data from ./test_data/action.json
		Then we will get a 200 status code

	Scenario: Request at /action with the wrong method
		Given friendbot is running
		When we make a GET request at /action
		Then we will get a 405 status code
