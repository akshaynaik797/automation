Feature: log into portal

  Scenario: log in successfully
     Given login details
      When username is filled
      And password is filled
      And pressed login button
      Then login is successful

