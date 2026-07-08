// Email database with rich body texts and custom AI replies (maintained as offline mockup fallback)
const mockEmailDatabase = {
  1: {
    from: "Bank of India",
    email: "notifications@bankofindia.co.in",
    date: "August 2, 2026",
    subject: "Loan repayment reminder",
    meta: "Inbox / Finance",
    isAiFlagged: true,
    aiStatus: "FLAGGED / FINANCE",
    body: `Dear Customer,

    This is a friendly reminder that your monthly Home Loan EMI payment of ₹24,500 (Account ending in *8824) is scheduled for auto-debit on August 5, 2026.

    Please ensure your account maintains a sufficient balance prior to the debit date to avoid any late payment fees, bounce penalties, or credit score adjustments.

    If you have already made the transfer, please disregard this automated notification.

    Warm regards,
    Retail Lending Operations
    Bank of India`,
    aiReply: "Log confirmation: Checked balance (current: ₹42,100). Auto-repayment scheduled. Remind me again on Aug 4."
  },
  2: {
    from: "Meera (Manager)",
    email: "meera.sharma@corp.com",
    date: "August 2, 2026 (10:15 AM)",
    subject: "Urgent: Q3 review slides",
    meta: "Inbox / Work",
    isAiFlagged: false,
    aiStatus: "DIRECT CORRESPONDENCE",
    body: `Hi Gopal,

    Hope you are having a productive week.

    The leadership team has moved the Q3 Business Review meeting up to Thursday morning. Because of this schedule shift, I need to compile all team slides by this evening.

    Could you please share your draft Q3 slides by EOD today? Let me know if you need any assistance compiling the customer satisfaction charts.

    Thanks,
    Meera`,
    aiReply: "Hi Meera,\n\nI am finalizing the Q3 slide deck and customer satisfaction charts now. I will have it uploaded and shared with you by 5:00 PM today. Let me know if you want to do a quick sync before the review.\n\nBest,\nGopal"
  },
  3: {
    from: "Freelance Client",
    email: "billing@indiedesigns.studio",
    date: "August 1, 2026",
    subject: "Invoice #INV-204 payment sent",
    meta: "Inbox / Payment",
    isAiFlagged: false,
    aiStatus: "PAYMENT INBOUND",
    body: `Hi Gopal,

    Just a quick update that I've processed the payment for Invoice #INV-204 ($1,200) for the landing page project today.

    It has been sent via bank wire, so it should reflect in your account within the next 2-3 business days depending on interbank processing speeds.

    Let me know once you see it on your end. It was absolute pleasure working with you on this launch!

    Best regards,
    Sarah K.`,
    aiReply: "Hi Sarah,\n\nThank you for processing the payment for invoice #INV-204. I will monitor my account and confirm as soon as the funds clear. It was a pleasure working with you on the landing page project as well!\n\nBest regards,\nGopal"
  },
  4: {
    from: "Dentist Clinic",
    email: "reception@pearlywhites.com",
    date: "August 1, 2026",
    subject: "Appointment tomorrow at 11 AM",
    meta: "Inbox / Health",
    isAiFlagged: false,
    aiStatus: "SCHEDULED EVENT",
    body: `Dear Gopal,

    This is a friendly reminder of your upcoming dental appointment tomorrow, August 3, at 11:00 AM at Pearly Whites Dental Clinic.

    Your session is scheduled for a routine cleaning and general checkup with Dr. Roy. Please try to arrive about 10 minutes early to check-in at reception.

    If you need to reschedule or cancel, please call us at least 12 hours in advance.

    Sincerely,
    Pearly Whites Dental Team`,
    aiReply: "Hi Pearly Whites Team,\n\nThank you for the reminder. I confirm that I will be arriving tomorrow at 11:00 AM for my checkup with Dr. Roy.\n\nBest,\nGopal"
  },
  5: {
    from: "winbig@lottery.xyz",
    email: "claims-department@winbiglottery.xyz",
    date: "July 30, 2026",
    subject: "🎉 You won $5,000,000!",
    meta: "Spam / Phishing",
    isAiFlagged: true,
    aiStatus: "AUTO-BLOCKED / PHISHING",
    body: `DEAR LUCKY WINNER,

    YOUR EMAIL ADDRESS HAS WON THE GRAND PRIZE OF FIVE MILLION DOLLARS ($5,000,000.00) IN THE GLOBAL EMAIL LOTTERY SWEEPSTAKES RUN BY THE TRUSTEES.

    TO CLAIM YOUR PRIZE IMMEDIATELY, PLEASE CLICK ON THE SECURE LINK BELOW AND FILL OUT YOUR BANK ROUTING DETAILS AND SCAN OF PASSPORT:

    http://suspicious-link-to-steal-your-identity.xyz/claim-prize

    DO NOT SHARE THIS EMAIL WITH ANYONE TO PREVENT DOUBLE CLAIMS.

    Yours faithfully,
    Lottery Claims Committee`,
    aiReply: "Action Logged: No response recommended. This is a phishing scam. Auto-reported to security and blacklisted."
  },
  6: {
    from: "cheapmeds@discount.net",
    email: "deals@cheapmeds-discount.net",
    date: "July 29, 2026",
    subject: "70% OFF all medicines 💊",
    meta: "Spam / Commercial",
    isAiFlagged: true,
    aiStatus: "AUTO-BLOCKED / SCAM",
    body: `HELLO FRIEND!

    SAVE BIG TODAY ON ALL YOUR ESSENTIAL MEDICINES. WE OFFER 70% DISCOUNT ON ALL POPULAR PHARMACEUTICAL BRANDS!

    - NO PRESCRIPTIONS REQUIRED
    - 100% DISCREET PACKAGING AND SECURE DELIVERY
    - FREE SHIPPING ON ALL ORDERS OVER $50

    ORDER NOW TO BEAT THE PRICE HIKE: http://scam-pharmacy.net`,
    aiReply: "Action Logged: Sender auto-blocked. Email quarantined."
  },
  7: {
    from: "Zomato",
    email: "offers@zomato-mail.com",
    date: "Today (11:40 AM)",
    subject: "Your last order: 20% off next meal",
    meta: "Inbox / Promo",
    isAiFlagged: false,
    aiStatus: "PROMOTIONAL",
    body: `Hey Gopal,

    How did you like your meal from Punjab Grill? We hope it was absolutely delicious!

    As a thank you for ordering with us, here's an exclusive 20% discount coupon for your next meal (up to ₹100). Use code CRITIC20 at checkout.

    Valid for the next 3 days on orders above ₹199.

    Enjoy your meal!`,
    aiReply: "Action: Archive. Coupon Code logged: CRITIC20 (expires in 3 days)."
  },
  8: {
    from: "LinkedIn",
    email: "connections@linkedin.com",
    date: "Today (9:00 AM)",
    subject: "5 new connection requests",
    meta: "Inbox / Social",
    isAiFlagged: false,
    aiStatus: "SOCIAL ALERTS",
    body: `Hi Gopal,

    You have 5 new pending connection requests waiting for your response on LinkedIn:

    - Ankit Verma (Software Engineer at TechCorp)
    - Priya Patel (UI/UX Designer)
    - ... and 3 other professionals in your network.

    Grow your network and see what they are posting today.

    Sincerely,
    The LinkedIn Team`,
    aiReply: "Action: Queue for manual review. Open LinkedIn to approve connection requests."
  },
  9: {
    from: "Amazon",
    email: "shipment-tracking@amazon.in",
    date: "Yesterday",
    subject: "Your order has shipped",
    meta: "Inbox / Shipping",
    isAiFlagged: false,
    aiStatus: "TRANSACTIONAL",
    body: `Dear Gopal,

    Your order containing the "AmazonBasics USB-C to USB-A Cable (3 ft)" has been shipped and is currently in transit.

    Your package is expected to arrive on Friday, August 7 by 8:00 PM.

    Tracking ID: AZ8821948B
    Carrier: Amazon Logistics

    You can track your package details inside your account at any time.`,
    aiReply: "Action: Auto-tracked. Delivery expected Friday, August 7. Track ID: AZ8821948B."
  },
  10: {
    from: "Gym",
    email: "info@corefitnessgym.com",
    date: "July 31, 2026",
    subject: "New yoga classes starting Monday",
    meta: "Inbox / Update",
    isAiFlagged: false,
    aiStatus: "NEWSLETTER",
    body: `Hi Fitness Enthusiasts,

    We are excited to announce new morning Yoga and Mindfulness classes starting this Monday at Core Fitness gym!

    Class schedule:
    - Monday & Wednesday: 6:30 AM - 7:30 AM
    - Friday: 7:00 AM - 8:00 AM

    Sign up by this weekend to claim a 15% early-bird discount on monthly packages. Spaces are limited!

    Get active,
    Core Fitness Gym`,
    aiReply: "Hi Core Fitness Gym,\n\nThanks for the update. Could you please send me details about the monthly pricing for the yoga batch? Thanks,\nGopal"
  },
  11: {
    from: "TLDR Newsletter",
    email: "tldr@tldrnewsletter.com",
    date: "July 31, 2026",
    subject: "The Future of WebGPU and Browser-based AI",
    meta: "Inbox / Older Updates",
    isAiFlagged: false,
    aiStatus: "OLDER_NEWSLETTER",
    body: "Browser-based AI models are getting 10x faster thanks to WebGPU bindings in modern browsers. Chrome and Safari have rolled out full acceleration support. WebGPU allows WebGL developers to harness compute shaders for heavy model weights...",
    aiReply: ""
  },
  12: {
    from: "Morning Brew",
    email: "brew@morningbrew.com",
    date: "July 30, 2026",
    subject: "A Big Shift in Global Supply Chains",
    meta: "Inbox / Older Updates",
    isAiFlagged: false,
    aiStatus: "OLDER_NEWSLETTER",
    body: "Manufacturing operations are shifting rapidly away from highly centralized pipelines to regional local assembly plants. This reduces carbon prints, improves shipping delays, and protects against geopolitical tariffs...",
    aiReply: ""
  }
};

const mockDigest = [
  {
    source: "Morning Brew",
    time: "[~40 sec read]",
    points: [
      "Markets dip as Fed holds interest rates steady",
      "Apple Vision Pro sales exceed expectations in early quarters",
      "Quick take: SEC releases new crypto regulation framework updates"
    ]
  },
  {
    source: "TLDR Newsletter",
    time: "[~35 sec read]",
    points: [
      "OpenAI releases new reasoning model focusing on math and science",
      "Meta's open-source Llama model beats leading commercial benchmarks",
      "Startup funding roundup: AI infrastructure remains dominant"
    ]
  },
  {
    source: "Frontend Focus",
    time: "[~30 sec read]",
    points: [
      "React Server Components now stable in major meta-frameworks",
      "A comprehensive guide to CSS Container Queries and queryable state",
      "New JavaScript runtime Bun v1.2 introduces performance boosts"
    ]
  }
];

let emailDatabase = {};
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000/api";
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || "434379829289-593k64codcrpeeuqtenkl1gmp6sqjo0l.apps.googleusercontent.com";
let tokenClient;

function getAuthHeaders() {
  const token = sessionStorage.getItem("gmail_access_token") || "mock_token_preview";
  return {
    "Authorization": `Bearer ${token}`,
    "Content-Type": "application/json"
  };
}

function handleSessionExpired() {
  sessionStorage.removeItem("gmail_access_token");
  document.getElementById('session-expired-banner').style.display = 'flex';
  document.body.classList.add('banner-active');
  checkAuthStatus();
}

function fetchUserProfile(token) {
  if (token && token.startsWith("mock_token_")) {
    document.getElementById('profile-name').textContent = "Preview User";
    document.getElementById('profile-email').textContent = "preview@example.com";
    return Promise.resolve();
  }
  return fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
    headers: { "Authorization": `Bearer ${token}` }
  })
    .then(res => {
      if (!res.ok) throw new Error("Profile fetch failed");
      return res.json();
    })
    .then(profile => {
      document.getElementById('profile-name').textContent = profile.name || profile.given_name || "Gopal";
      document.getElementById('profile-email').textContent = profile.email || profile.email;
    })
    .catch(err => {
      console.warn("Could not load Google user profile info dynamically: ", err);
    });
}

// DOM Selectors
const drawer = document.getElementById('email-detail-drawer');
const closeDrawerBtn = document.getElementById('btn-close-drawer');
const searchInput = document.getElementById('search-input');
const statusHeaderText = document.getElementById('status-header-text');
const btnSyncEmails = document.getElementById('btn-sync-emails');
const syncTimeText = document.getElementById('sync-time-text');
const syncIcon = document.getElementById('sync-icon');
const ledgerGridContainer = document.getElementById('ledger-grid-container');
const btnRegenerateDigest = document.getElementById('btn-regenerate-digest');

// Drawer Elements
const dMeta = document.getElementById('drawer-email-meta');
const dSubject = document.getElementById('drawer-email-subject');
const dFrom = document.getElementById('drawer-email-from');
const dAddress = document.getElementById('drawer-email-address');
const dDate = document.getElementById('drawer-email-date');
const dBody = document.getElementById('drawer-email-body');
const dPulseIndicator = document.getElementById('drawer-pulse-indicator');
const dStampLabel = document.getElementById('drawer-ai-stamp-label');
const btnDraftReply = document.getElementById('btn-draft-reply');
const draftContainer = document.getElementById('ai-draft-container');
const draftContent = document.getElementById('ai-draft-content');
const btnCopyDraft = document.getElementById('btn-copy-draft');

let activeEmailId = null;
let typingTimer = null;

// Toast Generator
function showToast(message) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.innerHTML = `<i class="fas fa-check"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Parse Date for row-time label
function formatDate(dateStr) {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) {
      return dateStr.split(',')[1] ? dateStr.split(',')[1].trim().split(' ').slice(0, 2).join(' ') : dateStr;
    }
    const now = new Date();
    if (d.toDateString() === now.toDateString()) {
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  } catch (e) {
    return dateStr;
  }
}

// Helper to parse dates for sorting
function parseEmailDate(dateStr) {
  if (!dateStr) return 0;
  // Clean parentheses like "(10:15 AM)" for mock data parsing
  const cleaned = dateStr.replace(/\s*\(.*\)\s*/g, '');
  const parsed = Date.parse(cleaned);
  return isNaN(parsed) ? 0 : parsed;
}

// Helper to escape HTML characters to prevent rendering/layout issues
function escapeHTML(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Render Inbox Ledger
function renderInbox(data) {
  emailDatabase = data;

  const colImportant = document.querySelector('#col-important .ledger-rows');
  const colRegular = document.querySelector('#col-regular .ledger-rows');
  const colSpam = document.querySelector('#col-spam .ledger-rows');
  const colSecurity = document.getElementById('rows-security');
  const colOtp = document.getElementById('rows-otp');
  const colCareer = document.getElementById('rows-career');
  const colOrders = document.getElementById('rows-orders');
  const colOlderNewsletters = document.getElementById('rows-older-newsletters');

  colImportant.innerHTML = '';
  colRegular.innerHTML = '';
  colSpam.innerHTML = '';
  colSecurity.innerHTML = '';
  colOtp.innerHTML = '';
  colCareer.innerHTML = '';
  colOrders.innerHTML = '';
  if (colOlderNewsletters) colOlderNewsletters.innerHTML = '';

  let spamCount = 0;
  let olderCount = 0;

  // Convert email database to an array and sort descending (newest first)
  const sortedEmails = Object.keys(emailDatabase).map(id => {
    return { id: id, ...emailDatabase[id] };
  }).sort((a, b) => {
    return parseEmailDate(b.date) - parseEmailDate(a.date);
  });

  sortedEmails.forEach(email => {
    const id = email.id;

    let columnContainer;
    let rowClass = 'ledger-row';

    const status = (email.aiStatus || "").toUpperCase();

    if (status === 'NEWSLETTER') {
      // Skipped in standard columns as they are already displayed in the digest/newsletter section
      return;
    }

    if (status === 'OLDER_NEWSLETTER') {
      if (colOlderNewsletters) {
        renderOlderNewsletterRow(id, email, colOlderNewsletters);
        olderCount++;
      }
      return;
    }

    if (status.includes('SPAM') || status.includes('BLOCKED')) {
      columnContainer = colSpam;
      rowClass += ' spam-row';
      spamCount++;
    } else if (status === 'SECURITY ALERT' || status === 'SECURITY') {
      columnContainer = colSecurity;
      rowClass += ' security-row';
    } else if (status === 'OTP') {
      columnContainer = colOtp;
      rowClass += ' otp-row';
    } else if (status === 'JOB ALERT' || status === 'CAREER UPDATE' || status.includes('CAREER') || status.includes('JOB')) {
      columnContainer = colCareer;
      rowClass += ' career-row';
    } else if (status === 'ORDER UPDATE' || status.includes('ORDER')) {
      columnContainer = colOrders;
      rowClass += ' orders-row';
    } else if (email.isAiFlagged ||
      ['IMPORTANT', 'DIRECT CORRESPONDENCE', 'PAYMENT INBOUND', 'SCHEDULED EVENT'].includes(status)) {
      columnContainer = colImportant;
      rowClass += ' important-row';
    } else {
      columnContainer = colRegular;
    }

    let stampHtml = '';
    if (status === 'IMPORTANT') {
      stampHtml = `
        <div class="postmark-stamp">
          <span class="stamp-top">AI</span>
          <span class="stamp-bottom">TRIAGED</span>
        </div>
      `;
    } else if (status.includes('SPAM') || status.includes('BLOCKED')) {
      stampHtml = `
        <div class="postmark-stamp">
          <span class="stamp-top">AI</span>
          <span class="stamp-bottom">BLOCKED</span>
        </div>
      `;
    }

    const initial = email.from ? email.from.charAt(0).toUpperCase() : '?';
    const tag = email.meta ? email.meta.split('/').pop().trim().toLowerCase() : 'inbox';

    const article = document.createElement('article');
    article.className = rowClass;
    article.setAttribute('data-id', id);
    article.innerHTML = `
      <div class="row-meta">
        <span class="row-from"><span class="row-initial">${initial}</span> ${escapeHTML(email.from)}</span>
        <time class="row-time">${formatDate(email.date)}</time>
      </div>
      <h3 class="row-subject">${escapeHTML(email.subject)}</h3>
      <p class="row-snippet">${email.body ? escapeHTML(email.body.substring(0, 100).trim()) + '...' : ''}</p>
      <div class="row-footer">
        <span class="row-tag">${tag}</span>
        ${stampHtml}
      </div>
    `;

    article.addEventListener('click', () => {
      openEmailDetails(id);
    });

    columnContainer.appendChild(article);
  });

  if (spamCount > 0) {
    const summary = document.createElement('div');
    summary.className = 'action-summary-row';
    summary.innerHTML = `
      <i class="fas fa-check-circle"></i>
      <span>${spamCount} log${spamCount > 1 ? 's' : ''} filtered safely. Inbox remains clean.</span>
    `;
    colSpam.appendChild(summary);
  }

  if (olderCount === 0 && colOlderNewsletters) {
    colOlderNewsletters.innerHTML = '<p class="empty-column-hint" style="text-align: center; padding: 24px; font-style: italic; opacity: 0.6;">No older newsletters found.</p>';
  }

  updateColumnCounts();
}

// Render Newsletter Digest
function renderDigest(digestList) {
  const digestGrid = document.querySelector('.digest-ledger-grid');
  digestGrid.innerHTML = '';

  const countEl = document.getElementById('sidebar-digest-count');
  if (countEl) {
    countEl.innerText = `[${digestList ? digestList.length : 0}]`;
  }

  // Update Morning Digest date header dynamically
  const dateEl = document.querySelector('.digest-date');
  if (dateEl) {
    const today = new Date();
    const options = { weekday: 'long', month: 'long', day: 'numeric' };
    dateEl.innerText = `— ${today.toLocaleDateString('en-US', options)}`;
  }

  // Update source briefs count dynamically
  const statSources = document.getElementById('digest-stat-sources');
  if (statSources) {
    const count = digestList ? digestList.length : 0;
    statSources.innerText = `${count} Source Brief${count !== 1 ? 's' : ''}`;
  }

  if (!digestList || digestList.length === 0) {
    digestGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; color: rgba(32, 38, 31, 0.5); font-style: italic; padding: 24px 0;">
        No newsletter briefs generated. Sync inbox to fetch recent newsletters.
      </div>
    `;
    return;
  }

  digestList.forEach(entry => {
    const div = document.createElement('div');
    div.className = 'digest-entry';

    let pointsHtml = '';
    entry.points.forEach(point => {
      pointsHtml += `<li>${point}</li>`;
    });

    div.innerHTML = `
      <h3 class="entry-source">${entry.source} <span class="entry-time">${entry.time}</span></h3>
      <ul class="entry-points">
        ${pointsHtml}
      </ul>
    `;
    digestGrid.appendChild(div);
  });
}

// Open Detail Drawer
function openEmailDetails(emailId) {
  console.log("openEmailDetails called with emailId:", emailId);
  const rows = document.querySelectorAll('.ledger-row, .gmail-row');
  rows.forEach(r => {
    if (r.getAttribute('data-id') == emailId) {
      r.classList.add('active');
    } else {
      r.classList.remove('active');
    }
  });

  activeEmailId = emailId;
  const emailData = emailDatabase[emailId];

  if (emailData) {
    dMeta.innerText = emailData.meta;
    dSubject.innerText = emailData.subject;
    dFrom.innerText = emailData.from;
    dAddress.innerText = emailData.email;
    dDate.innerText = emailData.date;
    dBody.innerText = emailData.body;

    const status = (emailData.aiStatus || "").toUpperCase();

    if (emailData.isAiFlagged || status === 'IMPORTANT') {
      dPulseIndicator.className = "pulse-dot ochre-pulse";
      dStampLabel.innerText = status || "IMPORTANT";
      dStampLabel.style.color = "var(--color-ochre)";
    } else {
      dPulseIndicator.className = "pulse-dot";
      dStampLabel.innerText = status || "REGULAR";
      dStampLabel.style.color = "var(--color-pine)";
    }

    // Check if reply already cached
    if (emailData.aiReply && emailData.aiReply.trim()) {
      btnDraftReply.style.display = 'none';
      draftContainer.style.display = 'block';
      draftContent.innerText = emailData.aiReply;
    } else {
      draftContainer.style.display = 'none';
      draftContent.innerText = '';
      btnDraftReply.style.display = 'block';
    }

    if (typingTimer) clearInterval(typingTimer);
    drawer.classList.add('open');
    document.body.classList.add('drawer-open');
  }
}

// Close Detail Drawer
closeDrawerBtn.addEventListener('click', closeDrawer);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeDrawer();
});

function closeDrawer() {
  drawer.classList.remove('open');
  document.body.classList.remove('drawer-open');
  const rows = document.querySelectorAll('.ledger-row, .gmail-row');
  rows.forEach(r => r.classList.remove('active'));
  activeEmailId = null;
  if (typingTimer) clearInterval(typingTimer);
}

// Fetch and dynamically type real AI draft reply (Phase 8)
btnDraftReply.addEventListener('click', () => {
  if (!activeEmailId) return;

  btnDraftReply.style.display = 'none';
  draftContainer.style.display = 'block';
  draftContent.innerHTML = '<span style="font-style:italic; opacity:0.5;"><i class="fas fa-spinner fa-spin"></i> Writing draft...</span>';

  fetch(`${API_BASE}/draft-reply`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ id: activeEmailId })
  })
    .then(res => {
      if (res.status === 401) {
        handleSessionExpired();
        throw new Error("Session expired");
      }
      if (!res.ok) throw new Error("Backend response error");
      return res.json();
    })
    .then(data => {
      if (data.status === "success") {
        const replyText = data.draft;
        // Cache in local memory database
        emailDatabase[activeEmailId].aiReply = replyText;

        draftContent.textContent = '';
        let index = 0;
        let typedText = '';
        if (typingTimer) clearInterval(typingTimer);

        typingTimer = setInterval(() => {
          if (index < replyText.length) {
            typedText += replyText.charAt(index);
            draftContent.textContent = typedText;
            index++;
          } else {
            clearInterval(typingTimer);
            showToast("AI response drafted successfully.");
          }
        }, 15);
      } else {
        throw new Error(data.message || "Failed to draft reply");
      }
    })
    .catch(err => {
      console.error("Draft generation failed, falling back to simulated typing: ", err);
      const emailData = emailDatabase[activeEmailId];
      const replyText = emailData && emailData.aiReply ? emailData.aiReply : "Hi, thank you for writing. I will look into this and get back to you soon.\n\nBest regards,\nGopal";

      draftContent.textContent = '';
      let index = 0;
      let typedText = '';
      if (typingTimer) clearInterval(typingTimer);

      typingTimer = setInterval(() => {
        if (index < replyText.length) {
          typedText += replyText.charAt(index);
          draftContent.textContent = typedText;
          index++;
        } else {
          clearInterval(typingTimer);
          showToast("AI response drafted successfully.");
        }
      }, 15);
    });
});

// Copy Draft to Clipboard
btnCopyDraft.addEventListener('click', () => {
  const text = draftContent.innerText;
  if (text) {
    navigator.clipboard.writeText(text).then(() => {
      showToast("Draft copied to clipboard.");
    }).catch(err => {
      console.error("Clipboard copy failed: ", err);
    });
  }
});

// Trigger API sync pipeline
btnSyncEmails.addEventListener('click', () => {
  syncIcon.className = "fas fa-sync-alt fa-spin";
  syncTimeText.innerText = "Syncing logs...";
  ledgerGridContainer.classList.add('shimmer-active');

  fetch(`${API_BASE}/sync`, {
    method: "POST",
    headers: getAuthHeaders()
  })
    .then(res => {
      if (res.status === 401) {
        handleSessionExpired();
        throw new Error("Session expired");
      }
      if (res.status === 429) {
        showToast("Sync rate limit reached. Please wait a moment.");
        throw new Error("Sync rate limit reached");
      }
      if (!res.ok) return res.json().then(d => { throw new Error(d.message || "Sync failed") });
      return res.json();
    })
    .then(data => {
      syncIcon.className = "fas fa-sync-alt";
      ledgerGridContainer.classList.remove('shimmer-active');
      syncTimeText.innerText = "Synced just now";
      showToast("Inbox ledger successfully updated.");
      // Reload dashboard
      loadDashboardData();
    })
    .catch(err => {
      console.error("Sync failed: ", err);
      syncIcon.className = "fas fa-sync-alt";
      ledgerGridContainer.classList.remove('shimmer-active');
      syncTimeText.innerText = "Sync failed";
      showToast(err.message || "Connection error. Make sure backend is running.");
    });
});

// Regenerate Digest
if (btnRegenerateDigest) {
  btnRegenerateDigest.addEventListener('click', () => {
    btnRegenerateDigest.innerText = "Summarizing...";
    btnRegenerateDigest.disabled = true;

    fetch(`${API_BASE}/digest`, { headers: getAuthHeaders() })
      .then(res => {
        if (res.status === 401) {
          handleSessionExpired();
          throw new Error("Session expired");
        }
        if (!res.ok) throw new Error("HTTP error");
        return res.json();
      })
      .then(data => {
        btnRegenerateDigest.innerText = "Regenerate Briefing";
        btnRegenerateDigest.disabled = false;
        renderDigest(data);
        showToast("Morning briefing re-compiled.");
      })
      .catch(err => {
        console.error("Digest generation failed: ", err);
        btnRegenerateDigest.innerText = "Regenerate Briefing";
        btnRegenerateDigest.disabled = false;
        showToast("Error connecting to server.");
      });
  });
}

// Live Search Filter — covers all 7 columns
searchInput.addEventListener('input', (e) => {
  const query = e.target.value.toLowerCase().trim();
  const rows = document.querySelectorAll('.ledger-row');

  rows.forEach(row => {
    const fromText = row.querySelector('.row-from') ? row.querySelector('.row-from').innerText.toLowerCase() : '';
    const subjectText = row.querySelector('.row-subject') ? row.querySelector('.row-subject').innerText.toLowerCase() : '';
    const snippetText = row.querySelector('.row-snippet') ? row.querySelector('.row-snippet').innerText.toLowerCase() : '';
    const tagText = row.querySelector('.row-tag') ? row.querySelector('.row-tag').innerText.toLowerCase() : '';

    const match = fromText.includes(query) || subjectText.includes(query) ||
      snippetText.includes(query) || tagText.includes(query);
    row.style.display = match ? 'flex' : 'none';
  });

  updateColumnCounts();
});

// Update column count bubbles dynamically based on visible items
function updateColumnCounts() {
  // Main 3 columns use id=col-* selectors (they contain .ledger-row directly)
  const mainCols = ['important', 'regular', 'spam'];
  // Extended 4 columns use id=rows-* selectors
  const extCols = ['security', 'otp', 'career', 'orders'];
  let totalVisible = 0;

  mainCols.forEach(col => {
    const container = document.getElementById(`col-${col}`);
    const visibleRows = Array.from(container.querySelectorAll('.ledger-row'))
      .filter(row => row.style.display !== 'none');
    const count = visibleRows.length;
    totalVisible += count;
    document.getElementById(`count-${col}`).innerText = count < 10 ? `[0${count}]` : `[${count}]`;
  });

  extCols.forEach(col => {
    const container = document.getElementById(`rows-${col}`);
    const visibleRows = Array.from(container.querySelectorAll('.ledger-row'))
      .filter(row => row.style.display !== 'none');
    const count = visibleRows.length;
    totalVisible += count;
    document.getElementById(`count-${col}`).innerText = count < 10 ? `[0${count}]` : `[${count}]`;

    // Update placeholder text
    const placeholderEl = document.getElementById(`placeholder-${col}`);
    if (placeholderEl) {
      const mailText = count === 1 ? 'mail' : 'mails';
      placeholderEl.innerText = `${count} ${mailText} available`;
    }
  });

  const importantContainer = document.getElementById('col-important');
  const importantCount = Array.from(importantContainer.querySelectorAll('.ledger-row'))
    .filter(row => row.style.display !== 'none').length;

  const today = new Date().toLocaleDateString('en-US', { weekday: 'long' });
  if (importantCount === 0) {
    statusHeaderText.innerHTML = `${today}. Ledger is <span class="highlight">tidy</span>.`;
  } else {
    const lettersWord = importantCount === 1 ? 'letter' : 'letters';
    statusHeaderText.innerHTML = `${today}. <span class="highlight">${importantCount} ${lettersWord}</span> need you.`;
  }

  document.getElementById('sidebar-inbox-count').innerText = `[${totalVisible}]`;
}

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    searchInput.focus();
  }
});

// Toggle sidebar on mobile
const btnToggleSidebar = document.getElementById('btn-toggle-sidebar');
const sidebar = document.querySelector('.sidebar');

if (btnToggleSidebar) {
  btnToggleSidebar.addEventListener('click', (e) => {
    e.stopPropagation();
    sidebar.classList.toggle('open');
  });
}

// Close drawer or sidebar when clicking outside
document.addEventListener('click', (e) => {
  if (sidebar && sidebar.classList.contains('open') &&
    !sidebar.contains(e.target) &&
    (btnToggleSidebar && !btnToggleSidebar.contains(e.target))) {
    sidebar.classList.remove('open');
  }

  if (drawer.classList.contains('open') &&
    !drawer.contains(e.target) &&
    !e.target.closest('.ledger-row, .gmail-row')) {
    closeDrawer();
  }
});

// Load data from Backend or fallback
function loadDashboardData() {
  const token = sessionStorage.getItem("gmail_access_token") || "mock_token_preview";
  if (!token) return;

  fetch(`${API_BASE}/inbox`, { headers: getAuthHeaders() })
    .then(res => {
      if (res.status === 401) {
        handleSessionExpired();
        throw new Error("Session expired");
      }
      if (!res.ok) throw new Error("HTTP error");
      return res.json();
    })
    .then(inboxData => {
      renderInbox(inboxData);
    })
    .catch(err => {
      console.warn("Backend server not available, loading fallback mockup: ", err);
      renderInbox(mockEmailDatabase);
    });

  fetch(`${API_BASE}/digest`, { headers: getAuthHeaders() })
    .then(res => {
      if (res.status === 401) {
        handleSessionExpired();
        throw new Error("Session expired");
      }
      if (!res.ok) throw new Error("HTTP error");
      return res.json();
    })
    .then(digestData => {
      renderDigest(digestData);
    })
    .catch(err => {
      console.warn("Backend server not available, loading mockup digest.");
      renderDigest(mockDigest);
    });
}

function checkAuthStatus() {
  const token = sessionStorage.getItem("gmail_access_token") || "mock_token_preview";
  const isPreview = !sessionStorage.getItem("gmail_access_token");
  const profileLoggedOut = document.getElementById("profile-logged-out");
  const profileLoggedIn = document.getElementById("profile-logged-in");
  const btnHeaderLogin = document.getElementById("btn-header-login");
  const btnSyncEmails = document.getElementById("btn-sync-emails");
  const btnRegenerateDigest = document.getElementById("btn-regenerate-digest");

  if (!isPreview) {
    if (profileLoggedOut) profileLoggedOut.style.display = "none";
    if (profileLoggedIn) profileLoggedIn.style.display = "block";
    if (btnHeaderLogin) btnHeaderLogin.style.display = "none";
  } else {
    if (profileLoggedOut) profileLoggedOut.style.display = "block";
    if (profileLoggedIn) profileLoggedIn.style.display = "none";
    if (btnHeaderLogin) btnHeaderLogin.style.display = "block";
  }
  
  if (btnSyncEmails) btnSyncEmails.style.display = "block";
  if (btnRegenerateDigest) btnRegenerateDigest.style.display = "block";
  
  fetchUserProfile(token);
  loadDashboardData();
  loadSettings();
}

function initOAuth() {
  if (typeof google === 'undefined') {
    console.warn("Google client library not loaded yet, retrying in 500ms...");
    setTimeout(initOAuth, 500);
    return;
  }


  tokenClient = google.accounts.oauth2.initTokenClient({
    client_id: GOOGLE_CLIENT_ID,
    scope: 'https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile',
    callback: (response) => {
      if (response.error) {
        console.error("OAuth Error: ", response);
        showToast("Authentication failed. Please try again.");
        return;
      }

      if (response.access_token) {
        sessionStorage.setItem("gmail_access_token", response.access_token);

        // Hide banners and update displays
        document.getElementById('session-expired-banner').style.display = 'none';
        document.body.classList.remove('banner-active');

        checkAuthStatus();
        showToast("Logged in successfully.");
      }
    },
  });
}

function signOutUser() {
  const token = sessionStorage.getItem("gmail_access_token");
  if (token) {
    try {
      google.accounts.oauth2.revoke(token, () => {
        console.log("Token revoked server-side.");
      });
    } catch (e) {
      console.warn("Could not revoke token on Google servers:", e);
    }
  }
  sessionStorage.removeItem("gmail_access_token");
  document.getElementById('session-expired-banner').style.display = 'none';
  document.body.classList.remove('banner-active');
  checkAuthStatus();
  showToast("Logged out successfully.");
}

let subscribedNewsletters = [];

function loadSettings() {
  const token = sessionStorage.getItem("gmail_access_token") || "mock_token_preview";
  if (!token) return;

  fetch(`${API_BASE}/settings`, { headers: getAuthHeaders() })
    .then(res => {
      if (res.status === 401) {
        handleSessionExpired();
        throw new Error("Session expired");
      }
      if (!res.ok) throw new Error("Failed to load settings");
      return res.json();
    })
    .then(data => {
      subscribedNewsletters = data.subscribed_newsletters || [];
      renderSettingsTags();
    })
    .catch(err => {
      console.warn("Could not load user settings: ", err);
    });
}

function renderSettingsTags() {
  const listEl = document.getElementById("settings-newsletter-list");
  if (!listEl) return;

  listEl.innerHTML = "";
  if (subscribedNewsletters.length === 0) {
    listEl.innerHTML = '<span style="font-style: italic; opacity: 0.5; font-size: 12px; margin: auto;">No custom newsletter whitelist configured. Falling back to heuristics.</span>';
    return;
  }

  subscribedNewsletters.forEach((item, index) => {
    const tag = document.createElement("div");
    tag.className = "newsletter-tag";
    tag.innerHTML = `<span>${item}</span><span class="remove-tag" data-index="${index}">&times;</span>`;
    listEl.appendChild(tag);
  });

  // Wire up remove handlers
  listEl.querySelectorAll(".remove-tag").forEach(btn => {
    btn.addEventListener("click", (e) => {
      const idx = parseInt(e.target.getAttribute("data-index"), 10);
      subscribedNewsletters.splice(idx, 1);
      renderSettingsTags();
    });
  });
}

function renderOlderNewsletterRow(id, email, container) {
  const wrapper = document.createElement('div');
  wrapper.className = 'gmail-row-wrapper';

  const snippet = email.body ? escapeHTML(email.body.substring(0, 80).trim()) + '...' : '';
  const dateFormatted = formatDate(email.date);

  const briefText = email.newsletterBriefing || '';
  const displayBriefing = briefText ? 'block' : 'none';

  wrapper.innerHTML = `
    <div class="gmail-row" data-id="${id}">
      <div class="gmail-col-from">${escapeHTML(email.from)}</div>
      <div class="gmail-col-subject-wrapper">
        <span class="gmail-subject">${escapeHTML(email.subject)}</span>
        <span class="gmail-sep"> — </span>
        <span class="gmail-snippet">${snippet}</span>
      </div>
      <div class="gmail-col-date">${dateFormatted}</div>
      <div class="gmail-col-action">
        <button class="btn-row-briefing" data-id="${id}">
          <i class="fas fa-magic"></i> Generate Briefing
        </button>
      </div>
    </div>
    <div class="row-briefing-box" id="briefing-box-${id}" style="display: ${displayBriefing};">
      <div class="briefing-header">AI Briefing Summary</div>
      <div class="briefing-text" id="briefing-text-${id}">${escapeHTML(briefText)}</div>
    </div>
  `;

  const gmailRow = wrapper.querySelector('.gmail-row');
  if (gmailRow) {
    gmailRow.addEventListener('click', (e) => {
      console.log("Older newsletter row clicked. ID:", id);
      if (e.target.closest('.gmail-col-action') || e.target.closest('.btn-row-briefing')) {
        console.log("Click ignored: inside action/briefing button");
        return;
      }
      openEmailDetails(id);
    });
  }

  const btnBrief = wrapper.querySelector('.btn-row-briefing');
  if (btnBrief) {
    btnBrief.addEventListener('click', (e) => {
      e.stopPropagation();
      generateOlderNewsletterBriefing(id);
    });
  }

  container.appendChild(wrapper);
}

function generateOlderNewsletterBriefing(id) {
  const token = sessionStorage.getItem("gmail_access_token");

  const box = document.getElementById(`briefing-box-${id}`);
  const textEl = document.getElementById(`briefing-text-${id}`);
  const btn = document.querySelector(`.btn-row-briefing[data-id="${id}"]`);

  if (box && textEl && btn) {
    box.style.display = 'block';
    textEl.innerHTML = '<span style="font-style:italic; opacity:0.5;"><i class="fas fa-spinner fa-spin"></i> Compiling brief...</span>';
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Working...';

    // If not logged in, simulate typing of fallback mockup briefing
    if (!token) {
      setTimeout(() => {
        const mockSummary = "This newsletter contains industry updates on browser technology developments. It details performance acceleration, driver implementations, and core rendering enhancements.";
        emailDatabase[id].newsletterBriefing = mockSummary;

        textEl.textContent = '';
        let index = 0;
        let typedBrief = '';
        const typingTimer = setInterval(() => {
          if (index < mockSummary.length) {
            typedBrief += mockSummary.charAt(index);
            textEl.textContent = typedBrief;
            index++;
          } else {
            clearInterval(typingTimer);
            showToast("Briefing compiled successfully (Demo Mode).");
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-magic"></i> Generate Briefing';
          }
        }, 15);
      }, 1000);
      return;
    }

    fetch(`${API_BASE}/brief-newsletter`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify({ id: id })
    })
      .then(res => {
        if (res.status === 401) {
          handleSessionExpired();
          throw new Error("Session expired");
        }
        if (!res.ok) throw new Error("Failed to compile summary");
        return res.json();
      })
      .then(data => {
        if (data.status === "success") {
          const summary = data.briefing;
          emailDatabase[id].newsletterBriefing = summary;

          textEl.textContent = '';
          let index = 0;
          let typedBrief = '';
          const typingTimer = setInterval(() => {
            if (index < summary.length) {
              typedBrief += summary.charAt(index);
              textEl.textContent = typedBrief;
              index++;
            } else {
              clearInterval(typingTimer);
              showToast("Briefing compiled successfully.");
            }
          }, 15);
        } else {
          throw new Error(data.message || "Briefing failed");
        }
      })
      .catch(err => {
        console.error("Summary generation failed: ", err);
        textEl.innerText = "Error compiling summary. Try again.";
      })
      .finally(() => {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-magic"></i> Generate Briefing';
      });
  }
}

// Wire OAuth and Settings UI listeners
document.addEventListener('DOMContentLoaded', () => {
  initOAuth();
  checkAuthStatus();

  const handleLoginClick = () => {
    if (tokenClient) {
      tokenClient.requestAccessToken();
    } else {
      showToast("Google OAuth library is still loading. Please wait a moment.");
    }
  };

  const btnSidebarLogin = document.getElementById('btn-sidebar-login');
  if (btnSidebarLogin) {
    btnSidebarLogin.addEventListener('click', handleLoginClick);
  }

  const btnHeaderLogin = document.getElementById('btn-header-login');
  if (btnHeaderLogin) {
    btnHeaderLogin.addEventListener('click', handleLoginClick);
  }

  const btnBannerReauth = document.getElementById('btn-banner-reauth');
  if (btnBannerReauth) {
    btnBannerReauth.addEventListener('click', handleLoginClick);
  }

  const btnLogout = document.getElementById('btn-logout');
  if (btnLogout) {
    btnLogout.addEventListener('click', signOutUser);
  }

  // Settings Modal Triggers
  const navLinks = document.querySelectorAll(".nav-links li");
  navLinks.forEach(link => {
    const text = link.textContent.trim().toLowerCase();
    if (text.includes("settings") || text.includes("ai rules")) {
      link.addEventListener("click", (e) => {
        e.preventDefault();

        const token = sessionStorage.getItem("gmail_access_token") || "mock_token_preview";
        if (!token) {
          showToast("Connect Gmail first to configure custom rules.");
          return;
        }

        document.getElementById("settings-modal").style.display = "flex";
        loadSettings();
      });
    }
  });

  // Inbox & Digests Navigation Scroll Triggers
  const navInbox = document.getElementById("nav-inbox");
  if (navInbox) {
    navInbox.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
      const navLinks = document.querySelectorAll(".nav-links li");
      navLinks.forEach(li => li.classList.remove("active"));
      navInbox.parentElement.classList.add("active");

      const sidebar = document.querySelector('.sidebar');
      if (sidebar && sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
      }
    });
  }

  const navDigests = document.getElementById("nav-digests");
  if (navDigests) {
    navDigests.addEventListener("click", (e) => {
      e.preventDefault();
      const digestSection = document.getElementById("digest-section");
      if (digestSection) {
        digestSection.scrollIntoView({ behavior: "smooth", block: "start" });
        const navLinks = document.querySelectorAll(".nav-links li");
        navLinks.forEach(li => li.classList.remove("active"));
        navDigests.parentElement.classList.add("active");

        const sidebar = document.querySelector('.sidebar');
        if (sidebar && sidebar.classList.contains('open')) {
          sidebar.classList.remove('open');
        }
      }
    });
  }

  const navArchive = document.getElementById("nav-archive");
  if (navArchive) {
    navArchive.addEventListener("click", (e) => {
      e.preventDefault();
      const olderSection = document.getElementById("older-newsletters-section");
      if (olderSection) {
        olderSection.scrollIntoView({ behavior: "smooth", block: "start" });
        const navLinks = document.querySelectorAll(".nav-links li");
        navLinks.forEach(li => li.classList.remove("active"));
        navArchive.parentElement.classList.add("active");

        const sidebar = document.querySelector('.sidebar');
        if (sidebar && sidebar.classList.contains('open')) {
          sidebar.classList.remove('open');
        }
      }
    });
  }

  const btnCloseSettings = document.getElementById("btn-close-settings");
  const btnCancelSettings = document.getElementById("btn-cancel-settings");
  const modalOverlay = document.getElementById("settings-modal");

  if (btnCloseSettings) btnCloseSettings.addEventListener("click", () => modalOverlay.style.display = "none");
  if (btnCancelSettings) btnCancelSettings.addEventListener("click", () => modalOverlay.style.display = "none");
  if (modalOverlay) {
    modalOverlay.addEventListener("click", (e) => {
      if (e.target === modalOverlay) modalOverlay.style.display = "none";
    });
  }

  // Add Newsletter Item to Settings whitelist
  const btnAddNewsletter = document.getElementById("btn-add-newsletter");
  const inputNewNewsletter = document.getElementById("input-new-newsletter");
  if (btnAddNewsletter && inputNewNewsletter) {
    btnAddNewsletter.addEventListener("click", () => {
      const val = inputNewNewsletter.value.trim();
      if (val) {
        if (!subscribedNewsletters.includes(val)) {
          subscribedNewsletters.push(val);
          renderSettingsTags();
        }
        inputNewNewsletter.value = "";
      }
    });

    inputNewNewsletter.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        btnAddNewsletter.click();
      }
    });
  }

  // Save Settings to Backend
  const btnSaveSettings = document.getElementById("btn-save-settings");
  if (btnSaveSettings) {
    btnSaveSettings.addEventListener("click", () => {
      const token = sessionStorage.getItem("gmail_access_token") || "mock_token_preview";
      if (!token) {
        showToast("Connect your Gmail account first to save settings.");
        return;
      }

      btnSaveSettings.innerText = "Saving...";
      btnSaveSettings.disabled = true;

      fetch(`${API_BASE}/settings`, {
        method: "POST",
        headers: getAuthHeaders(),
        body: JSON.stringify({ subscribed_newsletters: subscribedNewsletters })
      })
        .then(res => {
          if (res.status === 401) {
            handleSessionExpired();
            throw new Error("Session expired");
          }
          if (!res.ok) throw new Error("Save settings failed");
          return res.json();
        })
        .then(data => {
          showToast("Newsletter rules saved successfully.");
          modalOverlay.style.display = "none";
        })
        .catch(err => {
          showToast(err.message || "Failed to save settings.");
        })
        .finally(() => {
          btnSaveSettings.innerText = "Save Settings";
          btnSaveSettings.disabled = false;
        });
    });
  }
});
