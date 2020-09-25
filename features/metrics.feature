@PostStart
Feature: Retrieving Metrics

	Scenario: Request metrics
		Given friendbot is running
		When we make a GET request at /metrics
		Then we will get a 200 status code
