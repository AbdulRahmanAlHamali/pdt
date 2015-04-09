Feature: Instance admin interface

    Scenario: Instance list

        Given I am superuser
        And I have an instance

        When I go to instance list admin page

        Then I should see an instance in the list
