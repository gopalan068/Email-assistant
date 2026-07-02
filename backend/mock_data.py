# Default fallback mock data
DEFAULT_MOCK_INBOX = {
  "1": {
    "from": "Bank of India",
    "email": "notifications@bankofindia.co.in",
    "date": "August 2, 2026",
    "subject": "Loan repayment reminder",
    "meta": "Inbox / Finance",
    "isAiFlagged": True,
    "aiStatus": "IMPORTANT",
    "body": "Dear Customer,\n\nThis is a friendly reminder that your monthly Home Loan EMI payment of \u20b924,500 (Account ending in *8824) is scheduled for auto-debit on August 5, 2026.\n\nPlease ensure your account maintains a sufficient balance prior to the debit date to avoid any late payment fees, bounce penalties, or credit score adjustments.\n\nIf you have already made the transfer, please disregard this automated notification.\n\nWarm regards,\nRetail Lending Operations\nBank of India",
    "aiReply": "Log confirmation: Checked balance (current: \u20b942,100). Auto-repayment scheduled. Remind me again on Aug 4."
  },
  "2": {
    "from": "Meera (Manager)",
    "email": "meera.sharma@corp.com",
    "date": "August 2, 2026 (10:15 AM)",
    "subject": "Urgent: Q3 review slides",
    "meta": "Inbox / Work",
    "isAiFlagged": False,
    "aiStatus": "DIRECT CORRESPONDENCE",
    "body": "Hi Rahul,\n\nHope you are having a productive week.\n\nThe leadership team has moved the Q3 Business Review meeting up to Thursday morning. Because of this schedule shift, I need to compile all team slides by this evening.\n\nCould you please share your draft Q3 slides by EOD today? Let me know if you need any assistance compiling the customer satisfaction charts.\n\nThanks,\nMeera",
    "aiReply": "Hi Meera,\n\nI am finalizing the Q3 slide deck and customer satisfaction charts now. I will have it uploaded and shared with you by 5:00 PM today. Let me know if you want to do a quick sync before the review.\n\nBest,\nRahul"
  },
  "3": {
    "from": "Freelance Client",
    "email": "billing@indiedesigns.studio",
    "date": "August 1, 2026",
    "subject": "Invoice #INV-204 payment sent",
    "meta": "Inbox / Payment",
    "isAiFlagged": False,
    "aiStatus": "PAYMENT INBOUND",
    "body": "Hi Rahul,\n\nJust a quick update that I've processed the payment for Invoice #INV-204 ($1,200) for the landing page project today.\n\nIt has been sent via bank wire, so it should reflect in your account within the next 2-3 business days depending on interbank processing speeds.\n\nLet me know once you see it on your end. It was absolute pleasure working with you on this launch!\n\nBest regards,\nSarah K.",
    "aiReply": "Hi Sarah,\n\nThank you for processing the payment for invoice #INV-204. I will monitor my account and confirm as soon as the funds clear. It was a pleasure working with you on the landing page project as well!\n\nBest regards,\nRahul"
  },
  "4": {
    "from": "Dentist Clinic",
    "email": "reception@pearlywhites.com",
    "date": "August 1, 2026",
    "subject": "Appointment tomorrow at 11 AM",
    "meta": "Inbox / Health",
    "isAiFlagged": False,
    "aiStatus": "SCHEDULED EVENT",
    "body": "Dear Rahul,\n\nThis is a friendly reminder of your upcoming dental appointment tomorrow, August 3, at 11:00 AM at Pearly Whites Dental Clinic.\n\nYour session is scheduled for a routine cleaning and general checkup with Dr. Roy. Please try to arrive about 10 minutes early to check-in at reception.\n\nIf you need to reschedule or cancel, please call us at least 12 hours in advance.\n\nSincerely,\nPearly Whites Dental Team",
    "aiReply": "Hi Pearly Whites Team,\n\nThank you for the reminder. I confirm that I will be arriving tomorrow at 11:00 AM for my checkup with Dr. Roy.\n\nBest,\nRahul"
  },
  "5": {
    "from": "winbig@lottery.xyz",
    "email": "claims-department@winbiglottery.xyz",
    "date": "July 30, 2026",
    "subject": "\ud83c\udf89 You won $5,000,000!",
    "meta": "Spam / Phishing",
    "isAiFlagged": True,
    "aiStatus": "AUTO-BLOCKED / PHISHING",
    "body": "DEAR LUCKY WINNER,\n\nYOUR EMAIL ADDRESS HAS WON THE GRAND PRIZE OF FIVE MILLION DOLLARS ($5,000,000.00) IN THE GLOBAL EMAIL LOTTERY SWEEPSTAKES RUN BY THE TRUSTEES.\n\nTO CLAIM YOUR PRIZE IMMEDIATELY, PLEASE CLICK ON THE SECURE LINK BELOW AND FILL OUT YOUR BANK ROUTING DETAILS AND SCAN OF PASSPORT:\n\nhttp://suspicious-link-to-steal-your-identity.xyz/claim-prize\n\nDO NOT SHARE THIS EMAIL WITH ANYONE TO PREVENT DOUBLE CLAIMS.\n\nYours faithfully,\nLottery Claims Committee",
    "aiReply": "Action Logged: No response recommended. This is a phishing scam. Auto-reported to security and blacklisted."
  },
  "6": {
    "from": "cheapmeds@discount.net",
    "email": "deals@cheapmeds-discount.net",
    "date": "July 29, 2026",
    "subject": "70% OFF all medicines \ud83d\udc8a",
    "meta": "Spam / Commercial",
    "isAiFlagged": True,
    "aiStatus": "AUTO-BLOCKED / SCAM",
    "body": "HELLO FRIEND!\n\nSAVE BIG TODAY ON ALL YOUR ESSENTIAL MEDICINES. WE OFFER 70% DISCOUNT ON ALL POPULAR PHARMACEUTICAL BRANDS!\n\n- NO PRESCRIPTIONS REQUIRED\n- 100% DISCREET PACKAGING AND SECURE DELIVERY\n- FREE SHIPPING ON ALL ORDERS OVER $50\n\nORDER NOW TO BEAT THE PRICE HIKE: http://scam-pharmacy.net",
    "aiReply": "Action Logged: Sender auto-blocked. Email quarantined."
  },
  "7": {
    "from": "Zomato",
    "email": "offers@zomato-mail.com",
    "date": "Today (11:40 AM)",
    "subject": "Your last order: 20% off next meal",
    "meta": "Inbox / Promo",
    "isAiFlagged": False,
    "aiStatus": "PROMOTIONAL",
    "body": "Hey Rahul,\n\nHow did you like your meal from Punjab Grill? We hope it was absolutely delicious!\n\nAs a thank you for ordering with us, here's an exclusive 20% discount coupon for your next meal (up to \u20b9100). Use code CRITIC20 at checkout.\n\nValid for the next 3 days on orders above \u20b9199.\n\nEnjoy your meal!",
    "aiReply": "Action: Archive. Coupon Code logged: CRITIC20 (expires in 3 days)."
  },
  "8": {
    "from": "LinkedIn",
    "email": "connections@linkedin.com",
    "date": "Today (9:00 AM)",
    "subject": "5 new connection requests",
    "meta": "Inbox / Social",
    "isAiFlagged": False,
    "aiStatus": "SOCIAL ALERTS",
    "body": "Hi Rahul,\n\nYou have 5 new pending connection requests waiting for your response on LinkedIn:\n\n- Ankit Verma (Software Engineer at TechCorp)\n- Priya Patel (UI/UX Designer)\n- ... and 3 other professionals in your network.\n\nGrow your network and see what they are posting today.\n\nSincerely,\nThe LinkedIn Team",
    "aiReply": "Action: Queue for manual review. Open LinkedIn to approve connection requests."
  },
  "9": {
    "from": "Amazon",
    "email": "shipment-tracking@amazon.in",
    "date": "Yesterday",
    "subject": "Your order has shipped",
    "meta": "Inbox / Shipping",
    "isAiFlagged": False,
    "aiStatus": "TRANSACTIONAL",
    "body": "Dear Rahul,\n\nYour order containing the \"AmazonBasics USB-C to USB-A Cable (3 ft)\" has been shipped and is currently in transit.\n\nYour package is expected to arrive on Friday, August 7 by 8:00 PM.\n\nTracking ID: AZ8821948B\nCarrier: Amazon Logistics\n\nYou can track your package details inside your account at any time.",
    "aiReply": "Action: Auto-tracked. Delivery expected Friday, August 7. Track ID: AZ8821948B."
  },
  "10": {
    "from": "Gym",
    "email": "info@corefitnessgym.com",
    "date": "July 31, 2026",
    "subject": "New yoga classes starting Monday",
    "meta": "Inbox / Update",
    "isAiFlagged": False,
    "aiStatus": "NEWSLETTER",
    "body": "Hi Fitness Enthusiasts,\n\nWe are active to announce new morning Yoga and Mindfulness classes starting this Monday at Core Fitness gym!\n\nClass schedule:\n- Monday & Wednesday: 6:30 AM - 7:30 AM\n- Friday: 7:00 AM - 8:00 AM\n\nSign up by this weekend to claim a 15% early-bird discount on monthly packages. Spaces are limited!\n\nGet active,\nCore Fitness Gym",
    "aiReply": "Hi Core Fitness Gym,\n\nThanks for the update. Could you please send me details about the monthly pricing for the yoga batch? Thanks,\nRahul"
  }
}

DEFAULT_MOCK_DIGEST = [
  {
    "source": "Morning Brew",
    "time": "[~40 sec read]",
    "points": [
      "Markets dip as Fed holds interest rates steady",
      "Apple Vision Pro sales exceed expectations in early quarters",
      "Quick take: SEC releases new crypto regulation framework updates"
    ]
  },
  {
    "source": "TLDR Newsletter",
    "time": "[~35 sec read]",
    "points": [
      "OpenAI releases new reasoning model focusing on math and science",
      "Meta's open-source Llama model beats leading commercial benchmarks",
      "Startup funding roundup: AI infrastructure remains dominant"
    ]
  },
  {
    "source": "Frontend Focus",
    "time": "[~30 sec read]",
    "points": [
      "React Server Components now stable in major meta-frameworks",
      "A comprehensive guide to CSS Container Queries and queryable state",
      "New JavaScript runtime Bun v1.2 introduces performance boosts"
    ]
  }
]
