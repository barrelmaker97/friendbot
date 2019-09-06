Feature: Loading Friendbot

	Scenario: Channels are loaded from good data
		When we load good channel data from ./test_data/export

	Scenario: Channels are loaded from bad data
		When we load bad channel data from ./bad_path

	Scenario: Users are loaded from good data
		When we load good user data from ./test_data/export

	Scenario: Users are loaded from bad data
		When we load bad user data from ./bad_path
