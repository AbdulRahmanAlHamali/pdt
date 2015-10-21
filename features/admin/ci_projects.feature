Feature: CI project admin interface

    Scenario: CI project list

        Given I am superuser
        And I have a ci project

        When I go to ci project list admin page

        Then I should see a ci project in the list


    Scenario: Create CI project

        Given I am superuser

        When I go to add ci project admin page
        And I fill ci project form
        And I submit the form

        Then I should see a "success" message
        And the ci project should be created
