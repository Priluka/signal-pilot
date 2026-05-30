"""Cross-system mock fixtures for external-lookup skills.

A single dictionary tells the story of every plate that any skill might
get asked about. Each plate's entry carries every system's view of that
vehicle, so when the planner asks Graylog + Datatrans + Bmove in
sequence, the numbers line up.

Five plates, five stories:

* ``W-55123K``  — Vienna end-user, Bmove Ticketless. Paid 4.50 € via
                  VISA; Graylog shows AUTH → AUTH_HOLD → SETTLED;
                  Datatrans confirms settled. Customer claims they paid
                  but got a fine — this is the KAN-34 scenario.
* ``W-38702T``  — Vienna, SKIDATA Schwarzenbergplatz. LPR recognised
                  on entry, missed on exit; barrier opened by staff;
                  session left OPEN. Classic stuck-session ticket.
* ``ZG-1234-AB``— Zagreb, ParkIS Zone 2, paid 0.80 € via SMS gateway
                  (HT/T-com). Active session, operator confirmation
                  received.
* ``ZG-7777-XY``— Zagreb Bmove user with EXPIRED card; outstanding
                  debt 12.40 €. Last activity weeks ago.
* ``W-99999A``  — Not in any system. Surface "no data" so the planner
                  learns to handle clean-miss responses.

When Ivan wires real APIs, delete the data structures here; the
``lookup_*`` helpers below are the only entry points the skills hit.
"""
from __future__ import annotations

from typing import Any


# ---------------------------------------------------------------------------
# The shared fixture
# ---------------------------------------------------------------------------


_PLATES: dict[str, dict[str, Any]] = {
    # =======================================================================
    # W-55123K · Vienna · Bmove Ticketless · paid OK · the KAN-34 scenario
    # =======================================================================
    "W-55123K": {
        "bmove": {
            "user_id": "usr-445521",
            "email_masked": "k***@gmail.com",
            "registered": True,
            "vehicles": [{"plate": "W-55123K", "ticketless_enabled": True}],
            "active_sessions": 1,
            "outstanding_debts": 0,
            "payment_method": "VISA ****4821",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-27T14:22:01Z",
        },
        "graylog": [
            {
                "timestamp": "2026-05-27T14:22:01Z",
                "plate": "W-55123K",
                "amount": 4.50,
                "status": "AUTHORIZED",
                "gateway": "datatrans",
                "session_id": "sess-88421",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-27T14:22:03Z",
                "plate": "W-55123K",
                "amount": 4.50,
                "status": "AUTH_HOLD",
                "gateway": "datatrans",
                "session_id": "sess-88421",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-27T14:25:11Z",
                "plate": "W-55123K",
                "amount": 4.50,
                "status": "SETTLED",
                "gateway": "datatrans",
                "session_id": "sess-88421",
                "error_code": None,
            },
        ],
        "datatrans": {
            "sess-88421": {
                "transaction_id": "DT-20260527-882341",
                "amount": 450,
                "currency": "EUR",
                "status": "settled",
                "card_type": "VISA",
                "last4": "4821",
                "3ds_status": "authenticated",
                "settled_at": "2026-05-27T14:25:11Z",
                "refundable": True,
                "error_message": None,
            },
        },
        # No SKIDATA / ParkIS rows — Vienna Bmove Ticketless is a separate flow.
    },

    # =======================================================================
    # W-38702T · Vienna · SKIDATA Schwarzenbergplatz · OPEN stuck session
    # =======================================================================
    "W-38702T": {
        "skidata": {
            "session_id": "SK-2026-991204",
            "plate": "W-38702T",
            "garage": "Schwarzenbergplatz Wien",
            "entry_time": "2026-05-26T14:30:22Z",
            "exit_time": None,
            "status": "OPEN",
            "lpr_entry": "RECOGNIZED",
            "lpr_exit": "NOT_RECOGNIZED",
            "barrier_override": "MANUAL_STAFF",
            "tariff_zone": "Zone A",
            "amount_due": None,
        },
        "graylog": [
            {
                "timestamp": "2026-05-26T14:30:22Z",
                "plate": "W-38702T",
                "amount": None,
                "status": "SESSION_OPENED",
                "gateway": "skidata",
                "session_id": "SK-2026-991204",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-26T18:42:15Z",
                "plate": "W-38702T",
                "amount": None,
                "status": "LPR_EXIT_FAIL",
                "gateway": "skidata",
                "session_id": "SK-2026-991204",
                "error_code": "LPR_NO_MATCH",
            },
            {
                "timestamp": "2026-05-26T18:43:02Z",
                "plate": "W-38702T",
                "amount": None,
                "status": "BARRIER_MANUAL_OPEN",
                "gateway": "skidata",
                "session_id": "SK-2026-991204",
                "error_code": None,
            },
        ],
    },

    # =======================================================================
    # ZG-1234-AB · Zagreb · ParkIS Zone 2 · SMS payment OK
    # =======================================================================
    "ZG-1234-AB": {
        "parkis": {
            "transaction_id": "TXN-2026-445812",
            "plate": "ZG-1234-AB",
            "zone": "Zagreb Zone 2",
            "start_time": "2026-05-27T09:15:00Z",
            "end_time": "2026-05-27T10:15:00Z",
            "amount": 0.80,
            "payment_method": "SMS",
            "operator_confirmation": "RECEIVED",
            "status": "ACTIVE",
            "sms_gateway": "HT/T-com",
        },
        "graylog": [
            {
                "timestamp": "2026-05-27T09:14:58Z",
                "plate": "ZG-1234-AB",
                "amount": 0.80,
                "status": "SMS_RECEIVED",
                "gateway": "parkis",
                "session_id": "TXN-2026-445812",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-27T09:15:01Z",
                "plate": "ZG-1234-AB",
                "amount": 0.80,
                "status": "AUTHORIZED",
                "gateway": "parkis",
                "session_id": "TXN-2026-445812",
                "error_code": None,
            },
        ],
    },

    # =======================================================================
    # ZG-7777-XY · Zagreb · Bmove user · EXPIRED card · debt outstanding
    # =======================================================================
    "ZG-7777-XY": {
        "bmove": {
            "user_id": "usr-991834",
            "email_masked": "m***@yahoo.com",
            "registered": True,
            "vehicles": [{"plate": "ZG-7777-XY", "ticketless_enabled": False}],
            "active_sessions": 0,
            "outstanding_debts": 12.40,
            "payment_method": "VISA ****0192",
            "card_status": "EXPIRED",
            "last_activity": "2026-05-08T11:04:00Z",
        },
        "graylog": [
            {
                "timestamp": "2026-05-08T11:03:55Z",
                "plate": "ZG-7777-XY",
                "amount": 12.40,
                "status": "FAILED",
                "gateway": "datatrans",
                "session_id": "sess-77321",
                "error_code": "CARD_EXPIRED",
            },
        ],
        "datatrans": {
            "sess-77321": {
                "transaction_id": "DT-20260508-661120",
                "amount": 1240,
                "currency": "EUR",
                "status": "failed",
                "card_type": "VISA",
                "last4": "0192",
                "3ds_status": "skipped",
                "settled_at": None,
                "refundable": False,
                "error_message": "card_expired: tokenized card past expiry date",
            },
        },
    },

    # =======================================================================
    # W-12345B · Zagreb · rental car · drove through Kaptol garage, charged
    # minimum (2.50 EUR) even though they never actually parked.
    # =======================================================================
    "W-12345B": {
        "bmove": {
            "user_id": "usr-771203",
            "email_masked": "t***@rental.com",
            "registered": True,
            "vehicles": [{"plate": "W-12345B", "ticketless_enabled": True}],
            "active_sessions": 0,
            "outstanding_debts": 0,
            "payment_method": "VISA ****9012",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-28T10:05:30Z",
        },
        "skidata": {
            "session_id": "SK-2026-554477",
            "plate": "W-12345B",
            "garage": "Kaptol Center Zagreb",
            "entry_time": "2026-05-28T10:00:12Z",
            "exit_time": "2026-05-28T10:05:08Z",
            "status": "CLOSED",
            "lpr_entry": "RECOGNIZED",
            "lpr_exit": "RECOGNIZED",
            "barrier_override": "NONE",
            "tariff_zone": "Zone A",
            "amount_due": 2.50,
        },
        "graylog": [
            {
                "timestamp": "2026-05-28T10:00:12Z",
                "plate": "W-12345B",
                "amount": None,
                "status": "SESSION_OPENED",
                "gateway": "skidata",
                "session_id": "SK-2026-554477",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-28T10:05:08Z",
                "plate": "W-12345B",
                "amount": 2.50,
                "status": "SESSION_CLOSED",
                "gateway": "skidata",
                "session_id": "SK-2026-554477",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-28T10:05:30Z",
                "plate": "W-12345B",
                "amount": 2.50,
                "status": "CHARGE_AUTHORIZED",
                "gateway": "datatrans",
                "session_id": "sess-12345",
                "error_code": None,
            },
        ],
        "datatrans": {
            "sess-12345": {
                "transaction_id": "DT-20260528-101010",
                "amount": 250,
                "currency": "EUR",
                "status": "settled",
                "card_type": "VISA",
                "last4": "9012",
                "3ds_status": "authenticated",
                "settled_at": "2026-05-28T10:05:45Z",
                "refundable": True,
                "error_message": None,
            },
        },
    },

    # =======================================================================
    # SK-334AB · Slovak plate · LPR couldn't read foreign format, barrier
    # blocked, customer had to use the intercom.
    # =======================================================================
    "SK-334AB": {
        "bmove": {
            "user_id": "usr-883099",
            "email_masked": "p***@gmail.com",
            "registered": True,
            "vehicles": [{"plate": "SK-334AB", "ticketless_enabled": True}],
            "active_sessions": 0,
            "outstanding_debts": 0,
            "payment_method": "MASTERCARD ****6677",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-28T11:42:01Z",
        },
        "skidata": {
            "session_id": "SK-2026-771155",
            "plate": "SK-334AB",
            "garage": "Schwarzenbergplatz Wien",
            "entry_time": "2026-05-28T11:40:15Z",
            "exit_time": None,
            "status": "BLOCKED",
            "lpr_entry": "NOT_RECOGNIZED",
            "lpr_exit": None,
            "barrier_override": "NONE",
            "tariff_zone": "Zone A",
            "amount_due": None,
        },
        "graylog": [
            {
                "timestamp": "2026-05-28T11:40:15Z",
                "plate": "SK-334AB",
                "amount": None,
                "status": "LPR_FAIL",
                "gateway": "skidata",
                "session_id": "SK-2026-771155",
                "error_code": "LPR_FOREIGN_FORMAT",
            },
            {
                "timestamp": "2026-05-28T11:40:16Z",
                "plate": "SK-334AB",
                "amount": None,
                "status": "BARRIER_BLOCKED",
                "gateway": "skidata",
                "session_id": "SK-2026-771155",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-28T11:42:01Z",
                "plate": "SK-334AB",
                "amount": None,
                "status": "USER_INTERCOM_CALL",
                "gateway": "skidata",
                "session_id": "SK-2026-771155",
                "error_code": None,
            },
        ],
    },

    # =======================================================================
    # I-AM442RR · Italian B2B partner · monthly invoice request · Bologna
    # garage, 3 settled sessions in the last 7 days.
    # =======================================================================
    "I-AM442RR": {
        "bmove": {
            "user_id": "biz-IT-44291",
            "email_masked": "a***@parcheggi-italia.it",
            "registered": True,
            "account_type": "B2B",
            "company_name": "Parcheggi Italia SRL",
            "vat_id": "IT04482103651",
            "vehicles": [{"plate": "I-AM442RR", "ticketless_enabled": True}],
            "active_sessions": 0,
            "outstanding_debts": 0,
            "payment_method": "VISA ****0033",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-27T16:12:44Z",
        },
        "skidata": {
            "session_id": "SK-2026-IT-003",
            "plate": "I-AM442RR",
            "garage": "Bologna Centro",
            "entry_time": "2026-05-27T14:00:00Z",
            "exit_time": "2026-05-27T16:12:44Z",
            "status": "CLOSED",
            "lpr_entry": "RECOGNIZED",
            "lpr_exit": "RECOGNIZED",
            "barrier_override": "NONE",
            "tariff_zone": "Zone B",
            "amount_due": 15.00,
            "recent_sessions_count": 3,
        },
        "graylog": [
            {
                "timestamp": "2026-05-23T09:11:02Z",
                "plate": "I-AM442RR",
                "amount": 12.00,
                "status": "SETTLED",
                "gateway": "datatrans",
                "session_id": "sess-IT-001",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-25T13:22:30Z",
                "plate": "I-AM442RR",
                "amount": 8.50,
                "status": "SETTLED",
                "gateway": "datatrans",
                "session_id": "sess-IT-002",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-27T16:12:44Z",
                "plate": "I-AM442RR",
                "amount": 15.00,
                "status": "SETTLED",
                "gateway": "datatrans",
                "session_id": "sess-IT-003",
                "error_code": None,
            },
        ],
        "datatrans": {
            "sess-IT-001": {
                "transaction_id": "DT-20260523-IT00001",
                "amount": 1200,
                "currency": "EUR",
                "status": "settled",
                "card_type": "VISA",
                "last4": "0033",
                "3ds_status": "authenticated",
                "settled_at": "2026-05-23T09:11:15Z",
                "refundable": True,
                "error_message": None,
            },
            "sess-IT-002": {
                "transaction_id": "DT-20260525-IT00002",
                "amount": 850,
                "currency": "EUR",
                "status": "settled",
                "card_type": "VISA",
                "last4": "0033",
                "3ds_status": "authenticated",
                "settled_at": "2026-05-25T13:22:50Z",
                "refundable": True,
                "error_message": None,
            },
            "sess-IT-003": {
                "transaction_id": "DT-20260527-IT00003",
                "amount": 1500,
                "currency": "EUR",
                "status": "settled",
                "card_type": "VISA",
                "last4": "0033",
                "3ds_status": "authenticated",
                "settled_at": "2026-05-27T16:13:01Z",
                "refundable": True,
                "error_message": None,
            },
        },
    },

    # =======================================================================
    # W-88211C · refund already processed 3 days ago — customer is
    # asking for something that has already happened.
    # =======================================================================
    "W-88211C": {
        "bmove": {
            "user_id": "usr-882211",
            "email_masked": "g***@hotmail.com",
            "registered": True,
            "vehicles": [{"plate": "W-88211C", "ticketless_enabled": True}],
            "active_sessions": 0,
            "outstanding_debts": 0,
            "payment_method": "VISA ****3344",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-25T15:30:00Z",
        },
        "skidata": {
            "session_id": "SK-2026-882211",
            "plate": "W-88211C",
            "garage": "Millennium City Wien",
            "entry_time": "2026-05-25T13:00:11Z",
            "exit_time": "2026-05-25T14:55:02Z",
            "status": "CLOSED",
            "lpr_entry": "RECOGNIZED",
            "lpr_exit": "RECOGNIZED",
            "barrier_override": "NONE",
            "tariff_zone": "Zone A",
            "amount_due": 4.50,
        },
        "graylog": [
            {
                "timestamp": "2026-05-25T14:55:02Z",
                "plate": "W-88211C",
                "amount": 4.50,
                "status": "CHARGE_AUTHORIZED",
                "gateway": "datatrans",
                "session_id": "sess-88211",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-25T14:55:30Z",
                "plate": "W-88211C",
                "amount": 4.50,
                "status": "SETTLED",
                "gateway": "datatrans",
                "session_id": "sess-88211",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-25T15:28:00Z",
                "plate": "W-88211C",
                "amount": 4.50,
                "status": "REFUND_INITIATED",
                "gateway": "datatrans",
                "session_id": "sess-88211",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-25T15:30:00Z",
                "plate": "W-88211C",
                "amount": 4.50,
                "status": "REFUND_COMPLETED",
                "gateway": "datatrans",
                "session_id": "sess-88211",
                "error_code": None,
            },
        ],
        "datatrans": {
            "sess-88211": {
                "transaction_id": "DT-20260525-882211",
                "amount": 450,
                "currency": "EUR",
                "status": "refunded",
                "card_type": "VISA",
                "last4": "3344",
                "3ds_status": "authenticated",
                "settled_at": "2026-05-25T14:55:30Z",
                "refunded_at": "2026-05-25T15:30:00Z",
                "refundable": False,
                "error_message": None,
            },
        },
    },

    # =======================================================================
    # ZG-9988-CD · fleet user (3 vehicles) · 2 concurrent SMS payments
    # the same morning · sibling plate ZG-1122-FF also has an entry below.
    # =======================================================================
    "ZG-9988-CD": {
        "bmove": {
            "user_id": "usr-fleet-998",
            "email_masked": "f***@firma.hr",
            "registered": True,
            "vehicles": [
                {"plate": "ZG-9988-CD", "ticketless_enabled": True},
                {"plate": "ZG-9988-CE", "ticketless_enabled": True},
                {"plate": "ZG-1122-FF", "ticketless_enabled": True},
            ],
            "active_sessions": 2,
            "outstanding_debts": 0,
            "payment_method": "VISA ****5544",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-28T10:01:18Z",
        },
        "parkis": {
            "transaction_id": "TXN-2026-998801",
            "plate": "ZG-9988-CD",
            "zone": "Zagreb Zone 1",
            "start_time": "2026-05-28T10:00:00Z",
            "end_time": "2026-05-28T12:00:00Z",
            "amount": 1.60,
            "payment_method": "SMS",
            "operator_confirmation": "RECEIVED",
            "status": "ACTIVE",
            "sms_gateway": "HT/T-com",
        },
        "graylog": [
            {
                "timestamp": "2026-05-28T10:00:00Z",
                "plate": "ZG-9988-CD",
                "amount": 1.60,
                "status": "SMS_RECEIVED",
                "gateway": "parkis",
                "session_id": "TXN-2026-998801",
                "error_code": None,
            },
        ],
    },

    # Sibling plate of ZG-9988-CD's fleet user — listed so a plate-keyed
    # bmove_user_lookup against ZG-1122-FF returns the same fleet record.
    "ZG-1122-FF": {
        "bmove": {
            "user_id": "usr-fleet-998",
            "email_masked": "f***@firma.hr",
            "registered": True,
            "vehicles": [
                {"plate": "ZG-9988-CD", "ticketless_enabled": True},
                {"plate": "ZG-9988-CE", "ticketless_enabled": True},
                {"plate": "ZG-1122-FF", "ticketless_enabled": True},
            ],
            "active_sessions": 2,
            "outstanding_debts": 0,
            "payment_method": "VISA ****5544",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-28T10:01:18Z",
        },
        "parkis": {
            "transaction_id": "TXN-2026-112201",
            "plate": "ZG-1122-FF",
            "zone": "Zagreb Zone 2",
            "start_time": "2026-05-28T10:01:00Z",
            "end_time": "2026-05-28T11:01:00Z",
            "amount": 0.80,
            "payment_method": "SMS",
            "operator_confirmation": "RECEIVED",
            "status": "ACTIVE",
            "sms_gateway": "HT/T-com",
        },
        "graylog": [
            {
                "timestamp": "2026-05-28T10:01:00Z",
                "plate": "ZG-1122-FF",
                "amount": 0.80,
                "status": "SMS_RECEIVED",
                "gateway": "parkis",
                "session_id": "TXN-2026-112201",
                "error_code": None,
            },
        ],
    },

    # =======================================================================
    # DE-MH-5521 · German plate, Zagreb cross-border · SMS rejected
    # (foreign number), customer paid via app but parking already expired.
    # =======================================================================
    "DE-MH-5521": {
        "bmove": {
            "user_id": "usr-552100",
            "email_masked": "h***@web.de",
            "registered": True,
            "vehicles": [{"plate": "DE-MH-5521", "ticketless_enabled": True}],
            "active_sessions": 0,
            "outstanding_debts": 0,
            "payment_method": "VISA ****7711",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-28T14:33:08Z",
        },
        "parkis": {
            "transaction_id": "TXN-2026-552100",
            "plate": "DE-MH-5521",
            "zone": "Zagreb Zone 1",
            "start_time": "2026-05-28T13:30:00Z",
            "end_time": "2026-05-28T14:30:00Z",
            "amount": 1.60,
            "payment_method": "APP",
            "operator_confirmation": "RECEIVED",
            "status": "EXPIRED",
            "sms_gateway": None,
        },
        "graylog": [
            {
                "timestamp": "2026-05-28T13:30:12Z",
                "plate": "DE-MH-5521",
                "amount": 1.60,
                "status": "SMS_PAYMENT_ATTEMPT",
                "gateway": "parkis",
                "session_id": "TXN-2026-552100",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-28T13:30:13Z",
                "plate": "DE-MH-5521",
                "amount": 1.60,
                "status": "SMS_FAILED",
                "gateway": "parkis",
                "session_id": "TXN-2026-552100",
                "error_code": "FOREIGN_NUMBER_UNSUPPORTED",
            },
            {
                "timestamp": "2026-05-28T14:33:08Z",
                "plate": "DE-MH-5521",
                "amount": 1.60,
                "status": "APP_PAYMENT_SUCCESS",
                "gateway": "parkis",
                "session_id": "TXN-2026-552100",
                "error_code": None,
            },
        ],
    },

    # =======================================================================
    # W-44556D · 3 months of accumulated debt because the card expired
    # and nobody updated it. SKIDATA has 3 DEBT sessions to match.
    # =======================================================================
    "W-44556D": {
        "bmove": {
            "user_id": "usr-445560",
            "email_masked": "d***@web.de",
            "registered": True,
            "vehicles": [{"plate": "W-44556D", "ticketless_enabled": True}],
            "active_sessions": 0,
            "outstanding_debts": 34.20,
            "outstanding_debts_count": 3,
            "debts": [
                {
                    "session_id": "SK-2026-OLD-001",
                    "amount": 12.40,
                    "date": "2026-02-28",
                },
                {
                    "session_id": "SK-2026-OLD-002",
                    "amount": 8.30,
                    "date": "2026-03-28",
                },
                {
                    "session_id": "SK-2026-OLD-003",
                    "amount": 13.50,
                    "date": "2026-04-28",
                },
            ],
            "payment_method": "VISA ****7890",
            "card_status": "EXPIRED",
            "last_activity": "2026-04-28T16:00:00Z",
        },
        "skidata": {
            "session_id": "SK-2026-OLD-003",
            "plate": "W-44556D",
            "garage": "Millennium City Wien",
            "entry_time": "2026-04-28T13:30:00Z",
            "exit_time": "2026-04-28T16:00:00Z",
            "status": "DEBT",
            "lpr_entry": "RECOGNIZED",
            "lpr_exit": "RECOGNIZED",
            "barrier_override": "NONE",
            "tariff_zone": "Zone A",
            "amount_due": 13.50,
        },
        "graylog": [
            {
                "timestamp": "2026-02-28T15:00:00Z",
                "plate": "W-44556D",
                "amount": 12.40,
                "status": "CHARGE_FAILED",
                "gateway": "datatrans",
                "session_id": "sess-OLD-001",
                "error_code": "CARD_EXPIRED",
            },
            {
                "timestamp": "2026-03-28T15:00:00Z",
                "plate": "W-44556D",
                "amount": 8.30,
                "status": "CHARGE_FAILED",
                "gateway": "datatrans",
                "session_id": "sess-OLD-002",
                "error_code": "CARD_EXPIRED",
            },
            {
                "timestamp": "2026-04-28T16:00:00Z",
                "plate": "W-44556D",
                "amount": 13.50,
                "status": "CHARGE_FAILED",
                "gateway": "datatrans",
                "session_id": "sess-OLD-003",
                "error_code": "CARD_EXPIRED",
            },
        ],
        "datatrans": {
            "sess-OLD-001": {
                "transaction_id": "DT-20260228-OLD0001",
                "amount": 1240,
                "currency": "EUR",
                "status": "failed",
                "card_type": "VISA",
                "last4": "7890",
                "3ds_status": "skipped",
                "settled_at": None,
                "refundable": False,
                "error_message": "card_expired",
            },
            "sess-OLD-002": {
                "transaction_id": "DT-20260328-OLD0002",
                "amount": 830,
                "currency": "EUR",
                "status": "failed",
                "card_type": "VISA",
                "last4": "7890",
                "3ds_status": "skipped",
                "settled_at": None,
                "refundable": False,
                "error_message": "card_expired",
            },
            "sess-OLD-003": {
                "transaction_id": "DT-20260428-OLD0003",
                "amount": 1350,
                "currency": "EUR",
                "status": "failed",
                "card_type": "VISA",
                "last4": "7890",
                "3ds_status": "skipped",
                "settled_at": None,
                "refundable": False,
                "error_message": "card_expired",
            },
        },
    },

    # =======================================================================
    # HR-ZD-442 · Zadar · customer bought wrong zone (paid Zone 3,
    # actually parked in Zone 1). No Bmove record — pure ParkIS / SMS.
    # =======================================================================
    "HR-ZD-442": {
        "parkis": {
            "transaction_id": "TXN-2026-ZD-442",
            "plate": "HR-ZD-442",
            "zone": "Zadar Zone 3",
            "start_time": "2026-05-28T09:00:00Z",
            "end_time": "2026-05-28T10:00:00Z",
            "amount": 0.60,
            "payment_method": "SMS",
            "operator_confirmation": "RECEIVED",
            "status": "ACTIVE",
            "sms_gateway": "HT",
            "gps_location": "Zadar Zone 1",
            "gps_zone_mismatch": True,
        },
        "graylog": [
            {
                "timestamp": "2026-05-28T09:00:00Z",
                "plate": "HR-ZD-442",
                "amount": 0.60,
                "status": "SMS_RECEIVED",
                "gateway": "parkis",
                "session_id": "TXN-2026-ZD-442",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-28T09:00:05Z",
                "plate": "HR-ZD-442",
                "amount": None,
                "status": "GPS_ZONE_MISMATCH",
                "gateway": "parkis",
                "session_id": "TXN-2026-ZD-442",
                "error_code": "ZONE_MISMATCH_3_VS_1",
            },
        ],
    },

    # =======================================================================
    # W-77123E · Ticketless DISABLED — customer expects the barrier
    # to open automatically, but the flag was never turned on. SKIDATA
    # therefore has no session entry.
    # =======================================================================
    "W-77123E": {
        "bmove": {
            "user_id": "usr-771230",
            "email_masked": "n***@gmx.at",
            "registered": True,
            "vehicles": [{"plate": "W-77123E", "ticketless_enabled": False}],
            "active_sessions": 0,
            "outstanding_debts": 0,
            "payment_method": "MASTERCARD ****8855",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-26T12:00:00Z",
        },
        # No skidata / graylog / datatrans entries — the whole point of
        # the story is that the system never even saw this car at the
        # garage because Ticketless isn't enabled on the account.
    },

    # =======================================================================
    # ZG-5555-MN · everything is fine; customer just didn't get the
    # confirmation SMS, so they're asking unnecessarily.
    # =======================================================================
    "ZG-5555-MN": {
        "bmove": {
            "user_id": "usr-555500",
            "email_masked": "s***@gmail.com",
            "registered": True,
            "vehicles": [{"plate": "ZG-5555-MN", "ticketless_enabled": True}],
            "active_sessions": 1,
            "outstanding_debts": 0,
            "payment_method": "MASTERCARD ****1234",
            "card_status": "ACTIVE",
            "last_activity": "2026-05-28T08:15:00Z",
        },
        "parkis": {
            "transaction_id": "TXN-2026-555500",
            "plate": "ZG-5555-MN",
            "zone": "Zagreb Zone 2",
            "start_time": "2026-05-28T08:15:00Z",
            "end_time": "2026-05-28T09:15:00Z",
            "amount": 0.80,
            "payment_method": "SMS",
            "operator_confirmation": "CONFIRMED",
            "status": "ACTIVE",
            "sms_gateway": "HT/T-com",
        },
        "graylog": [
            {
                "timestamp": "2026-05-28T08:15:00Z",
                "plate": "ZG-5555-MN",
                "amount": 0.80,
                "status": "SMS_RECEIVED",
                "gateway": "parkis",
                "session_id": "TXN-2026-555500",
                "error_code": None,
            },
            {
                "timestamp": "2026-05-28T08:15:03Z",
                "plate": "ZG-5555-MN",
                "amount": 0.80,
                "status": "PAYMENT_CONFIRMED",
                "gateway": "parkis",
                "session_id": "TXN-2026-555500",
                "error_code": None,
            },
        ],
    },
}


# Extra fixtures used by lookups that scan all rows (e.g. Graylog
# free-text search). Plates above are the canonical stories; these add
# realistic noise so a query that doesn't filter by plate returns >1
# row from genuinely different sessions.
_GRAYLOG_EXTRA: list[dict[str, Any]] = [
    {
        "timestamp": "2026-05-27T08:01:12Z",
        "plate": "ZG-5562-CD",
        "amount": 1.20,
        "status": "SETTLED",
        "gateway": "datatrans",
        "session_id": "sess-88002",
        "error_code": None,
    },
    {
        "timestamp": "2026-05-27T11:44:23Z",
        "plate": "ST-1010-PA",
        "amount": 2.40,
        "status": "AUTHORIZED",
        "gateway": "parkis",
        "session_id": "TXN-2026-445999",
        "error_code": None,
    },
]


# ---------------------------------------------------------------------------
# Lookup helpers — single entry points per system
# ---------------------------------------------------------------------------


def lookup_bmove(*, plate: str | None = None, email: str | None = None) -> dict[str, Any] | None:
    if plate:
        row = _PLATES.get(plate.upper(), {}).get("bmove")
        return dict(row) if row else None
    if email:
        for data in _PLATES.values():
            row = data.get("bmove")
            if row and row.get("email_masked", "").lower().startswith(email.lower()[:1]):
                # Cheap masked-email match — real implementation will hash.
                return dict(row)
    return None


def lookup_parkis(
    *,
    plate: str,
    zone: str | None = None,
    date: str | None = None,  # noqa: ARG001 — placeholder for real API
) -> dict[str, Any] | None:
    row = _PLATES.get(plate.upper(), {}).get("parkis")
    if not row:
        return None
    if zone and zone.lower() not in (row.get("zone") or "").lower():
        return None
    return dict(row)


def lookup_skidata(*, plate: str, garage: str | None = None) -> dict[str, Any] | None:
    row = _PLATES.get(plate.upper(), {}).get("skidata")
    if not row:
        return None
    if garage and garage.lower() not in (row.get("garage") or "").lower():
        return None
    return dict(row)


def lookup_datatrans(*, reference: str) -> dict[str, Any] | None:
    # reference can be a session id or a transaction id; index both ways.
    for data in _PLATES.values():
        bucket = data.get("datatrans", {})
        if reference in bucket:
            return dict(bucket[reference])
        for tx in bucket.values():
            if tx.get("transaction_id") == reference:
                return dict(tx)
    return None


def search_graylog(
    *,
    query: str,
    limit: int = 25,
) -> list[dict[str, Any]]:
    """Tiny subset of the Graylog query language — supports ``plate:VAL``,
    ``status:VAL``, ``gateway:VAL`` filters joined by ``AND`` or whitespace.
    Anything else is ignored. Real implementation talks to the
    ``/api/search/messages`` endpoint."""
    filters = _parse_graylog_query(query)
    rows: list[dict[str, Any]] = []
    for data in _PLATES.values():
        rows.extend(data.get("graylog") or [])
    rows.extend(_GRAYLOG_EXTRA)

    def _matches(row: dict[str, Any]) -> bool:
        for key, value in filters.items():
            if key == "plate" and (row.get("plate") or "").upper() != value.upper():
                return False
            if key == "status" and (row.get("status") or "").lower() != value.lower():
                return False
            if key == "gateway" and (row.get("gateway") or "").lower() != value.lower():
                return False
        return True

    rows = [r for r in rows if _matches(r)]
    rows.sort(key=lambda r: r.get("timestamp") or "")
    return rows[:limit]


def _parse_graylog_query(query: str) -> dict[str, str]:
    """Pull out simple ``key:VAL`` pairs. Operator words (AND/OR) are
    discarded — we treat everything as AND."""
    import re

    filters: dict[str, str] = {}
    for match in re.finditer(r"(\w+):([^\s\"]+)", query):
        key, value = match.group(1).lower(), match.group(2)
        filters[key] = value
    return filters
