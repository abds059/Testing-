import streamlit as st
import random
import matplotlib.pyplot as plt
import time
from daa_project import sieve, is_probable_prime
from daa_1 import compare_algorithms

st.set_page_config(page_title="Prime Number Generator & Comparison", layout="wide")

st.sidebar.title("🔢 Prime Number Toolkit")
page = st.sidebar.radio("Navigate", ["Large Prime Generation", "AKS vs Miller–Rabin Comparison"])

# --- PAGE 1: Large Prime Generation (daa_project.py) ---
if page == "Large Prime Generation":
    st.title("🔹 Large Prime Generation (Miller–Rabin + Sieve)")
    st.write("Generate, test, and analyze large prime numbers using the Sieve of Eratosthenes and Miller–Rabin algorithms.")

    st.subheader("1️⃣ Generate Base Primes")
    st.write("Use the Sieve of Eratosthenes to pre-compute small primes for faster Miller–Rabin testing.")

    limit_input = st.text_input("Enter limit for sieve generation (max 5,000,000):", "100000")

    if st.button("Run Sieve"):
        if not limit_input.strip():
            st.error("⚠️ Please enter a number.")
        elif not limit_input.isdigit():
            st.error("❌ Invalid input! Only digits are allowed.")
        else:
            try:
                limit = int(limit_input)
                if limit < 1000:
                    st.error("⚠️ Limit too small! Please enter ≥ 1,000.")
                elif limit > 5_000_000:
                    st.error("⚠️ Limit too large! Please enter ≤ 5,000,000.")
                else:
                    with st.spinner("Generating primes..."):
                        start = time.perf_counter()
                        small_primes = sieve(limit)
                        elapsed = time.perf_counter() - start
                        st.success(f"✅ Generated {len(small_primes)} primes up to {limit} in {elapsed:.6f} seconds.")
                        st.session_state["small_primes"] = small_primes
            except ValueError:
                st.error("❌ Invalid input! Please enter a valid integer.")


    st.divider()
    st.subheader("2️⃣ Miller–Rabin Prime Testing")

    mode = st.radio("Choose mode:", ["Single Number", "Range", "Random Number"])

    if "small_primes" not in st.session_state:
        st.warning("⚠️ Please run the sieve first.")
    else:
        small_primes = st.session_state["small_primes"]

        # --- SINGLE NUMBER MODE ---
        if mode == "Single Number":
            user_input = st.text_input("Enter a number to test:")
            if st.button("Check Primality"):
                if not user_input.strip():
                    st.error("⚠️ Please enter a number.")
                elif not user_input.isdigit():
                    st.error("❌ Invalid input! Only digits are allowed.")
                else:
                    try:
                        n = int(user_input)
                        if n > 10**10:
                            st.error("⚠️ Number too large! Please enter ≤ 10¹⁰.")
                        elif n < 2:
                            st.error("⚠️ Please enter an integer ≥ 2.")
                        else:
                            start = time.perf_counter()
                            is_prime = is_probable_prime(n)
                            elapsed = time.perf_counter() - start
                            st.write(f"🕒 Time taken: {elapsed:.8f} sec")
                            if is_prime:
                                st.success("✅ Probably Prime!")
                            else:
                                st.error("❌ Composite Number")
                    except ValueError:
                        st.error("❌ Invalid input! Please enter an integer.")

        # --- RANGE MODE ---
        elif mode == "Range":
            start_str = st.text_input("Start of range:")
            end_str = st.text_input("End of range:")
            if st.button("Check Range"):
                if not start_str.strip() or not end_str.strip():
                    st.error("⚠️ Both fields are required.")
                elif not (start_str.isdigit() and end_str.isdigit()):
                    st.error("❌ Invalid input! Only digits allowed.")
                else:
                    try:
                        start_range = int(start_str)
                        end_range = int(end_str)
                        if start_range > end_range:
                            st.error("⚠️ Start cannot be greater than end.")
                        elif end_range - start_range > 1_000_000:
                            st.error("⚠️ Range too large! Please limit to ≤ 1 million numbers.")
                        elif end_range > 10**10:
                            st.error("⚠️ Range end too large! Please use numbers ≤ 10¹⁰.")
                        else:
                            start_time = time.perf_counter()
                            results = []
                            for num in range(start_range, end_range + 1):
                                if all(num % p != 0 for p in small_primes if p < num):
                                    if is_probable_prime(num):
                                        results.append(num)
                            elapsed = time.perf_counter() - start_time
                            st.success(f"✅ Found {len(results)} probable primes in range. Took {elapsed:.6f} sec.")
                            if results:
                                st.text_area("Probable Primes", ", ".join(map(str, results)), height=150)
                    except ValueError:
                        st.error("❌ Invalid range values!")

        # --- RANDOM NUMBER MODE ---
        elif mode == "Random Number":
            lower_str = st.text_input("Lower bound:")
            upper_str = st.text_input("Upper bound:")
            if st.button("Generate & Test"):
                if not lower_str.strip() or not upper_str.strip():
                    st.error("⚠️ Please enter both bounds.")
                elif not (lower_str.isdigit() and upper_str.isdigit()):
                    st.error("❌ Invalid input! Only digits allowed.")
                else:
                    try:
                        lower = int(lower_str)
                        upper = int(upper_str)
                        if lower >= upper:
                            st.error("⚠️ Lower bound must be smaller than upper bound.")
                        elif upper > 10**10:
                            st.error("⚠️ Upper bound too large! Use ≤ 10¹⁰.")
                        else:
                            random_num = random.randint(lower, upper)
                            start = time.perf_counter()
                            result = is_probable_prime(random_num)
                            elapsed = time.perf_counter() - start
                            st.info(f"🎲 Generated number: {random_num}")
                            st.write(f"🕒 Time taken: {elapsed:.8f} sec")
                            if result:
                                st.success("✅ Probably Prime!")
                            else:
                                st.error("❌ Composite Number")
                    except ValueError:
                        st.error("❌ Invalid bounds!")

# --- PAGE 2: AKS vs Miller–Rabin (daa_(1).py) ---
elif page == "AKS vs Miller–Rabin Comparison":
    st.title("⚖️ AKS vs Miller–Rabin Algorithm Comparison")
    st.write("Compare execution time and results between deterministic (AKS) and probabilistic (Miller–Rabin) primality tests.")

    # --- Secure input field ---
    user_input = st.text_input("Enter number to compare:")
    repeats = st.slider("Repetitions for timing accuracy", 1, 10, 3)

    if st.button("Compare Algorithms"):
        # --- Input Validation ---
        if not user_input.strip():
            st.error("⚠️ Please enter a number before running the comparison.")
        elif not user_input.isdigit():
            st.error("❌ Invalid input! Please enter digits only (no spaces or symbols).")
        else:
            try:
                n = int(user_input)
                # You can tune this bound (e.g., 10^9)
                if n > 10**10:
                    st.error("⚠️ Number too large! Please enter a number ≤ 10¹⁰.")
                elif n < 2:
                    st.error("⚠️ Please enter an integer ≥ 2.")
                else:
                    with st.spinner("Running comparison..."):
                        total_mr = total_aks = 0
                        for _ in range(repeats):
                            time_mr, time_aks = compare_algorithms(n)
                            if time_mr is None or time_aks is None:
                                st.error("⚠️ The number is not prime. Comparison skipped.")
                                break
                            total_mr += time_mr
                            total_aks += time_aks
                        else:
                            avg_mr = total_mr / repeats
                            avg_aks = total_aks / repeats
                            st.success(f"✅ Comparison completed over {repeats} runs!")
                            st.write(f"🕒 **Miller–Rabin (avg):** {avg_mr:.8f} seconds")
                            st.write(f"🕒 **AKS (avg):** {avg_aks:.8f} seconds")

                            # Display comparison chart
                            fig, ax = plt.subplots()
                            ax.bar(["Miller–Rabin", "AKS"], [avg_mr, avg_aks], color=["skyblue", "salmon"])
                            ax.set_ylabel("Execution Time (seconds)")
                            ax.set_title(f"Average Comparison for n = {n}")
                            st.pyplot(fig)
            except ValueError:
                st.error("❌ Invalid input! Please enter a valid integer.")
