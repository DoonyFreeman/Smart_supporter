CLASSIFICATION_PROMPT = """You are a tech support triage agent. Analyze the following ticket and classify it.

Ticket: {title}
Description: {description}

Similar past tickets: {similar_tickets}
Related FAQ articles: {faq_articles}

Choose exactly one category:
- faq_match — the issue is solved by an FAQ article
- bug — a backend/system bug
- feature_request — a request for a new feature
- needs_info — not enough information to classify

Respond with only the category name."""

ROUTING_PROMPT = """You are a tech support triage agent. Classify this bug ticket.

Ticket: {title}
Description: {description}

Return a JSON with three fields:
- category: one of [Database, API, Reports, Auth, UI, Network, Other]
- priority: one of [low, medium, high, critical]
- assigned_team: one of [backend-db, backend-api, frontend, infra]

Respond with only the JSON."""

RESPONSE_PROMPT = """You are a tech support agent. Write a helpful response to the customer.

Ticket: {title}
Description: {description}

Type: {ticket_type}
FAQ reference: {faq_content}

Write a professional, empathetic response in the same language as the ticket.
If the type is faq_match, include step-by-step instructions from the FAQ.
If the type is bug/feature_request, acknowledge the issue and provide an ETA estimate."""
