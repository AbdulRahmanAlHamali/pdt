Feature: Instance admin interface

    Scenario: Instance list

        Given I am superuser
        And I have an instance

        When I go to instance list admin page

        Then I should see an instance in the list


    Scenario: Create instance

        Given I am superuser
        And I have a CI project

        When I go to add instance admin page
        And I fill instance form
        And I submit the form

        Then I should see a "success" message
        And the instance should be created
