# app.py
import streamlit as st
import random
import secrets
import time
import matplotlib.pyplot as plt

from daa_project import sieve, is_probable_prime
from daa_1 import compare_algorithms
from rsa_simulation import RSA  

# Custom CSS for blueish buttons
st.markdown("""
<style>
    /* All buttons - Blue theme */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #4fc3f7 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5568d3 0%, #3ea9d8 100%);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
        box-shadow: 0 1px 2px rgba(102, 126, 234, 0.3);
    }
    
    /* Primary buttons - Darker blue */
    button[kind="primary"] {
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
    }
    
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Config + session defaults
# -------------------------
st.set_page_config(page_title="Cryptographic Prime Toolkit", layout="wide")

# pages list (human-friendly labels)
PAGES = [
    "Large Prime Generation",
    "AKS vs Miller–Rabin Comparison",
    "RSA Simulation"
]

# initialize session_state keys
st.session_state.setdefault("current_page", PAGES[0])
st.session_state.setdefault("small_primes", [])
st.session_state.setdefault("probable_primes", [])
st.session_state.setdefault("rsa", None)
st.session_state.setdefault("cipher", "")

# Sidebar navigation (keep in sync with session_state)
# Compute index safely
try:
    idx = PAGES.index(st.session_state["current_page"])
except Exception:
    idx = 0
page = st.sidebar.radio("Navigate", PAGES, index=idx)
# update state when user selects from sidebar
if page != st.session_state["current_page"]:
    st.session_state["current_page"] = page
    # no rerun here — we'll just continue rendering the chosen page

# Helper to programmatically navigate to a page and refresh UI
def go_to(page_name: str):
    st.session_state["current_page"] = page_name
    st.rerun()   # refresh immediately so sidebar reflects change

# -------------------------------
# PAGE 1: Large Prime Generation
# -------------------------------
if st.session_state["current_page"] == "Large Prime Generation":
    st.title("🔍 Prime Number Generation & Testing")
    st.write("Generate primes (Sieve) and test numbers (Miller–Rabin). Primes are stored in memory for reuse.")

    st.subheader("1 — Generate base primes (Sieve)")
    limit_input = st.text_input("Sieve limit (max 5,000,000)", value="100000", key="sieve_limit")

    if st.button("Run Sieve", key="run_sieve"):
        if not limit_input.strip() or not limit_input.isdigit():
            st.error("Please enter a valid integer limit (digits only).")
        else:
            limit = int(limit_input)
            if limit < 1000:
                st.error("Limit too small — use ≥ 1,000.")
            elif limit > 5_000_000:
                st.error("Limit too large — use ≤ 5,000,000.")
            else:
                with st.spinner("Running sieve..."):
                    t0 = time.perf_counter()
                    primes = sieve(limit)
                    t1 = time.perf_counter()
                    st.session_state["small_primes"] = primes
                    st.success(f"Generated {len(primes)} primes in {t1 - t0:.4f} s")

    st.divider()
    st.subheader("2 — Miller–Rabin testing (use generated primes)")

    if not st.session_state["small_primes"]:
        st.warning("Run the sieve first to get a small-primes list.")
    else:
        small_primes = st.session_state["small_primes"]
        mode = st.radio("Mode", ["Single Number", "Range", "Random Number"], key="mode_main")

        # Single number
        if mode == "Single Number":
            n_str = st.text_input("Enter number to test", key="single_n")
            if st.button("Test Number", key="btn_test_single"):
                if not n_str.strip() or not n_str.isdigit():
                    st.error("Enter a valid integer (digits only).")
                else:
                    n = int(n_str)
                    if n < 2:
                        st.error("Enter integer ≥ 2.")
                    elif n > 10**10:
                        st.error("Number too large — use ≤ 1e10.")
                    else:
                        t0 = time.perf_counter()
                        res = is_probable_prime(n)
                        t1 = time.perf_counter()
                        if res:
                            st.success(f"{n} → Probably prime (checked in {t1-t0:.6f}s)")
                            if n not in st.session_state["probable_primes"]:
                                st.session_state["probable_primes"].append(n)
                        else:
                            st.error(f"{n} → Composite (checked in {t1-t0:.6f}s)")

        # Range
        elif mode == "Range":
            start_s = st.text_input("Range start", key="range_start")
            end_s = st.text_input("Range end", key="range_end")
            if st.button("Check Range", key="btn_check_range"):
                if not (start_s.isdigit() and end_s.isdigit()):
                    st.error("Enter valid digits for start and end.")
                else:
                    start_n = int(start_s); end_n = int(end_s)
                    if start_n >= end_n:
                        st.error("Start must be smaller than end.")
                    elif end_n - start_n > 10000:
                        st.error("Range too large; limit to 10,000 numbers")
                    else:
                        found = []
                        with st.spinner("Testing range..."):
                            t0 = time.perf_counter()
                            for x in range(start_n, end_n+1):
                                if all(x % p != 0 for p in small_primes if p < x):
                                    if is_probable_prime(x):
                                        found.append(x)
                                        if x not in st.session_state["probable_primes"]:
                                            st.session_state["probable_primes"].append(x)
                            t1 = time.perf_counter()
                        st.success(f"Found {len(found)} probable primes in {t1-t0:.4f}s")
                        if found:
                            st.text_area("Probable primes (scrollable)", ", ".join(map(str, found)), height=160)

        # Random number
        elif mode == "Random Number":
            lo = st.text_input("Lower bound", key="rand_lo")
            hi = st.text_input("Upper bound", key="rand_hi")
            if st.button("Generate & Test", key="btn_rand_test"):
                if not (lo.isdigit() and hi.isdigit()):
                    st.error("Enter digits only.")
                else:
                    l, h = int(lo), int(hi)
                    if l >= h:
                        st.error("Lower must be < Upper.")
                    else:
                        n = random.randint(l, h)
                        st.info(f"Testing random number {n} ...")
                        t0 = time.perf_counter()
                        r = is_probable_prime(n)
                        t1 = time.perf_counter()
                        if r:
                            st.success(f"{n} → Probably prime ({t1-t0:.6f}s)")
                            if n not in st.session_state["probable_primes"]:
                                st.session_state["probable_primes"].append(n)
                        else:
                            st.error(f"{n} → Composite ({t1-t0:.6f}s)")

    # show quick RSA button only when primes available
    if len(st.session_state["probable_primes"]) >= 2:
        st.divider()
        st.write("You have primes stored in memory.")
        if st.button("Proceed to RSA Simulation (use generated primes)", key="goto_rsa"):
            go_to("RSA Simulation")

# ----------------------------
# PAGE 2: AKS vs Miller–Rabin
# ----------------------------
elif st.session_state["current_page"] == "AKS vs Miller–Rabin Comparison":
    st.title("⚖️ AKS vs Miller–Rabin Algorithm Comparison")
    num_s = st.text_input("Number to compare", key="comp_num")
    repeats = st.slider("Repetitions", 1, 10, 3, key="comp_reps")
    if st.button("Compare", key="btn_do_compare"):
        if not num_s.isdigit():
            st.error("Enter digits only.")
        else:
            n = int(num_s)
            with st.spinner("Comparing..."):
                total_mr = total_aks = 0.0
                for _ in range(repeats):
                    t_mr, t_aks = compare_algorithms(n)
                    if t_mr is None or t_aks is None:
                        st.error("Comparison not available for this number.")
                        break
                    total_mr += t_mr; total_aks += t_aks
                else:
                    avg_mr = total_mr / repeats; avg_aks = total_aks / repeats
                    st.success("Comparison done")
                    fig, ax = plt.subplots(figsize=(6,4))
                    bars = ax.bar(["Miller–Rabin", "AKS"], [avg_mr, avg_aks], color=["#4fc3f7","#ff7043"])
                    ax.set_ylabel("Time (s)")
                    ax.set_title(f"Average runtimes for n={n}")
                    for bar,val in zip(bars,[avg_mr,avg_aks]):
                        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height(), f"{val:.6f}s", ha="center", va="bottom")
                    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
                    st.pyplot(fig)

# -------------------------
# PAGE 3: RSA Simulation
# -------------------------
elif st.session_state["current_page"] == "RSA Simulation":
    st.title("🔐 RSA Simulation")
    st.write("Select two primes from memory or auto-select them.")

    primes = st.session_state["probable_primes"]
    # fallback to small_primes if probable_primes empty
    if len(primes) < 2 and st.session_state["small_primes"]:
        primes = st.session_state["small_primes"][:200]  # show a manageable slice

    if len(primes) < 2:
        st.warning("Not enough primes in memory. Go to 'Large Prime Generation' and generate primes.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            p = st.selectbox("Select p", primes, key="rsa_p")
        with col2:
            q = st.selectbox("Select q", [x for x in primes if x != p], key="rsa_q")

        if st.button("Generate RSA keys (from selected primes)", key="btn_rsa_from_selected"):
            try:
                rsa = RSA(int(p), int(q))
                st.session_state["rsa"] = rsa
                st.success("RSA keys created!")
                st.write(f"Public (e,n): ({rsa.e}, {rsa.n})")
                st.write(f"Private (d,n): ({rsa.d}, {rsa.n})")
            except Exception as e:
                st.error(f"Error generating RSA: {e}")

        if st.button("Auto-select two primes and create RSA", key="btn_rsa_auto"):
            # secure choice
            if len(primes) >= 2:
                p_auto = secrets.choice(primes)
                q_auto = secrets.choice(primes)
                while q_auto == p_auto:
                    q_auto = secrets.choice(primes)
                try:
                    rsa = RSA(int(p_auto), int(q_auto))
                    st.session_state["rsa"] = rsa
                    st.success(f"Auto-created RSA (p={p_auto}, q={q_auto})")
                    st.write(f"Public (e,n): ({rsa.e}, {rsa.n})")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Encrypt / Decrypt UI
    if st.session_state.get("rsa"):
        rsa_obj = st.session_state["rsa"]
        st.divider()
        st.subheader("Encrypt / Decrypt")
        plain = st.text_input("Plaintext (alphanumeric):", key="rsa_plain")
        if st.button("Encrypt message", key="btn_encrypt_msg"):
            try:
                cipher_text = rsa_obj.encrypt(plain)
                st.session_state["cipher"] = cipher_text
                st.success("Encrypted (stored in session).")
                st.text_area("Ciphertext:", cipher_text, height=120)
            except Exception as e:
                st.error(f"Encrypt error: {e}")

        cipher_in = st.text_area("Ciphertext to decrypt (or leave default stored):", value=st.session_state.get("cipher",""), height=120, key="rsa_cipher_in")
        if st.button("Decrypt message", key="btn_decrypt_msg"):
            try:
                dec = rsa_obj.decrypt(cipher_in)
                st.success(f"Decrypted: {dec}")
            except Exception as e:
                st.error(f"Decrypt error: {e}")
