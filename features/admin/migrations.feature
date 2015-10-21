Feature: Migration admin interface

    Scenario: Migration list

        Given I am superuser
        And I have a migration

        When I go to migration list admin page

        Then I should see a migration in the list


    Scenario: Create migration

        Given I am superuser
        And I have a case

        When I go to add migration admin page
        And I fill migration form
        And I submit the form

        Then I should see a "success" message
        And the migration should be created
