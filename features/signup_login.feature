Feature: ParaBank Sign Up then Login (E2E with reusable data)
  As a user
  I want to create an account and then sign in
  So that I can capture the post-login balance

  Background:
    Given I open the site
    And I log out if logged in

  Scenario Outline: Register a new user, then login and print balance
    And I navigate to the registration page
    When I register a new user with:
      | firstName | lastName | address         | city        | state | zip   | phone       | ssn         | username |
      | <first>   | <last>   | <address>       | <city>      | <st>  | <zip> | <phone>     | <ssn>       | UNIQUE   |
    And I remember the password from config
    Then registration should succeed
    And I log out if logged in
    When I log in with the remembered username and password
    Then I should see Accounts Overview and print the balance

   Examples: Typical US personas
      | first   | last   | address             | city        | st | zip   | phone       | ssn       |
      | Alicia  | Gomez  | 742 Evergreen Ter   | Springfield | IL | 62704 | 3125550182  | 111223333 |
      | Marcus  | Reid   | 19 Market Street    | Boston      | MA | 02108 | 6175550144  | 222334444 |

  Scenario Outline: Registration validations (required and format)
    And I navigate to the registration page
    When I attempt registration with:
      | firstName   | lastName   | address   | city   | state  | zip   | phone  | ssn    | username   | password   | confirm   |
      | <firstName> | <lastName> | <address> | <city> | <state>| <zip> | <phone>| <ssn>  | <username> | <password> | <confirm> |
    Then I should see a registration validation containing "<expect>"

    Examples:
      | firstName | lastName | address         | city      | state | zip   | phone       | ssn         | username | password | confirm  | expect                                        |
      | EMPTY     | Tester   | 123 Test Street | Testville | TS    | 12345 | 5551234567  | 123-45-6789 | UNIQUE   | Venice12 | Venice12 | First name is required.                       |
      | John      | EMPTY    | 123 Test Street | Testville | TS    | 12345 | 5551234567  | 123-45-6789 | UNIQUE   | Venice12 | Venice12 | Last name is required.                        |
      | John      | Tester   | EMPTY           | Testville | TS    | 12345 | 5551234567  | 123-45-6789 | UNIQUE   | Venice12 | Venice12 | Address is required.                          |
      | John      | Tester   | 123 Test Street | EMPTY     | TS    | 12345 | 5551234567  | 123-45-6789 | UNIQUE   | Venice12 | Venice12 | City is required.                             |
      | John      | Tester   | 123 Test Street | Testville | EMPTY | 12345 | 5551234567  | 123-45-6789 | UNIQUE   | Venice12 | Venice12 | State is required.                            |
      | John      | Tester   | 123 Test Street | Testville | TS    | EMPTY | 5551234567  | 123-45-6789 | UNIQUE   | Venice12 | Venice12 | Zip Code is required.                         |
      | John      | Tester   | 123 Test Street | Testville | TS    | 12345 | 5551234567  | EMPTY       | UNIQUE   | Venice12 | Venice12 | Social Security Number is required.           |
      | John      | Tester   | 123 Test Street | Testville | TS    | 12345 | 5551234567  | 123-45-6789 | EMPTY    | Venice12 | Venice12 | Username is required.                         |
      | John      | Tester   | 123 Test Street | Testville | TS    | 12345 | 5551234567  | 123-45-6789 | UNIQUE   | EMPTY    | Venice12 | Password is required.                         |
      | John      | Tester   | 123 Test Street | Testville | TS    | 12345 | 5551234567  | 123-45-6789 | UNIQUE   | Venice12 | EMPTY    | Password Confirmation is required.            |
      | John      | Tester   | 123 Test Street | Testville | TS    | 12345 | 5551234567  | 123-45-6789 | UNIQUE   | Venice12 | wrongPwd | Password is required.                         |


Scenario Outline: Login succeeds with valid credentials
    When I attempt login with "<username>" and "<password>"
    Then I should see Accounts Overview and print the balance

    Examples:
      | username | password   |
      | john     | demo       |

  Scenario Outline: Login validations (errors and edge cases)
    When I attempt login with "<username>" and "<password>"
    Then I should see a login error containing "<expect>"

    Examples:
      | username | password | expect                                           |
      | EMPTY    | EMPTY    | Please enter a username and password.            |
      | baduser  | badpass  | The username and password could not be verified. |
      | baduser  | EMPTY    | Please enter a username and password.            |
      | EMPTY    | badpass  | Please enter a username and password.            |