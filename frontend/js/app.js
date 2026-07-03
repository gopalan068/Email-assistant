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
const API_BASE = "http://localhost:5000/api";

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

  colImportant.innerHTML = '';
  colRegular.innerHTML = '';
  colSpam.innerHTML = '';
  colSecurity.innerHTML = '';
  colOtp.innerHTML = '';
  colCareer.innerHTML = '';
  colOrders.innerHTML = '';

  let spamCount = 0;

  Object.keys(emailDatabase).forEach(id => {
    const email = emailDatabase[id];

    let columnContainer;
    let rowClass = 'ledger-row';

    const status = (email.aiStatus || "").toUpperCase();

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
        <span class="row-from"><span class="row-initial">${initial}</span> ${email.from}</span>
        <time class="row-time">${formatDate(email.date)}</time>
      </div>
      <h3 class="row-subject">${email.subject}</h3>
      <p class="row-snippet">${email.body ? email.body.substring(0, 100).trim() + '...' : ''}</p>
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

  updateColumnCounts();
}

// Render Newsletter Digest
function renderDigest(digestList) {
  const digestGrid = document.querySelector('.digest-ledger-grid');
  digestGrid.innerHTML = '';

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
  const rows = document.querySelectorAll('.ledger-row');
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
  }
}

// Close Detail Drawer
closeDrawerBtn.addEventListener('click', closeDrawer);
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeDrawer();
});

function closeDrawer() {
  drawer.classList.remove('open');
  const rows = document.querySelectorAll('.ledger-row');
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
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: activeEmailId })
  })
    .then(res => {
      if (!res.ok) throw new Error("Backend response error");
      return res.json();
    })
    .then(data => {
      if (data.status === "success") {
        const replyText = data.draft;
        // Cache in local memory database
        emailDatabase[activeEmailId].aiReply = replyText;

        draftContent.innerText = '';
        let index = 0;
        if (typingTimer) clearInterval(typingTimer);

        typingTimer = setInterval(() => {
          if (index < replyText.length) {
            draftContent.innerText += replyText.charAt(index);
            index++;
          } else {
            clearInterval(typingTimer);
            showToast("AI response drafted successfully.");
          }
        }, 10);
      } else {
        throw new Error(data.message || "Failed to draft reply");
      }
    })
    .catch(err => {
      console.error("Draft generation failed, falling back to simulated typing: ", err);
      // Fallback to local default mockup draft text if API unavailable
      const emailData = emailDatabase[activeEmailId];
      const replyText = emailData && emailData.aiReply ? emailData.aiReply : "Hi, thank you for writing. I will look into this and get back to you soon.\n\nBest regards,\nGopal";

      draftContent.innerText = '';
      let index = 0;
      if (typingTimer) clearInterval(typingTimer);

      typingTimer = setInterval(() => {
        if (index < replyText.length) {
          draftContent.innerText += replyText.charAt(index);
          index++;
        } else {
          clearInterval(typingTimer);
          showToast("AI response drafted successfully.");
        }
      }, 10);
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

  fetch(`${API_BASE}/sync`, { method: "POST" })
    .then(res => {
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
btnRegenerateDigest.addEventListener('click', () => {
  btnRegenerateDigest.innerText = "Summarizing...";
  btnRegenerateDigest.disabled = true;

  fetch(`${API_BASE}/digest`)
    .then(res => res.json())
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

// Close drawer when clicking outside
document.addEventListener('click', (e) => {
  if (drawer.classList.contains('open') &&
    !drawer.contains(e.target) &&
    !e.target.closest('.ledger-row')) {
    closeDrawer();
  }
});

// Load data from Backend or fallback
function loadDashboardData() {
  fetch(`${API_BASE}/inbox`)
    .then(res => {
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

  fetch(`${API_BASE}/digest`)
    .then(res => {
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

// Initialize Dashboard
window.addEventListener('DOMContentLoaded', loadDashboardData);
