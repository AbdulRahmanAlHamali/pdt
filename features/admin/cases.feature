Feature: Case admin interface

    Scenario: Case list

        Given I am superuser
        And I have a case

        When I go to case list admin page

        Then I should see a case in the list


    Scenario: Create case

        Given I am superuser
        And I have a CI project
        And I have a release

        When I go to add case admin page
        And I fill case form
        And I submit the form

        Then I should see a "success" message
        And the case should be created
