Feature: log into portal with captcha

  Scenario: log in successfully with captcha
     Given login details
      When username is filled
      And password is filled
      And captcha is filled
      And pressed login button
      Then login is successful
