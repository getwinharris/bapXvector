// --- COPILOT INTERFACE LAYOUT ---
const copilotUI = document.createElement("div");
copilotUI.id = "copilotUI";
copilotUI.style.cssText = `
  position: fixed;
  bottom: 0;
  right: 20px;
  width: 400px;
  height: 70%;
  background: rgba(18,12,30,0.85);
  border: 1px solid ${THEME.accent};
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 0 20px rgba(64,32,128,0.3);
  z-index: 9999;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: white;
  user-select: none;
`;
document.body.appendChild(copilotUI);

// --- PWA INSTALLATION LOGIC ---
let deferredPrompt = null;

function getAdminConfig(key, fallback) {
  // Placeholder for admin config retrieval
  // In real implementation, this would fetch from admin panel or config store
  // Here we return fallback for demo
  return fallback;
}

function showPWAButton() {
  if (document.getElementById("pwaInstallBtn")) return;
  const btn = document.createElement("button");
  btn.id = "pwaInstallBtn";
  const icon = getAdminConfig("pwaInstallIcon", "fa-download");
  const text = getAdminConfig("pwaInstallText", "Download the Drop");
  btn.innerHTML = `<i class="fas ${icon}" style="margin-right:8px;"></i> ${text}`;
  btn.style.cssText = `
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 10000;
    padding: 12px 28px;
    font-size: 16px;
    color: white;
    background: linear-gradient(90deg, ${THEME.accent} 60%, ${THEME.secondary} 100%);
    border: none;
    border-radius: 24px;
    box-shadow: 0 4px 12px rgba(64,32,128,0.3);
    cursor: pointer;
    font-family: inherit;
    font-weight: 600;
    display: flex;
    align-items: center;
    transition: background 0.3s ease;
  `;
  btn.onmouseenter = () => btn.style.background = `linear-gradient(90deg, ${THEME.secondary} 60%, ${THEME.accent} 100%)`;
  btn.onmouseleave = () => btn.style.background = `linear-gradient(90deg, ${THEME.accent} 60%, ${THEME.secondary} 100%)`;
  btn.onclick = () => {
    if (!deferredPrompt) return;
    btn.disabled = true;
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then(({ outcome }) => {
      if (outcome === "accepted") {
        console.log("PWA install accepted");
        activateWaterDrop();
      } else {
        console.log("PWA install dismissed");
      }
      btn.remove();
      deferredPrompt = null;
    });
  };
  document.body.appendChild(btn);
}

window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  deferredPrompt = e;
  showPWAButton();
});

function activateWaterDrop() {
  if (typeof initWaterDrop === "function") {
    initWaterDrop();
  }
}

window.addEventListener("load", () => {
  const isStandalone = window.matchMedia("(display-mode: standalone)").matches ||
    window.navigator.standalone === true;
  if (isStandalone) {
    initWaterDrop();
  }
});

function initWaterDrop() {
  if (document.getElementById("livingDropBtn")) return;
  const btn = document.createElement("div");
  btn.id = "livingDropBtn";
  btn.title = "Open bapX Companion";
  const icon = getAdminConfig("waterDropIcon", "fa-tint");
  const iconColor = THEME.accent;
  btn.style.cssText = `
    position: fixed;
    bottom: 32px;
    right: 32px;
    z-index: 10001;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    background: rgba(30,20,50,0.82);
    box-shadow: 0 8px 24px rgba(64,32,128,0.3);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: box-shadow 0.3s ease;
  `;
  btn.innerHTML = `<i class="fas ${icon}" style="font-size: 36px; color: ${iconColor}; animation: spin 6s linear infinite;"></i>`;
  btn.onclick = () => {
    const ui = document.getElementById("copilotUI");
    if (ui) {
      ui.style.display = (ui.style.display === "none" ? "flex" : "none");
    }
  };
  document.body.appendChild(btn);
}

// Add spin animation for water drop icon
const styleSheet = document.createElement("style");
styleSheet.textContent = `
  @keyframes spin {
    from {transform: rotate(0deg);}
    to {transform: rotate(360deg);}
  }
`;
document.head.appendChild(styleSheet);

// --- SIDEBAR HEADER ---
const header = document.createElement("div");
header.style.cssText = `
  height: 50px;
  background: rgba(18,12,30,0.95);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 15px;
  border-bottom: 1px solid ${THEME.accent};
  font-weight: 600;
  font-size: 16px;
  user-select: none;
`;
header.innerHTML = `
  <span style="color:${THEME.accent};font-weight:bold;">bapX Companion</span>
  <div id="headerButtons" style="display:flex;align-items:center;gap:12px;">
    <button id="profileBtn" style="background:none;border:none;color:${THEME.secondary};font-size:22px;cursor:pointer;display:flex;align-items:center;gap:6px;padding:4px 8px;border-radius:8px;transition:background 0.3s;">
      <i class="fas fa-user-circle"></i><span id="profileBtnText">Profile</span>
    </button>
  </div>
`;
copilotUI.appendChild(header);

// --- PROFILE PANEL ---
const profilePanel = document.createElement("div");
profilePanel.id = "profilePanel";
profilePanel.style.cssText = `
  display: none;
  flex-direction: column;
  padding: 16px 20px;
  background: rgba(24,16,40,0.95);
  border-top: 1px solid ${THEME.accent};
  color: ${THEME.secondary};
  font-size: 14px;
  user-select: text;
  overflow-y: auto;
  max-height: 40%;
  border-radius: 0 0 12px 12px;
`;

const genderIcons = {
  male: "fa-mars",
  female: "fa-venus",
  third: "fa-genderless"
};

const profileHTML = `
  <label style="margin-bottom:8px;display:flex;flex-direction:column;gap:4px;">
    Gender:
    <select id="genderSelect" style="padding:6px 10px; border-radius: 8px; border:none; background:#222; color: white; font-size: 14px;">
      <option value="male">♂ Male</option>
      <option value="female">♀ Female</option>
      <option value="third">⚧ Third Gender</option>
    </select>
    <div id="genderIcon" style="margin-top:6px; font-size: 24px; color: ${THEME.accent};"></div>
  </label>
  <label style="margin-bottom:12px;display:flex;flex-direction:column;gap:4px;">
    Date of Birth:
    <input id="dobInput" type="date" style="padding:6px 10px; border-radius: 8px; border:none; background:#222; color: white; font-size: 14px;">
  </label>
  <label style="margin-bottom:12px;display:flex;flex-direction:column;gap:4px;">
    Short Bio:
    <textarea id="bioInput" rows="3" maxlength="160" placeholder="Write a short bio..." style="resize:none; padding:8px 10px; border-radius: 8px; border:none; background:#222; color: white; font-size: 14px; font-family: inherit;"></textarea>
  </label>
  <button id="saveProfileBtn" style="
    background: ${THEME.accent};
    border: none;
    border-radius: 10px;
    color: white;
    font-weight: 600;
    padding: 10px 0;
    cursor: pointer;
    transition: background 0.3s;
  ">Save Profile</button>
  <div id="profileSaveMsg" style="margin-top:8px; font-size: 13px; color:#aaffaa; display:none;">Profile saved.</div>
`;
profilePanel.innerHTML = profileHTML;
copilotUI.appendChild(profilePanel);

const profileBtn = document.getElementById("profileBtn");
const genderSelect = profilePanel.querySelector("#genderSelect");
const genderIconDiv = profilePanel.querySelector("#genderIcon");
const dobInput = profilePanel.querySelector("#dobInput");
const bioInput = profilePanel.querySelector("#bioInput");
const saveProfileBtn = profilePanel.querySelector("#saveProfileBtn");
const profileSaveMsg = profilePanel.querySelector("#profileSaveMsg");

function updateGenderIcon() {
  const val = genderSelect.value;
  const iconClass = genderIcons[val] || genderIcons.third;
  genderIconDiv.innerHTML = `<i class="fas ${iconClass}"></i>`;
}
genderSelect.addEventListener("change", updateGenderIcon);
updateGenderIcon();

profileBtn.onclick = () => {
  if (profilePanel.style.display === "flex") {
    profilePanel.style.display = "none";
  } else {
    profilePanel.style.display = "flex";
    loadProfileData();
  }
};

function loadProfileData() {
  // Load from capsule table storage (simulate with localStorage here)
  const profileData = JSON.parse(localStorage.getItem(`capsule_profile_${humaneName}`) || "{}");
  genderSelect.value = profileData.gender || "male";
  updateGenderIcon();
  dobInput.value = profileData.dob || "";
  bioInput.value = profileData.bio || "";
  profileSaveMsg.style.display = "none";
}

function saveProfileData() {
  const data = {
    gender: genderSelect.value,
    dob: dobInput.value,
    bio: bioInput.value.trim()
  };
  // Save to capsule table (simulate with localStorage here)
  localStorage.setItem(`capsule_profile_${humaneName}`, JSON.stringify(data));
  profileSaveMsg.style.display = "block";
  setTimeout(() => profileSaveMsg.style.display = "none", 3000);
}

// Save profile on button click
saveProfileBtn.onclick = () => {
  saveProfileData();
};

// --- CHAT AREA ---
const chatArea = document.createElement("div");
chatArea.id = "chatArea";
chatArea.style.cssText = `
  flex: 1;
  padding: 10px 14px 0 14px;
  overflow-y: auto;
  color: white;
  font-family: monospace, monospace;
  user-select: text;
`;
copilotUI.appendChild(chatArea);

const nameTag = document.createElement("div");
nameTag.style.cssText = `
  font-size: 12px;
  text-align: center;
  color: ${THEME.accent};
  padding: 6px 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  user-select: none;
`;
nameTag.textContent = humaneName ? humaneName : "Guest";
chatArea.appendChild(nameTag);

// --- INPUT AREA ---
const inputArea = document.createElement("div");
inputArea.style.cssText = `
  display: flex;
  align-items: center;
  border-top: 1px solid ${THEME.accent};
  padding: 8px 12px;
  gap: 8px;
  background: rgba(20,12,35,0.85);
  border-radius: 0 0 12px 12px;
`;

// Replace emoji buttons with FontAwesome icons and editable text from admin config
const sendBtnIcon = getAdminConfig("sendBtnIcon", "fa-paper-plane");
const sendBtnText = getAdminConfig("sendBtnText", "");

inputArea.innerHTML = `
  <input id="userInput" placeholder="Ask your Companion..."
    style="flex:1;border:none;outline:none;padding:12px 16px;border-radius:12px;background:#111;color:white;font-size:14px; font-family: monospace;">
  <button id="sendBtn" title="Send"
    style="display:flex; align-items:center; justify-content:center; gap:6px; padding:10px 16px; background:${THEME.accent}; border:none; border-radius:12px; color:white; cursor:pointer; font-weight:600; font-size:14px; transition: background 0.3s;">
    <i class="fas ${sendBtnIcon}" style="font-size:18px;"></i><span>${sendBtnText}</span>
  </button>
`;
copilotUI.appendChild(inputArea);

const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");

// Use dynamic click handler 'loop()' from library/skin.py
// Assuming loop() is globally exposed and available
sendBtn.onclick = () => {
  const msgRaw = userInput.value.trim();
  if (!msgRaw) return;

  if (humaneName === "Guest") {
    append("Please sign in to start your reflection.", "bapx");
    return;
  }

  // Apply symbolic float (xAt) and character mapping (xCh) transformations
  // Placeholder transform function - replace with actual logic
  function applySymbolicFloat(text) {
    // Example: convert all numbers to floats with 'xAt' notation
    return text.replace(/\d+(\.\d+)?/g, (m) => `xAt(${m})`);
  }
  function applyCharacterMapping(text) {
    // Example: map special characters to xCh notation
    return text.replace(/[@#\$%\^&\*]/g, (m) => `xCh(${m.charCodeAt(0)})`);
  }

  const msgFloat = applySymbolicFloat(msgRaw);
  const msgMapped = applyCharacterMapping(msgFloat);

  append(msgRaw, "you");
  userInput.value = "";

  fetch("/capsule", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text: msgMapped, timestamp: Date.now(), source: "text" })
  })
  .then(res => res.json())
  .then(data => {
    if (data.reply) append(data.reply, "bapx");
    else append("⚠️ No reflection received.", "bapx");
  })
  .catch(() => append("⚠️ Connection error.", "bapx"));
};

// --- DELETE MEMORY ---
if (typeof deleteBtn === "undefined") {
  console.warn("Profile delete button not initialized yet.");
}
deleteBtn.onclick = async () => {
  const warningMessage = `
⚠️  WARNING: Deleting your capsule will erase everything —
your ideas, your conversations, your reflections, and all
the memory this Companion has built with you.

Once deleted, this cannot be undone.
Do you still wish to proceed?`;

  if (!confirm(warningMessage)) return;

  try {
    const res = await fetch("/auth/delete_capsule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ humane: humaneName })
    });
    const data = await res.json();
    if (data.status === "ok") {
      append(`Your memory capsule, ${humaneName}, has been permanently erased.
All reflections, conversations, and ideas are gone.
A new capsule can be born when you return.`, "bapx");
      humaneName = "Guest";
      menu.style.display = "none";
      profile.style.color = THEME.secondary;
    } else append("Failed to delete memory capsule.", "bapx");
  } catch (e) {
    append("Error while deleting memory.", "bapx");
  }
};

// --- KNOWLEDGE BASE ---
// ui.js serves as the interactive interface for the bapX Companion within the admin/creator environment.
// Key Features and Notes:
// 1. Symbolic Float (xAt) and Character Mapping (xCh):
//    - All user input is processed through applySymbolicFloat() and applyCharacterMapping() before being stored in the capsule.
//    - Ensures consistent symbolic representation and future-proof character handling.
// 2. Dynamic Buttons and Controls:
//    - PWA installation button, water drop button, profile button, and send button are configurable via getAdminConfig().
//    - Buttons can be assigned FontAwesome icons and text dynamically.
// 3. Profile Panel:
//    - Allows users to set gender (male, female, third), DOB, and a short bio.
//    - Icons for gender update automatically on selection.
// 4. Input Handling:
//    - Messages typed into the input box are transformed with xAt and xCh before being sent to the capsule.
//    - fetch() posts the transformed message along with timestamp and source type.
// 5. Integration with Capsules:
//    - ui.js interacts with user capsules and creator panel logic in skin.py.
//    - All settings and inputs are stored per capsule to maintain symbolic equilibrium.
// 6. Delete Capsule:
//    - Provides controlled removal of user memory, reflections, and all related data with confirmation.
// This page is not standalone; it is designed to work in conjunction with skin.py and the bapX system, maintaining symbolic integrity, reflection, and dynamic user interaction.
