"""
📖 How It Works - Comprehensive documentation page
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from dashboard.theme import inject_theme, inject_sidebar_brand, COLORS
from dashboard.components import page_header, init_shared_state

st.set_page_config(page_title="How It Works", page_icon="📖", layout="wide")
inject_theme()
inject_sidebar_brand()
init_shared_state()

page_header("📖", "How It Works", "Comprehensive system documentation")

tabs = st.tabs([
    "What Is NAD",
    "CICIDS2017 Dataset",
    "ML Models",
    "Feature Engineering",
    "System Architecture",
    "Attack Types",
    "Glossary",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: What Is Network Anomaly Detection
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("## What Is Network Anomaly Detection?")
    st.markdown(f"""
    **Network Anomaly Detection (NAD)** is the process of identifying unusual patterns in
    network traffic that deviate from established baselines. These deviations often indicate
    security threats such as intrusions, data exfiltration, or denial-of-service attacks.

    ### Why It Matters
    - **Volume**: Modern networks generate millions of flows per hour -- far too many for manual review.
    - **Speed**: Attacks can escalate in seconds. Automated detection enables real-time response.
    - **Sophistication**: Attackers constantly evolve tactics. ML-based detection can identify
      previously unseen (zero-day) attack patterns that rule-based systems miss.

    ### IDS vs IPS
    | Feature | IDS (Intrusion Detection) | IPS (Intrusion Prevention) |
    |---------|---------------------------|----------------------------|
    | Action | Monitors and **alerts** | Monitors and **blocks** |
    | Placement | Passive (mirror port) | Inline (all traffic flows through) |
    | Latency | None | May add latency |
    | Risk | Alerts may be ignored | False positives block legitimate traffic |

    This system is an **IDS** -- it detects and reports anomalies. Prevention (blocking) would
    require integration with a firewall or network gateway.

    ### Detection Approaches
    - **Signature-based**: Matches traffic against known attack patterns (like antivirus rules).
      Fast and accurate for known threats, but blind to novel attacks.
    - **Anomaly-based**: Learns what "normal" looks like and flags deviations. Can detect
      zero-day attacks but may produce false positives. **This system uses anomaly-based
      detection powered by machine learning.**
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: The CICIDS2017 Dataset
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("## The CICIDS2017 Dataset")
    st.markdown(f"""
    The **Canadian Institute for Cybersecurity Intrusion Detection System 2017** (CICIDS2017)
    dataset was created by the University of New Brunswick. It is one of the most widely used
    benchmark datasets for network intrusion detection research.

    ### Key Facts
    - **Created**: July 3-7, 2017 (5-day capture)
    - **Total flows**: ~2.8 million
    - **Features**: 80+ network flow features extracted with CICFlowMeter
    - **Protocols**: HTTP, HTTPS, FTP, SSH, and email protocols

    ### Day-by-Day Breakdown

    | Day | Date | Activity |
    |-----|------|----------|
    | Monday | July 3 | **Benign traffic only** -- establishes normal baseline |
    | Tuesday | July 4 | **FTP-Patator**, **SSH-Patator** (brute-force attacks) |
    | Wednesday | July 5 | **DoS Slowloris**, **DoS Slowhttptest**, **DoS Hulk**, **DoS GoldenEye**, **Heartbleed** |
    | Thursday | July 6 | **Web attacks** (Brute Force, XSS, SQL Injection), **Infiltration** |
    | Friday | July 7 | **Botnet (ARES)**, **Port Scan**, **DDoS (LOIT)** |

    ### Classes in Our Model
    After preprocessing and class balancing, our model classifies flows into **7 classes**:

    1. **BENIGN** -- Normal, legitimate network traffic
    2. **Bot** -- Botnet command-and-control communication
    3. **DDoS** -- Distributed Denial of Service
    4. **DoS Hulk** -- DoS attack using the Hulk tool
    5. **FTP-Patator** -- FTP brute-force login attempts
    6. **PortScan** -- Network reconnaissance via port scanning
    7. **SSH-Patator** -- SSH brute-force login attempts
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: Machine Learning Models
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("## Machine Learning Models")

    st.markdown("### LightGBM (Primary Model)")
    st.markdown(f"""
    **LightGBM** (Light Gradient Boosting Machine) is our primary classifier,
    achieving **98.2% accuracy** on the CICIDS2017 test set.

    **How it works:**
    - Uses **leaf-wise tree growth** (vs. level-wise in XGBoost), which tends to
      converge faster and achieve higher accuracy.
    - Employs **histogram-based splitting** for efficient handling of continuous features.
    - Supports **categorical features** natively.

    **Why chosen for this project:**
    - Extremely fast training and inference (<15ms per batch)
    - Low memory footprint -- ideal for real-time dashboards
    - Built-in handling of class imbalance
    - State-of-the-art accuracy on tabular data

    **Key hyperparameters** (from config.yaml):
    - Algorithm: Gradient Boosting Decision Tree
    - Trained on 78 numeric features after StandardScaler normalization
    """)

    st.markdown("---")
    st.markdown("### Random Forest")
    st.markdown(f"""
    **Random Forest** is an ensemble of decision trees trained on random subsets of the data.

    **How it works:**
    - Trains **100 independent decision trees** (n_estimators=100)
    - Each tree sees a random sample (bootstrap) of the training data
    - Final prediction is the **majority vote** across all trees
    - max_depth=20, min_samples_split=5

    **Pros:** Robust to overfitting, interpretable feature importance, no need for scaling.
    **Cons:** Slower inference than LightGBM, less accurate on this dataset.
    """)

    st.markdown("---")
    st.markdown("### XGBoost")
    st.markdown(f"""
    **XGBoost** (Extreme Gradient Boosting) is a regularized gradient boosting framework.

    **How it works:**
    - Builds trees **sequentially**, where each new tree corrects errors from previous ones
    - Uses **L1 and L2 regularization** to prevent overfitting
    - n_estimators=200, max_depth=8, learning_rate=0.1

    **Pros:** Strong regularization, handles missing values, GPU support.
    **Cons:** Level-wise growth can be less efficient than LightGBM's leaf-wise approach.
    """)

    st.markdown("---")
    st.markdown("### LSTM Autoencoder")
    st.markdown(f"""
    **LSTM Autoencoder** is an unsupervised deep learning model for anomaly detection.

    **How it works:**
    - **Encoder**: LSTM layers compress the 78-dimensional input into a 32-dimensional latent space
    - **Decoder**: LSTM layers reconstruct the original input from the compressed representation
    - Trained **only on benign traffic** to learn "normal" patterns
    - At inference, high **reconstruction error** indicates an anomaly

    **Architecture** (from config.yaml):
    - Input dimension: 78
    - Hidden dimension: 64
    - Latent dimension: 32
    - Number of layers: 2
    - Dropout: 0.2

    **Pros:** Can detect **zero-day attacks** (unseen attack types).
    **Cons:** Higher false positive rate, requires careful threshold tuning.
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4: Feature Engineering
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("## Feature Engineering")

    st.markdown("""
    ### What Are Network Flow Features?
    A **network flow** is a sequence of packets between two endpoints (IP:port pairs)
    using the same protocol. Instead of analyzing individual packets, we aggregate
    them into flows and extract statistical features:

    - **Packet counts**: Forward packets, backward packets, total packets
    - **Byte counts**: Forward bytes, backward bytes, total bytes
    - **Timing**: Flow duration, inter-arrival times (IAT), active/idle times
    - **TCP flags**: SYN, ACK, FIN, RST, PSH counts
    - **Statistical**: Mean, std, min, max of packet sizes and IATs

    ### From Raw Packets to Feature Vectors
    """)

    st.markdown(f"""
    ```
    Raw Packets          Flow Aggregation         Feature Vector (78-dim)
    ┌──────────┐        ┌─────────────────┐      ┌──────────────────────┐
    │ PKT 1    │───┐    │ Group by:       │      │ Flow Duration        │
    │ PKT 2    │───┤    │  src_ip:dst_ip  │      │ Total Fwd Packets    │
    │ PKT 3    │───┼───>│  src_port:dport │─────>│ Total Bwd Packets    │
    │ ...      │───┤    │  protocol       │      │ Fwd Packet Len Mean  │
    │ PKT N    │───┘    │                 │      │ Flow Bytes/s         │
    └──────────┘        └─────────────────┘      │ ... (78 features)    │
                                                  └──────────────────────┘
    ```
    """)

    st.markdown("""
    ### StandardScaler Normalization
    Before feeding features to the ML model, we apply **StandardScaler**:

    `X_scaled = (X - mean) / std`

    This ensures all features have zero mean and unit variance, preventing
    features with large magnitudes (e.g., bytes/s) from dominating features
    with small magnitudes (e.g., flag counts).

    ### SMOTE for Class Imbalance
    The CICIDS2017 dataset is heavily imbalanced (>80% benign traffic). We use
    **SMOTE** (Synthetic Minority Over-sampling Technique) to balance the classes:

    - SMOTE generates **synthetic** samples for minority classes
    - It works by interpolating between existing minority samples and their nearest neighbors
    - This prevents the model from simply predicting "BENIGN" for everything
    """)

    # Feature importance image
    fi_path = Path(__file__).parent.parent.parent / 'models' / 'feature_importance.png'
    if fi_path.exists():
        st.markdown("### Feature Importance (LightGBM)")
        st.image(str(fi_path), use_container_width=True)
    else:
        st.info("Feature importance visualization not found at `models/feature_importance.png`.")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5: System Architecture
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("## System Architecture")
    st.markdown("### End-to-End Pipeline")

    box_style = "border-radius:4px; padding:0.75rem 1.25rem; text-align:center; min-width:140px;"

    st.markdown(f"""
    <div style="background:{COLORS['bg_tertiary']}; border:1px solid rgba(245,158,11,0.12);
         border-top:2px solid {COLORS['primary']}; border-radius:4px; padding:2rem; margin:1rem 0;">
        <div style="display:flex; align-items:center; justify-content:center; gap:0.5rem; flex-wrap:wrap;">
            <div style="background:{COLORS['primary']}15; border:1px solid {COLORS['primary']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">📡</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">Data Source</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">Live / PCAP / Sim</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['secondary']}15; border:1px solid {COLORS['secondary']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">🔄</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">Feature Extraction</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">78 CIC Features</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['success']}15; border:1px solid {COLORS['success']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">📏</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">StandardScaler</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">Normalize</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['primary']}15; border:1px solid {COLORS['primary']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">🧠</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">LightGBM</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">Predict + Proba</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['danger']}15; border:1px solid {COLORS['danger']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">🎯</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">Classification</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">7 Classes</div>
            </div>
            <div style="color:{COLORS['primary']}; font-size:1.5rem;">→</div>
            <div style="background:{COLORS['primary']}15; border:1px solid {COLORS['primary']}30;
                 {box_style}">
                <div style="font-size:1.5rem;">📋</div>
                <div style="font-weight:700; font-size:0.9rem; font-family:'Space Grotesk',sans-serif;">Verdict</div>
                <div style="color:{COLORS['text_muted']}; font-size:0.75rem;">Alert / Benign</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### Data Sources
    | Source | Description | Use Case |
    |--------|-------------|----------|
    | **Live Network Capture** | Scapy-based packet sniffing on a real interface | Demo with attack sender script |
    | **Simulation** | Synthetic traffic generator with attack injection | Testing without network access |
    | **Pre-recorded** | CSV datasets from `data/samples/` | Reproducible analysis |
    | **PCAP Upload** | User-uploaded .pcap/.pcapng files | Forensic analysis of captures |

    ### Confidence Threshold & Severity
    The model outputs a **confidence score** (0.0 - 1.0) for each prediction.

    - Flows below the **confidence threshold** (configurable in Settings) are treated as benign
    - Severity levels based on confidence: **Medium** (<90%), **High** (90-95%), **Critical** (>95%)
    """)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6: Attack Types Explained
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("## Attack Types Explained")
    st.markdown("The model detects the following 6 attack categories:")

    attacks = [
        {
            'name': 'DDoS (Distributed Denial of Service)',
            'icon': '🌊',
            'description': """
A DDoS attack overwhelms a target server with a flood of traffic from multiple sources,
making it unavailable to legitimate users. In CICIDS2017, the LOIT tool was used.

**How it works:** Thousands of SYN packets per second from spoofed source IPs flood the target,
exhausting connection table resources.

**Key features the model uses:** Extremely high `Flow Packets/s`, high `Flow Bytes/s`,
many `SYN` flags, very short `Flow Duration`, low `Bwd Packets` (mostly one-directional).

**Mitigation:** Rate limiting, SYN cookies, traffic scrubbing services, blackhole routing.
            """,
        },
        {
            'name': 'DoS Hulk',
            'icon': '💥',
            'description': """
DoS Hulk generates unique, obfuscated HTTP GET requests to bypass caching and overwhelm
web servers. Unlike simple floods, each request looks different.

**How it works:** Rapid HTTP requests with randomized URL parameters to prevent caching.
Each request forces the server to process a full response.

**Key features:** High `Fwd Packet Length`, moderate `Flow Duration`, consistent
`Fwd Packets` count, high `Flow Bytes/s`.

**Mitigation:** Web Application Firewall (WAF), request rate limiting per IP, CAPTCHA challenges.
            """,
        },
        {
            'name': 'PortScan',
            'icon': '🔍',
            'description': """
Port scanning is a reconnaissance technique to discover open services on a target host.
Attackers probe many ports to find vulnerable services.

**How it works:** Sends SYN packets to sequential or random ports. An open port responds
with SYN-ACK; a closed port responds with RST.

**Key features:** Many unique `Dst Ports`, very small `Fwd Packet Length` (just SYN packets),
short `Flow Duration`, high `Flow Packets/s`, few `Bwd Packets`.

**Mitigation:** Firewall rules to limit port exposure, IDS alerting, port knocking.
            """,
        },
        {
            'name': 'FTP-Patator (FTP Brute Force)',
            'icon': '🔓',
            'description': """
FTP-Patator uses the Patator tool to perform brute-force login attempts against FTP servers
(port 21), trying many username/password combinations.

**How it works:** Repeated TCP connections to port 21 with different credentials.
Each attempt creates a short flow with authentication data.

**Key features:** `Dst Port` = 21, moderate `Fwd Bytes` (credential data), many short flows
from the same source, consistent `Flow Duration`.

**Mitigation:** Account lockout policies, fail2ban, strong passwords, disable anonymous FTP.
            """,
        },
        {
            'name': 'SSH-Patator (SSH Brute Force)',
            'icon': '🔑',
            'description': """
SSH-Patator uses the Patator tool to brute-force SSH login credentials on port 22.
Similar to FTP-Patator but targets the SSH protocol.

**How it works:** Repeated SSH connection attempts with different credentials.
SSH handshake creates distinctive flow patterns.

**Key features:** `Dst Port` = 22, higher `Fwd Bytes` than FTP (SSH handshake is larger),
many flows from a single source IP, consistent timing patterns.

**Mitigation:** Key-based authentication only, fail2ban, non-standard SSH port, MFA.
            """,
        },
        {
            'name': 'Bot (Botnet)',
            'icon': '🤖',
            'description': """
Botnet traffic represents communication between infected machines and their
Command-and-Control (C2) server. The ARES botnet was used in CICIDS2017.

**How it works:** Infected hosts periodically beacon to the C2 server, receive commands,
and exfiltrate data. Traffic patterns are regular and persistent.

**Key features:** Regular `Flow Duration`, consistent `IAT` (inter-arrival times),
moderate `Bytes/s`, bidirectional communication (both `Fwd` and `Bwd` packets present).

**Mitigation:** Network segmentation, DNS sinkholing, endpoint detection and response (EDR).
            """,
        },
    ]

    for attack in attacks:
        with st.expander(f"{attack['icon']}  {attack['name']}", expanded=False):
            st.markdown(attack['description'])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 7: Glossary
# ═══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("## Glossary")

    terms = [
        ("Network Flow", "A sequence of packets between two endpoints (src_ip:src_port ↔ dst_ip:dst_port) using the same protocol."),
        ("PCAP", "Packet Capture -- a file format for storing captured network packets. Created by tools like Wireshark and tcpdump."),
        ("IDS / IPS", "Intrusion Detection System (monitors and alerts) / Intrusion Prevention System (monitors and blocks)."),
        ("CICIDS2017", "Canadian Institute for Cybersecurity Intrusion Detection System 2017 -- the benchmark dataset used to train our models."),
        ("Gradient Boosting", "An ensemble ML technique that builds models sequentially, where each new model corrects errors from previous ones."),
        ("LightGBM", "Light Gradient Boosting Machine -- a fast, leaf-wise gradient boosting framework by Microsoft."),
        ("Random Forest", "An ensemble of decision trees trained on random subsets of data, with predictions made by majority vote."),
        ("XGBoost", "Extreme Gradient Boosting -- a regularized gradient boosting framework with L1/L2 penalties."),
        ("Autoencoder", "A neural network trained to compress and reconstruct its input. High reconstruction error indicates anomalies."),
        ("LSTM", "Long Short-Term Memory -- a type of recurrent neural network that can learn long-term dependencies in sequential data."),
        ("SMOTE", "Synthetic Minority Over-sampling Technique -- generates synthetic samples for underrepresented classes to balance datasets."),
        ("StandardScaler", "Normalizes features to have zero mean and unit variance: X_scaled = (X - mean) / std."),
        ("Feature Importance", "A score indicating how much each feature contributes to the model's predictions."),
        ("F1 Score", "The harmonic mean of Precision and Recall. Balances false positives and false negatives."),
        ("Precision", "Of all instances predicted as positive, what fraction are actually positive? TP / (TP + FP)."),
        ("Recall", "Of all actual positive instances, what fraction did the model detect? TP / (TP + FN). Also called Sensitivity."),
        ("False Positive", "A benign flow incorrectly classified as an attack. Causes unnecessary alerts."),
        ("False Negative", "An attack flow incorrectly classified as benign. The most dangerous type of error."),
        ("Confidence Score", "The probability assigned by the model to its predicted class. Range: 0.0 (uncertain) to 1.0 (certain)."),
        ("Confidence Threshold", "The minimum confidence required to flag a flow as an attack. Configurable in Settings."),
        ("Severity Level", "Assigned based on confidence: Medium (<90%), High (90-95%), Critical (>95%)."),
        ("TCP Flags", "Control bits in TCP headers: SYN (connection start), ACK (acknowledgment), FIN (connection end), RST (reset), PSH (push data)."),
        ("IAT", "Inter-Arrival Time -- the time between consecutive packets in a flow. Important feature for detecting automated attacks."),
        ("Scapy", "A Python library for packet manipulation, capture, and crafting. Used for both live capture and the attack sender script."),
        ("DDoS", "Distributed Denial of Service -- flooding a target with traffic from many sources to make it unavailable."),
        ("Brute Force", "An attack that tries many password combinations until the correct one is found. Targets SSH (port 22) or FTP (port 21)."),
        ("Port Scan", "Reconnaissance technique that probes many ports on a target to discover running services."),
        ("Botnet", "A network of compromised machines controlled by an attacker via a Command-and-Control (C2) server."),
        ("C2 (Command and Control)", "A server that sends commands to compromised machines in a botnet."),
    ]

    for term, definition in terms:
        st.markdown(f"**{term}** -- {definition}")

st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding-top:1.5rem; border-top:1px solid {COLORS['border']};">
    <p style="color:{COLORS['text_muted']}; font-size:0.85rem;">Network Anomaly Analyzer v2.0</p>
</div>
""", unsafe_allow_html=True)
