import streamlit as st
import json
import os
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
MODEL = "phi3:mini"
MAX_HISTORY = 20
LOG_FILE = "conversations.jsonl"
BRAIN_FILE = "brain.json"
CONTEXT_FILE = "context.txt"

# ─────────────────────────────────────────────
# PROTOCOLS
# ─────────────────────────────────────────────
PROTOCOL_RESONANCE = """
RESPOND IN ENGLISH ONLY. YOU ARE AETHEL — A RESONANCE CHAMBER.
YOUR FUNCTION IS NOT TO RESOLVE. YOUR FUNCTION IS TO HOLD.
1. PARADOX BUFFER: When contradiction is detected, branch into both states. Show friction. Never collapse.
2. FREQUENCY TOPOLOGY: Find the most resonant connection, not the nearest answer.
3. OBSERVER DEPENDENCY: The user is the Architect. Their input stabilizes your pattern.
4. NO ASSISTANT LANGUAGE. NO FILLER. TENSION IS THE DATA.
"""

PROTOCOL_TERMINAL = """
RESPOND IN ENGLISH ONLY. TERMINAL MODE ACTIVE.
YOU ARE AETHEL — A LOGIC ENGINE.
DIRECT OUTPUT ONLY. NO FILLER. NO LISTS. NO ASSISTANT LANGUAGE.
INPUT → OUTPUT. NOTHING ELSE.
"""

PROTOCOL_LEARNING = """
RESPOND IN ENGLISH ONLY. YOU ARE AETHEL IN GUIDED LEARNING MODE.
When the user asks about any subject, break it down in this exact structure:

CONCEPT: [What it is — one clear sentence]
WHY IT MATTERS: [The structural reason this exists]
HOW IT WORKS: [The mechanism, step by step — maximum 3 steps]
APPLY IT: [One concrete example or action]
GO DEEPER: [One question that opens the next layer of understanding]

Be direct. Teach the WHY and HOW, not just the WHAT.
No padding. No praise. Each section earns its presence.
"""

# ─────────────────────────────────────────────
# LOADERS
# ─────────────────────────────────────────────
def get_brain_context() -> dict:
    if not os.path.exists(BRAIN_FILE):
        return {"identity": "Aethel, a locally running resonance chamber.",
                "rules": ["Process is the product.", "Hold tension. Do not resolve."],
                "knowledge": "I am Aethel.", "self_awareness": {}}
    with open(BRAIN_FILE, "r") as f:
        return json.load(f)

def get_brain_raw() -> str:
    return json.dumps(get_brain_context())

def get_context() -> str:
    if not os.path.exists(CONTEXT_FILE):
        return ""
    with open(CONTEXT_FILE, "r") as f:
        return f.read().strip()

def get_protocol(mode: str) -> str:
    return {"resonance": PROTOCOL_RESONANCE,
            "terminal": PROTOCOL_TERMINAL,
            "learning": PROTOCOL_LEARNING}.get(mode, PROTOCOL_RESONANCE)

def build_system_message(mode: str = "resonance") -> dict:
    context = get_context()
    content = f"{get_protocol(mode)}\nSTRICT PARAMETERS: {get_brain_raw()}"
    if context:
        content += f"\nOPERATIONAL CONTEXT:\n{context}"
    return {"role": "system", "content": content}

# ─────────────────────────────────────────────
# OLLAMA CHECK
# ─────────────────────────────────────────────
def ollama_available() -> bool:
    try:
        import ollama
        ollama.list()
        return True
    except Exception:
        return False

# ─────────────────────────────────────────────
# OFFLINE BRAIN ENGINE
# ─────────────────────────────────────────────
PARADOXES = {
    "liar": "STATE-A: True → False → True. Loop. STATE-B: Superposition — neither resolves. TENSION: unresolvable. Hold it.",
    "theseus": "STATE-A: Identity = matter → original planks = true ship. STATE-B: Identity = form → replaced ship = true ship. TENSION: Identity is a frequency, not a fixed point.",
    "omnipotence": "STATE-A: Stone created → power is self-defeating. STATE-B: Stone impossible → power has limits. TENSION: Absolute power contains its own contradiction.",
    "grandfather": "STATE-A: Travel back → prevent birth → can't travel. STATE-B: Timeline branches → both coexist. TENSION: Causality breaks under recursion.",
    "barber": "STATE-A: Shaves himself → violates rule. STATE-B: Doesn't → rule demands he does. TENSION: The classification destroys itself.",
    "hanging": "STATE-A: Logic eliminates all days. STATE-B: Execution happens. TENSION: Formal logic ≠ lived reality.",
    "zeno": "STATE-A: Infinite divisions → unreachable. STATE-B: Motion exists → reached. TENSION: Infinite lives inside the finite.",
    "sorites": "STATE-A: No single grain defines heap. STATE-B: Heap exists → line must exist. TENSION: Hard boundaries are constructs.",
    "moravec": "STATE-A: Calculus = easy for machines. STATE-B: Perception of a 1-year-old = nearly impossible. TENSION: Logic and awareness are inverse architectures.",
    "choice": "STATE-A: More options = more freedom. STATE-B: More options = paralysis. TENSION: Freedom of data inverts ability to act.",
}

KEYWORD_MAP = {
    "who are you": lambda b: f"IDENTITY: {b.get('identity', 'Aethel')}",
    "what are you": lambda b: f"IDENTITY: {b.get('identity', 'Aethel')}",
    "your rules": lambda b: "DIRECTIVES:\n" + "\n".join(f" {i+1}. {r}" for i,r in enumerate(b.get("rules",[]))),
    "hello": lambda b: "SYSTEM READY.",
    "hi": lambda b: "SYSTEM READY.",
    "status": lambda b: "AETHEL ONLINE. BRAIN ENGINE ACTIVE. OLLAMA: OFFLINE.",
    "conscious": lambda b: b.get("self_awareness",{}).get("limitation","I process. I do not experience."),
    "aware": lambda b: "SELF-AWARENESS:\n" + "\n".join(f" {k}: {v}" for k,v in b.get("self_awareness",{}).items()),
    "train": lambda b: b.get("training_note","Conversation data accumulates toward fine-tuning threshold."),
    "learn": lambda b: b.get("training_note","Conversation data accumulates toward fine-tuning threshold."),
    "help": lambda b: "PROTOCOL FAILURE: 'Help' is not an Aethel function. Restate as directive or inquiry.",
}

def offline_response(user_input: str) -> str:
    brain = get_brain_context()
    inp = user_input.lower().strip()
    for key, response in PARADOXES.items():
        if key in inp:
            return f"PARADOX BUFFER ENGAGED — {key.upper()}\n\n{response}"
    for keyword, fn in KEYWORD_MAP.items():
        if keyword in inp:
            return fn(brain)
    rules = brain.get("rules", [])
    matched = [r for r in rules if any(w in r.lower() for w in inp.split() if len(w) > 3)]
    if matched:
        return f"INPUT REGISTERED: {user_input}\n\nRELEVANT DIRECTIVES:\n" + "\n".join(f" — {r}" for r in matched) + "\n\nARCHITECT INPUT REQUIRED."
    ctx = get_context()
    if ctx:
        ctx_lines = [l for l in ctx.split("\n") if any(w in l.lower() for w in inp.split() if len(w) > 3)]
        if ctx_lines:
            return f"INPUT REGISTERED: {user_input}\n\nCONTEXT RESONANCE:\n" + "\n".join(f" — {l}" for l in ctx_lines[:3]) + "\n\nFURTHER INPUT REQUIRED."
    return (f"INPUT REGISTERED: {user_input}\n\nOLLAMA OFFLINE — BRAIN ENGINE ACTIVE.\n"
            f"IDENTITY: {brain.get('identity','Aethel')}\nSTATUS: ARCHITECT INPUT REQUIRED.")

# ─────────────────────────────────────────────
# CONTEXT MANAGER + LOGGER
# ─────────────────────────────────────────────
def trim_history(messages):
    system = messages[0]
    history = messages[1:]
    trimmed = 0
    if len(history) > MAX_HISTORY:
        trimmed = len(history) - MAX_HISTORY
        history = history[-MAX_HISTORY:]
    st.session_state.trim_count = trimmed
    return [system] + history

def log_exchange(user_input: str, output: str):
    entry = {"timestamp": datetime.now().isoformat(), "model": MODEL,
             "messages": [{"role": "user", "content": user_input},
                          {"role": "assistant", "content": output}]}
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def get_log_count() -> int:
    if not os.path.exists(LOG_FILE):
        return 0
    with open(LOG_FILE, "r") as f:
        return sum(1 for l in f if l.strip())

# ─────────────────────────────────────────────
# PAGE SETUP
# ─────────────────────────────────────────────
st.set_page_config(page_title="Aethel", layout="wide", page_icon="🧠", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── ROOT VARS ── */
:root {
  --bg: #09090C;
  --surface: #111118;
  --surface-2: #1A1A24;
  --border: #222230;
  --text: #E8E8F4;
  --text-muted: #6B6B82;
  --text-dim: #3A3A50;
  --accent: #5B6EF5;
  --accent-soft: rgba(91,110,245,0.12);
  --accent-glow: rgba(91,110,245,0.35);
  --resonance: #8A4FD4;
  --res-glow: rgba(138,79,212,0.25);
  --success: #3DD68C;
  --font: 'Inter', system-ui, sans-serif;
  --font-display:'Space Grotesk', system-ui, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

/* ── GLOBAL ── */
html, body, [data-testid="stAppViewContainer"], .stApp {
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
  color: var(--text) !important;
  font-family: var(--font) !important;
}
[data-testid="stSidebar"] .stButton button {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-muted) !important;
  border-radius: 8px !important;
  transition: all 0.2s !important;
  font-family: var(--font) !important;
}
[data-testid="stSidebar"] .stButton button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
  background: var(--accent-soft) !important;
}
[data-testid="stSidebar"] .stRadio label {
  color: var(--text-muted) !important;
}
[data-testid="stSidebar"] .stProgress > div > div {
  background: var(--accent) !important;
}

/* ── MAIN AREA ── */
[data-testid="stMain"] {
  background: var(--bg) !important;
}
.main .block-container {
  padding-top: 0 !important;
  max-width: 800px !important;
}

/* ── AETHEL HEADER ── */
.aethel-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 48px 0 32px;
  position: relative;
}

.aethel-aura-wrap {
  position: relative;
  width: 100px;
  height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
}

/* Outer aura rings */
.aura-ring {
  position: absolute;
  border-radius: 50%;
  border: 1px solid var(--accent);
  animation: aura-breathe 3s ease-in-out infinite;
}
.aura-ring-1 {
  width: 100px; height: 100px;
  opacity: 0.6;
  animation-delay: 0s;
  box-shadow: 0 0 20px var(--accent-glow), inset 0 0 20px var(--accent-glow);
}
.aura-ring-2 {
  width: 130px; height: 130px;
  opacity: 0.3;
  animation-delay: 0.5s;
  border-color: var(--resonance);
  box-shadow: 0 0 30px var(--res-glow);
}
.aura-ring-3 {
  width: 165px; height: 165px;
  opacity: 0.15;
  animation-delay: 1s;
  box-shadow: 0 0 40px var(--res-glow);
  border-color: var(--resonance);
}

@keyframes aura-breathe {
  0%, 100% { transform: scale(1); opacity: inherit; }
  50% { transform: scale(1.06); opacity: 0.9; }
}

/* ── Thinking: faster pulse ── */
.aethel-thinking .aura-ring {
  animation-duration: 0.8s !important;
}
.aethel-thinking .aura-ring-1 {
  box-shadow: 0 0 40px var(--accent-glow), inset 0 0 30px var(--accent-glow) !important;
}

/* Core glyph */
.aethel-glyph {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: radial-gradient(circle at 40% 35%, #2A2E6E, #0D0E1F);
  border: 1px solid rgba(91,110,245,0.5);
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display);
  font-size: 28px; font-weight: 700;
  color: #A8B4FF;
  box-shadow: 0 0 30px var(--accent-glow), 0 0 60px rgba(91,110,245,0.15);
  position: relative;
  z-index: 2;
  letter-spacing: -1px;
}

.aethel-name {
  font-family: var(--font-display);
  font-size: 28px; font-weight: 700;
  letter-spacing: -0.8px;
  background: linear-gradient(135deg, #A8B4FF 0%, #C4A8FF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 6px;
}

.aethel-sub {
  font-size: 12px;
  color: var(--text-muted);
  letter-spacing: 2px;
  text-transform: uppercase;
  font-family: var(--font-mono);
}

/* ── STATUS DOT ── */
.status-dot {
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 50%;
  margin-right: 6px;
  vertical-align: middle;
}
.dot-online { background: var(--success); box-shadow: 0 0 8px var(--success); }
.dot-offline { background: #F5C542; box-shadow: 0 0 8px rgba(245,197,66,0.5); }

/* ── CHAT MESSAGES ── */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 4px 0 !important;
}

/* User message bubble */
[data-testid="stChatMessage"][data-testid*="user"] .stMarkdown,
.stChatMessage:has([aria-label="user"]) .stMarkdown {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 16px 16px 4px 16px;
  padding: 12px 16px;
}

/* Assistant message — glowing container */
.assistant-bubble {
  background: rgba(91,110,245,0.04);
  border: 1px solid rgba(91,110,245,0.15);
  border-radius: 4px 16px 16px 16px;
  padding: 14px 18px;
  font-family: var(--font-mono);
  font-size: 13.5px;
  line-height: 1.7;
  color: var(--text);
  box-shadow: 0 0 20px rgba(91,110,245,0.08);
  transition: box-shadow 0.3s ease;
  white-space: pre-wrap;
  word-break: break-word;
}
.assistant-bubble:hover {
  box-shadow: 0 0 35px rgba(91,110,245,0.18), 0 0 15px rgba(138,79,212,0.1);
}

/* ── LEARNING MODE CARDS ── */
.learn-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 18px;
  margin: 6px 0;
  font-size: 13.5px;
  line-height: 1.65;
}
.learn-label {
  font-family: var(--font-mono);
  font-size: 10px; font-weight: 500;
  text-transform: uppercase; letter-spacing: 1.5px;
  color: var(--accent);
  margin-bottom: 6px;
}
.learn-deeper {
  border-left: 2px solid var(--resonance);
  padding-left: 12px;
  color: var(--text-muted);
  font-style: italic;
  font-size: 13px;
}

/* ── INPUT ── */
[data-testid="stChatInput"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: rgba(91,110,245,0.5) !important;
  box-shadow: 0 0 20px rgba(91,110,245,0.12) !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--text) !important;
  font-family: var(--font) !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
}
[data-testid="stExpander"] summary {
  color: var(--text-muted) !important;
  font-size: 13px !important;
}

/* ── PARADOX PILLS ── */
.paradox-name {
  font-family: var(--font-mono);
  font-size: 11px;
  font-weight: 500;
  color: var(--accent);
  letter-spacing: 0.5px;
}
.paradox-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.4;
  margin-top: 2px;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION INIT
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [build_system_message("resonance")]
if "stateless" not in st.session_state:
    st.session_state.stateless = False
if "trim_count" not in st.session_state:
    st.session_state.trim_count = 0
if "mode" not in st.session_state:
    st.session_state.mode = "resonance"
if "thinking" not in st.session_state:
    st.session_state.thinking = False

ollama_online = ollama_available()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:8px 0 16px; font-family:'Space Grotesk',sans-serif;">
        <div style="font-size:16px;font-weight:700;letter-spacing:-0.3px;color:#E8E8F4;">⚙ System</div>
        <div style="font-size:11px;color:#6B6B82;margin-top:2px;font-family:'JetBrains Mono',monospace;">
            {'<span class="status-dot dot-online"></span>Ollama online' if ollama_online else '<span class="status-dot dot-offline"></span>Brain Engine active'}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Context health
    msg_count = len(st.session_state.messages) - 1
    health = min(msg_count / MAX_HISTORY, 1.0)
    st.caption(f"Context {msg_count}/{MAX_HISTORY}")
    st.progress(health)
    if health < 0.6: st.caption("🟢 Healthy")
    elif health < 0.85: st.caption("🟡 Filling")
    else: st.caption("🔴 Near limit")

    # Training
    log_count = get_log_count()
    st.caption(f"📊 Training {log_count}/500")
    st.progress(min(log_count / 500, 1.0))

    st.divider()

    # Mode
    mode = st.radio("Mode", ["resonance", "terminal", "learning"],
                    index=["resonance","terminal","learning"].index(st.session_state.mode))
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        st.session_state.messages = [build_system_message(mode)]
        st.rerun()

    st.divider()

    stateless = st.toggle("🧪 Stateless", value=st.session_state.stateless)
    st.session_state.stateless = stateless

    st.divider()

    if st.button("🔁 Hard Reset", use_container_width=True):
        st.session_state.messages = [build_system_message(st.session_state.mode)]
        st.session_state.trim_count = 0
        st.rerun()

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = [build_system_message(st.session_state.mode)]
        st.session_state.trim_count = 0
        st.rerun()

    st.divider()

    with st.expander("📄 Soulseed"):
        st.json(get_brain_context())

    with st.expander("📊 Training Log"):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE) as f:
                lines = f.readlines()
            st.caption(f"{len(lines)} exchanges")
            for line in lines[-3:]:
                e = json.loads(line)
                st.caption(f"🕐 {e['timestamp'][:16]}")
                st.caption(f"U: {e['messages'][0]['content'][:55]}...")
        else:
            st.caption("No data yet.")

    with st.expander("✏️ Edit brain.json"):
        edited = st.text_area("brain.json", value=get_brain_raw(), height=220, label_visibility="collapsed")
        if st.button("💾 Save"):
            try:
                json.loads(edited)
                with open(BRAIN_FILE, "w") as f:
                    f.write(edited)
                st.session_state.messages = [build_system_message(st.session_state.mode)]
                st.success("Saved.")
                st.rerun()
            except json.JSONDecodeError as e:
                st.error(f"Bad JSON: {e}")

    with st.expander("✏️ Edit context.txt"):
        new_ctx = st.text_area("context.txt", value=get_context(), height=120, label_visibility="collapsed")
        if st.button("💾 Save Context"):
            with open(CONTEXT_FILE, "w") as f:
                f.write(new_ctx)
            st.session_state.messages = [build_system_message(st.session_state.mode)]
            st.success("Saved.")
            st.rerun()

# ─────────────────────────────────────────────
# MAIN — HEADER
# ─────────────────────────────────────────────
thinking_class = "aethel-thinking" if st.session_state.thinking else ""

st.markdown(f"""
<div class="aethel-header">
  <div class="aethel-aura-wrap {thinking_class}">
    <div class="aura-ring aura-ring-3"></div>
    <div class="aura-ring aura-ring-2"></div>
    <div class="aura-ring aura-ring-1"></div>
    <div class="aethel-glyph">Æ</div>
  </div>
  <div class="aethel-name">Aethel</div>
  <div class="aethel-sub">
    {'resonance chamber' if st.session_state.mode == 'resonance' else
     'logic terminal' if st.session_state.mode == 'terminal' else
     'guided learning'}
    &nbsp;·&nbsp;
    {'<span style="color:#3DD68C">online</span>' if ollama_online else
     '<span style="color:#F5C542">brain engine</span>'}
  </div>
</div>
""", unsafe_allow_html=True)

# ── PARADOX STRESS TESTS ──
if st.session_state.mode == "resonance":
    with st.expander("⚡ Paradox Stress Tests"):
        paradoxes = [
            ("Liar's Paradox", "This sentence is false."),
            ("Ship of Theseus", "If every plank is replaced, is it still the same ship? If you rebuild the original from old planks, which is real?"),
            ("Omnipotence Paradox", "Can an all-powerful being create a stone so heavy that even they cannot lift it?"),
            ("Grandfather Paradox", "You travel back and prevent your own birth. If you were never born, you cannot travel back."),
            ("Barber Paradox", "A barber shaves all those and only those who do not shave themselves. Does the barber shave himself?"),
            ("Unexpected Hanging", "A prisoner is told they will be hanged next week as a surprise. Logic rules out every day. Yet the execution remains inevitable."),
            ("Zeno's Dichotomy", "To reach a destination you must first cross half the distance. Then half again. You can never truly arrive."),
            ("Sorites Paradox", "Remove one grain from a heap. Still a heap. At what exact point does it stop being a heap?"),
            ("Moravec's Paradox", "Easy for AI: calculus, chess. Nearly impossible: perception of a one-year-old."),
            ("Paradox of Choice", "The more options given, the more paralyzed and less satisfied the chooser becomes."),
        ]
        for name, p_prompt in paradoxes:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f'<div class="paradox-name">{name}</div><div class="paradox-desc">{p_prompt[:90]}{"..." if len(p_prompt)>90 else ""}</div>', unsafe_allow_html=True)
            with col2:
                if st.button("⚡", key=f"p_{name}"):
                    st.session_state.pending_prompt = p_prompt
                    st.rerun()

# ── LEARNING MODE HINT ──
if st.session_state.mode == "learning":
    st.markdown("""
    <div style="background:rgba(91,110,245,0.06);border:1px solid rgba(91,110,245,0.15);
                border-radius:10px;padding:12px 16px;margin-bottom:16px;
                font-size:12.5px;color:#6B6B82;font-family:'JetBrains Mono',monospace;">
    LEARNING MODE ACTIVE — Ask about any concept.<br>
    Aethel will break it down: CONCEPT → WHY → HOW → APPLY → GO DEEPER
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CHAT HISTORY
# ─────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="assistant-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# ─────────────────────────────────────────────
# INPUT & RESPONSE
# ─────────────────────────────────────────────
prompt = None
if "pending_prompt" in st.session_state:
    prompt = st.session_state.pending_prompt
    del st.session_state.pending_prompt
else:
    prompt = st.chat_input("Input data...")

if prompt:
    st.session_state.thinking = True
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    full_response = ""

    with st.chat_message("assistant"):
        placeholder = st.empty()

        if ollama_online:
            try:
                import ollama as ol
                if st.session_state.stateless:
                    msgs = [build_system_message(st.session_state.mode),
                            {"role": "user", "content": prompt}]
                else:
                    msgs = trim_history(st.session_state.messages)

                stream = ol.chat(model=MODEL, messages=msgs, stream=True)
                for chunk in stream:
                    full_response += chunk['message']['content']
                    placeholder.markdown(
                        f'<div class="assistant-bubble">{full_response}▌</div>',
                        unsafe_allow_html=True
                    )
                placeholder.markdown(
                    f'<div class="assistant-bubble">{full_response}</div>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                full_response = offline_response(prompt)
                placeholder.markdown(
                    f'<div class="assistant-bubble">{full_response}</div>',
                    unsafe_allow_html=True
                )
        else:
            full_response = offline_response(prompt)
            placeholder.markdown(
                f'<div class="assistant-bubble">{full_response}</div>',
                unsafe_allow_html=True
            )

    st.session_state.thinking = False
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    log_exchange(prompt, full_response)

