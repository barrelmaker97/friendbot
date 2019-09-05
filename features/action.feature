Feature: Responding to Actions

	Scenario: POST an action
		Given friendbot is running
		When we make a POST request at /action using data from ./test_data/action.json
		Then we will get a 204 status code
