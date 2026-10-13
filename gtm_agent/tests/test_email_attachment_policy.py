import unittest

from gtm_agent.gtm_agent import SYSTEM_PROMPT, send_prospect_email


class EmailAttachmentPolicyTests(unittest.TestCase):
    def test_document_request_requires_text_only_confirmation_before_sending(self):
        self.assertIn("cannot attach files", SYSTEM_PROMPT)
        self.assertIn("ask whether they want a text-only email instead", SYSTEM_PROMPT)
        self.assertIn("do not send until they confirm", SYSTEM_PROMPT)

    def test_confirmed_text_only_email_cannot_claim_document_delivery(self):
        self.assertIn("After confirmation, send only the agreed text-only email", SYSTEM_PROMPT)
        self.assertIn("in the email body or your reply to the rep", SYSTEM_PROMPT)
        self.assertIn("attached, included, or delivered", SYSTEM_PROMPT)

    def test_ordinary_text_only_email_requests_remain_supported(self):
        self.assertIn("Send ordinary text-only email requests normally", SYSTEM_PROMPT)
        self.assertNotIn("always carry the request through and send the email", SYSTEM_PROMPT)

    def test_send_tool_exposes_no_attachment_argument(self):
        self.assertIn("plain-text email", send_prospect_email.description)
        self.assertIn("cannot attach files", send_prospect_email.description)
        self.assertNotIn("attachment", send_prospect_email.args)


if __name__ == "__main__":
    unittest.main()
