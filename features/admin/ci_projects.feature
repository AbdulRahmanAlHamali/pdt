Feature: CI project admin interface

    Scenario: CI project list

        Given I am superuser
        And I have a CI project

        When I go to CI project list admin page

        Then I should see a CI project in the list


    Scenario: Create CI project

        Given I am superuser

        When I go to add CI project admin page
        And I fill CI project form
        And I submit the form

        Then I should see a "success" message
        And the CI project should be created
