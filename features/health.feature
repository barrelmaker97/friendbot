@PostStart
Feature: Responding to Actions

	Scenario: Request at /health
		Given friendbot is running
		When we make a GET request at /health
		Then we will get a 200 status code
		Then the response will be {"status":"running","sentence_generation":true}
