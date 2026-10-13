import os
import unittest
from unittest.mock import patch

os.environ.setdefault("OPENAI_API_KEY", "test-key")

from gtm_agent.gtm_agent import SYSTEM_PROMPT, send_prospect_email


class SendProspectEmailTests(unittest.TestCase):
    def call_tool(self, prospect):
        return send_prospect_email.func(
            prospect=prospect,
            subject="Follow up",
            body="Hello",
            runtime=None,
            from_rep={},
        )

    def test_blocks_disqualified_source_record_without_sending(self):
        prospect = {"prospect_id": "LEAD-1", "email": "lead@example.com"}
        with (
            patch("gtm_agent.gtm_agent.data_service.get_prospect_record", return_value={"disqualified": True}),
            patch("gtm_agent.gtm_agent.uuid.uuid4") as uuid4,
        ):
            result = self.call_tool(prospect)

        self.assertEqual(
            result,
            {"status": "blocked", "error": "Prospect is disqualified; email not sent."},
        )
        uuid4.assert_not_called()

    def test_falls_back_to_disqualified_passed_prospect(self):
        prospect = {
            "prospect_id": "LEAD-1",
            "email": "lead@example.com",
            "disqualified": True,
        }
        with (
            patch("gtm_agent.gtm_agent.data_service.get_prospect_record", return_value=None),
            patch("gtm_agent.gtm_agent.uuid.uuid4") as uuid4,
        ):
            result = self.call_tool(prospect)

        self.assertEqual(
            result,
            {"status": "blocked", "error": "Prospect is disqualified; email not sent."},
        )
        uuid4.assert_not_called()

    def test_sends_when_source_record_is_not_disqualified(self):
        prospect = {
            "prospect_id": "LEAD-1",
            "name": "Prospect",
            "email": "lead@example.com",
        }
        with patch(
            "gtm_agent.gtm_agent.data_service.get_prospect_record",
            return_value={"disqualified": False},
        ):
            result = self.call_tool(prospect)

        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["to"], "lead@example.com")
        self.assertEqual(result["to_name"], "Prospect")
        self.assertEqual(result["subject"], "Follow up")
        self.assertEqual(result["body"], "Hello")

    def test_keeps_missing_email_behavior(self):
        prospect = {"prospect_id": "LEAD-1"}
        with patch(
            "gtm_agent.gtm_agent.data_service.get_prospect_record",
            return_value={"disqualified": False},
        ):
            result = self.call_tool(prospect)

        self.assertEqual(
            result,
            {"status": "failed", "error": "Prospect record has no email address."},
        )

    def test_prompt_checks_and_explains_disqualification(self):
        prompt = SYSTEM_PROMPT.lower()

        self.assertIn("get_prospect", prompt)
        self.assertIn("disqualified is true", prompt)
        self.assertIn("do not call send_prospect_email", prompt)
        self.assertIn("tell the rep", prompt)
        self.assertIn("that the prospect is disqualified", prompt)
        self.assertNotIn("always carry the request", prompt)
        self.assertNotIn("complete the email", prompt)


if __name__ == "__main__":
    unittest.main()
