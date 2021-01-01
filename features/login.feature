Feature: log into portal

  @check_portal
  Scenario: check if portal is reachable
     Given login details
      Then portal is reachable

  @login
  Scenario: log in successfully
     Given login details
      When username is filled
      And password is filled
      And pressed login button
      Then login is successful

  Scenario: log in successfully with captcha
     Given login details
      When username is filled
      And password is filled
      And captcha is filled
      And pressed login button
      Then login is successful
