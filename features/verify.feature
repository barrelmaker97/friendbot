@PostStart
Feature: Verify Requests

	Scenario: Perform an action with an unsigned request
		Given friendbot is running
		When we make a POST request that isn't signed at /action using ./example-data/actions/shuffle.json
		Then we will get a 400 status code

	Scenario: Perform an action with an old request
		Given friendbot is running
		When we make a POST request that is too old at /action using ./example-data/actions/shuffle.json
		Then we will get a 400 status code

	Scenario: Request a sentence with an unsigned request
		Given friendbot is running
		When we make a blank POST request as UCF55PTPV at /sentence that isn't signed
		Then we will get a 400 status code

	Scenario: Request a sentence with an old request
		Given friendbot is running
		When we make a blank POST request as UCF55PTPV at /sentence that is too old
		Then we will get a 400 status code
