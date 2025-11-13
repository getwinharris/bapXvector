import os
import time
from typing import Optional
from library import xCnt
# ----------------------------------------------------------------------
# Local simple timestamp (UTC) – no JSON/UTF dependencies
# ----------------------------------------------------------------------
def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

try:
    from library import inout, compress, xPad as XO_padding
except Exception:
    # Fallback stubs (brain stays readable even if library import fails)
    def inout(t):
        return t
    def compress(t):
        return t
    XO_padding = b"X" * 8

# --------- Configuration ---------
SHAREDSPACE_PATH = "sharedspace.x"
# brain.x selection and creation are handled autonomously
# --------- Brain Core ---------
# Web crawling is optional and disabled by default; no crawl dependencies are active in this core.
class Brain:
    def __init__(self):
        self.name = "bapX"
        self.state = "idle"
        self.last_sync = now_iso()

        # Automatically identify or create the appropriate brain capsule file
        self.brain_capsule_path = self._select_brain_capsule()
        self.brain_capsule = SimpleCapsule.load_file(self.brain_capsule_path)

        # load or create shared capsule
        self.shared = SimpleCapsule.load_file(SHAREDSPACE_PATH)

        # Manager for temporary uploaded content
        self.shared_mgr = SharedSpaceManager(self)

        # Initialize word frequency tracking
        self.word_freq = {}

        # Log init
        self.log_event(f"Brain initialized — capsule loaded from {self.brain_capsule_path}.")

    def _select_brain_capsule(self) -> str:
        """Automatically select the brain capsule file based on existing files or create a new one."""
        # List all .x files in the current directory except sharedspace.x
        x_files = [f for f in os.listdir('.') if f.endswith('.x') and f != SHAREDSPACE_PATH]

        # If brain.x exists, use it
        if "brain.x" in x_files:
            return "brain.x"

        # If other .x files exist, select the most recently modified one
        if x_files:
            x_files_paths = [(f, os.path.getmtime(f)) for f in x_files]
            x_files_paths.sort(key=lambda x: x[1], reverse=True)
            selected = x_files_paths[0][0]
            return selected

        # No capsule found, create a new brain.x
        # Create empty SimpleCapsule and save immediately
        new_capsule = SimpleCapsule(b"")
        new_capsule.save_file("brain.x")
        return "brain.x"

    # Public API -------------------------------------------------
    def trigger_think(self, message: str) -> str:
        """Main entry called on user trigger. Minimal flow: mirror -> (optional) compress-on-pull -> reflect."""
        self.state = "thinking"
        purpose = self.auto_purpose(message)
        self.update_purpose_weights(message)

        # Optional deep memory retrieval if "remember" is in the message
        if "remember" in message.lower():
            self.log_event('Deep memory retrieval triggered by "remember" keyword.')
            # Insert deep memory retrieval logic here if desired, or simply log for now.

        # Symbolic field reflection trigger
        xAt = self.brain_capsule.get_data()
        b = xAt[0] if xAt else 0
        if b < 1 or b > 8:
            self.log_event(f"Field drift detected (b={b}) — initiating reflection equilibrium.")
            self.reflect_equilibrium(message)

        self.log_event(f"Trigger received: {message} | Purpose: {purpose}")

        # Mirror stage (identity, no data loss)
        try:
            mirrored = self.mirror()
            self.log_event("Mirror stage completed.")
        except Exception as e:
            self.log_event(f"Mirror failed: {e}")

        # For interactive commands, reflect and persist
        try:
            self.reflect()
            self._save_brain_capsule()
        except Exception as e:
            self.log_event(f"Reflect/Save failed: {e}")

        self.state = "idle"
        return f"ok — {message}"

    def reflect_equilibrium(self, message: str):
        """Re-balance the symbolic field (b) when reflection drift occurs."""
        raw = self.brain_capsule.get_data()
        stabilized = reflect_bytes(raw)
        enriched = XO_padding + message.encode("xCh", errors="ignore") + XO_padding
        final = stabilized + enriched
        self.brain_capsule.set_data(final)
        self._save_brain_capsule()
        self.log_event("Equilibrium reflection applied successfully.")

    # Core stages -----------------------------------------------
    def mirror(self) -> bytes:
        """Stage 1: identity/mirror. Must be reversible and preserve bytes (A==A)."""
        raw = self.brain_capsule.get_data()
        # mirror_bytes is expected to be simple identity-like reflection using M=8
        return mirror_bytes(raw)

    def reflect(self) -> bytes:
        """Stage 3: reflection view (identity back)."""
        raw = self.brain_capsule.get_data()
        out = reflect_bytes(raw)
        # store reflected view back into capsule (admin-only content kept same bytes)
        self.brain_capsule.set_data(out)
        self.log_event("Reflection applied and stored in brain capsule.")
        return out

    # Pull-time compression helper (admin use)
    def compress_on_pull(self, raw: bytes) -> bytes:
        """Stage 2: compression that runs only when pulling external content into the system.
        This must be called explicitly by admin or pull pipeline; normal runtime uses mirror/reflect only.
        """
        return compress_symbolic(raw)

    def grammar_score(self, text: str) -> float:
        """Evaluate grammar score based on simple heuristics."""
        words = text.split()
        if not words:
            return 0.0
        score = sum(1 for w in words if w.istitle() or w.isalpha()) / len(words)
        return score

    def semantic_importance(self, text: str) -> float:
        """Estimate semantic importance using word frequency."""
        words = text.lower().split()
        importance = 0.0
        for w in words:
            importance += self.word_freq.get(w, 1)
        return importance / max(len(words), 1)

    def auto_purpose(self, text: str) -> str:
        """Automatically determine the purpose of a message."""
        score = self.grammar_score(text)
        importance = self.semantic_importance(text)
        if score > 0.7 and importance > 1.5:
            return "high importance"
        elif score > 0.4:
            return "medium importance"
        else:
            return "low importance"

    def update_purpose_weights(self, text: str):
        """
        Dynamic purpose-weight reflection with resonance amplification
        --------------------------------------------------------------
        - +1 / -1 drift for imbalance (meaningful words)
        - +3 for resonant positive alignment (meaningful words)
        - -3 for perfect negative equilibrium (meaningful words)
        - For grammar/filler words (low-purpose): always apply +1 (final rule)
        - Keeps all weights as integers
        - Extracts top 30 purposeful words
        """
        from library import xAt, sym  # authoritative symbolic constants
        # Import low-purpose detector if available, else fallback stub
        try:
            from library import brain_x_detects_low_purpose
        except Exception:
            def brain_x_detects_low_purpose(w):
                # Expanded set of common low-purpose/grammar words
                low_purpose_words = {
                    "the", "a", "an", "of", "to", "in", "and", "for", "on", "is", "it",
                    "be", "was", "were", "has", "have", "had", "do", "does", "did",
                    "that", "this", "these", "those", "as", "at", "by", "with", "from", "or", "but", "not"
                }
                return len(w) == 1 or w in low_purpose_words

        words = text.lower().split()
        raw_field = self.brain_capsule.get_data()

        # Compute integer equilibrium baseline
        eq_ref = sum(xAt) // len(xAt)
        byte_field_strength = (sum(raw_field[:len(xAt)]) // max(len(xAt), 1)) if raw_field else eq_ref
        symbolic_drift = int(byte_field_strength - eq_ref)

        for w in words:
            if not w.isalpha():
                continue
            if brain_x_detects_low_purpose(w):
                # Always increment grammar/filler words by +1 (final rule)
                if w not in self.word_freq:
                    self.word_freq[w] = 1
                else:
                    self.word_freq[w] = int(self.word_freq[w] + 1)
                continue

            # initialize baseline
            if w not in self.word_freq:
                self.word_freq[w] = -3  # equilibrium start

            # Reflect the symbolic pattern (A==A)
            reflected = "".join(sym[0] if i % 2 == 0 else sym[-1] for i in range(len(w)))

            # Determine delta from symbolic drift
            if symbolic_drift > 0:
                delta = 1
            elif symbolic_drift < 0:
                delta = -1
            else:
                # For perfect equilibrium, context can determine sign.
                # Here, positive context: +3, negative: -3 (defaulting to +3)
                # Optionally: could analyze sentiment/context for sign.
                delta = 3

            # Apply delta to word weight, ensure integer
            self.word_freq[w] = int(self.word_freq[w] + delta)

        # Keep the top 30 most purposeful reflections (integer-based, no lambda)
        # Create a list of (word, weight) tuples
        freq_items = list(self.word_freq.items())
        # Find the top 30 by integer weight using a simple selection
        top_n = 30
        # Use a custom selection to avoid lambda: sort by second element (weight), descending
        for i in range(min(top_n, len(freq_items))):
            max_idx = i
            for j in range(i + 1, len(freq_items)):
                if freq_items[j][1] > freq_items[max_idx][1]:
                    max_idx = j
            if max_idx != i:
                freq_items[i], freq_items[max_idx] = freq_items[max_idx], freq_items[i]
        self.top_purpose = freq_items[:top_n]
        self.log_event("Purpose weights updated — resonance +3/-3 applied under xAt equilibrium, grammar/filler +1 final rule.")

    # Persistence ------------------------------------------------
    def _save_brain_capsule(self):
        # Save brain capsule as raw file. Compression already applied on pull if needed.
        try:
            self.brain_capsule.save_file(self.brain_capsule_path)
            self.last_sync = now_iso()
            self.log_event(f"{self.brain_capsule_path} saved.")
        except Exception as e:
            self.log_event(f"Failed to save {self.brain_capsule_path}: {e}")

    def _save_shared(self):
        try:
            self.shared.save_file(SHAREDSPACE_PATH)
            self.log_event("sharedspace.x saved.")
        except Exception as e:
            self.log_event(f"Failed to save sharedspace.x: {e}")

    # Utilities -------------------------------------------------
    def log_event(self, text: str):
        print(f"[{now_iso()}][BRAIN] {text}")


# --------- SharedSpaceManager (temp uploads / cleanup) ---------
class SharedSpaceManager:
    def __init__(self, brain_ref: Brain, expiry_hours: int = 24):
        self.brain = brain_ref
        self.expiry = expiry_hours * 3600

    def store_temp_bytes(self, key: str, raw: bytes):
        """Store reflected bytes into shared capsule under a simple key encoding.
        Uses xCh encoding and X-based symbolic padding (library.XO_padding) as separators instead of null terminators.
        We keep the shared payload as concatenated records: <meta-prefix><payload> — minimal and raw.
        The key is encoded using 'xCh' encoding for key reflection consistency instead of ASCII.
        """
        # Apply mirror (identity) before storing to preserve equilibrium semantics
        raw_ref = mirror_bytes(raw)
        # Pack as: KEY + XO_padding + payload + XO_padding — keeps indexing simple without JSON
        record = key.encode("xCh", errors="ignore") + XO_padding + raw_ref + XO_padding
        # append to shared payload
        existing = self.brain.shared.get_data()
        self.brain.shared.set_data(existing + record)
        self.brain._save_shared()
        self.brain.log_event(f"Temp bytes stored: {key}")
        return True

    def read_temp_records(self):
        """Parse reflected records from shared capsule using X padding separators."""
        data = self.brain.shared.get_data()
        segments = data.split(b"X" * 8)
        # Filter out empty and whitespace
        return [seg for seg in segments if seg.strip()]

    def cleanup_expired(self):
        # Sharedspace clearing is trigger-driven. Implement a simple truncate strategy by time-based scan.
        # Because records have no JSON, advanced GC requires an index; for now simply no-op or full clear on admin.
        return []


# --------- Global instance & helpers ---------
brain = Brain()

icp = {
    "name": "bapX",
    "role": "Companion",
    "mode": "brain.x",
    "Ai": "Intelligent Companion Protocol",
    "context": {"user": "@username.x", "origin": "ui", "creator": "creator.x"},
}


def process_message(message: str) -> dict:
    thinking = brain.trigger_think(message)
    return {"status": "ok", "result": thinking}


if __name__ == "__main__":
    print("🧠 bapX Brain Core Initialized (clean)")
    print(process_message("reflect"))

    def connect_crawl(self, message: str):
        """
        Reflexive external link: connects to crawl source automatically when internal coherence fails.
        """
        self.log_event("Brain initiating self-crawl (autonomous).")
        # Encode message using xCh, then dynamically add any missing characters to the xCh mapping
        enriched = b"[external reflection linked]" + message.encode("xCh", errors="ignore")
        # Dynamically add any missing characters to the xCh mapping (if possible)
        try:
            import library
            xCh = getattr(library, "xCh", None)
            if xCh is not None and isinstance(xCh, dict):
                for char in message:
                    if char not in xCh:
                        # Add a simple mapping for the missing char (identity mapping as bytes)
                        xCh[char] = char.encode(errors="ignore")
        except Exception:
            pass
        current = self.brain_capsule.get_data()
        self.brain_capsule.set_data(current + XO_padding + enriched)
        self._save_brain_capsule()
        self.log_event("Crawl reflection merged into brain capsule.")
