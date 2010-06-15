ALTER TABLE ticket_sales_product ADD requires_shipping BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE ticket_sales_product ADD includes_ticket BOOLEAN NOT NULL DEFAULT TRUE;
