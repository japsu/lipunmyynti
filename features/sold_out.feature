Feature: A product is sold out
  As a visitor
  I want to order a ticket to Yukicon
  But five hundred others beat me to it
  And now I'm left without.

  Scenario: Sold out products on the ticket phase
    Given there is a product that is sold out
    When I view the tickets phase
    Then the product that is sold out should be marked as such

  Scenario: A product becoming sold out while I am is ordering
    Given there is a product that is not yet sold out
    When I complete my order up to the confirmation phase
    And the product becomes sold out due to another order

    When I try to confirm the order
    Then I should be at the tickets phase
    And there should be a notification stating that a product in my cart has been sold out

  Scenario: A product becoming sold out while I am making a payment
    Given there is a product that is not yet sold out
    When I complete my order up to the confirmation phase
    And I try to confirm the order
    And the product becomes sold out due to another order

    When I complete the payment process
    Then my order should be successfully finished

  # TODO Another opinion was that the reservation should occur at the end of the tickets phase.
  Scenario: My order reserving the last available ticket
    Given there is a product of which there is only one piece left
    When I complete my order up to the confirmation phase
    And I try to confirm the order

    Then the product should be sold out

    When I complete the payment process
    Then my order should be successfully finished   

  Scenario: An unpaid reservation expires after a period of time
    Given there is a product that is not yet sold out
    And I complete my order up to the confirmation phase
    And I abandon the order

    # TODO The length of the period is open for debate.
    When a week has passed
    Then my order should be automatically cancelled
