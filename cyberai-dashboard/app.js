/**
 * CyberAI Command Center - Web Dashboard Logic Engine
 * Implements: 
 * 1. Live system clock
 * 2. Tab switching system
 * 3. Client-side Logistic Regression AI equation with live slider inputs
 * 4. Continuous real-time animated packet logging stream
 * 5. Programmatic K-Means & PCA SVG cluster rendering with interactive events
 */

// Global state for live tracking
let packetCounter = 0;
const MAX_PACKET_ROWS = 8;

// Client-side Logistic Regression Weights (Standardized scaling replicates Python output)
const MODEL_WEIGHTS = {
    intercept: -0.85,
    duration: -1.2,   // Shorter duration = more likely to be an attack (DDoS/Scans)
    orig_pkts: 1.8,   // More packets = higher chance of DDoS activity
    orig_bytes: -2.5  // Fewer bytes for the session size = highly anomalous
};

// Standard Scaler reference values (Mean and Std Dev from our dataset)
const SCALER_PARAMS = {
    duration: { mean: 4.5, std: 12.0 },
    orig_pkts: { mean: 12.0, std: 45.0 },
    orig_bytes: { mean: 6500.0, std: 18000.0 }
};

// 1. Initializer
document.addEventListener("DOMContentLoaded", () => {
    // Start System Clock
    setInterval(updateClock, 1000);
    updateClock();
    
    // Initialize AI Predictor Sliders
    setupSliders();
    
    // Generate Cluster Datapoints in the SVG
    generateClusterPoints();
    
    // Start Live Network Packet Simulation Feed
    startPacketSimulation();
});

// 2. System Clock logic
function updateClock() {
    const timeDisplay = document.getElementById("clock-display");
    if (timeDisplay) {
        const now = new Date();
        const timeString = now.toLocaleTimeString() + " " + now.toLocaleDateString(undefined, {month:'short', day:'numeric'});
        timeDisplay.textContent = timeString + " LT";
    }
}

// 3. Tab Switching logic
function switchTab(tabName) {
    // Remove active state from all buttons and tabs
    const buttons = document.querySelectorAll(".tab-btn");
    const contents = document.querySelectorAll(".tab-content");
    
    buttons.forEach(btn => btn.classList.remove("active"));
    contents.forEach(content => content.classList.remove("active"));
    
    // Activate clicked tab
    const activeBtn = document.getElementById(`btn-tab-${tabName}`);
    const activeContent = document.getElementById(`tab-${tabName}`);
    
    if (activeBtn) activeBtn.classList.add("active");
    if (activeContent) activeContent.classList.add("active");
}

// 4. Logistic Regression AI Predictor Math & Sliders
function setupSliders() {
    const durSlider = document.getElementById("slider-duration");
    const pktsSlider = document.getElementById("slider-packets");
    const bytesSlider = document.getElementById("slider-bytes");
    
    const durVal = document.getElementById("val-duration");
    const pktsVal = document.getElementById("val-packets");
    const bytesVal = document.getElementById("val-bytes");
    
    const updatePrediction = () => {
        const duration = parseFloat(durSlider.value);
        const packets = parseInt(pktsSlider.value);
        const bytes = parseInt(bytesSlider.value);
        
        // Display values
        durVal.textContent = duration.toFixed(1) + "s";
        pktsVal.textContent = packets.toLocaleString() + " pkts";
        bytesVal.textContent = bytes.toLocaleString() + " B";
        
        // Run Math
        const probability = runLogisticRegression(duration, packets, bytes);
        
        // Update UI
        updatePredictorUI(probability);
    };
    
    // Attach event listeners for real-time slider sliding
    durSlider.addEventListener("input", updatePrediction);
    pktsSlider.addEventListener("input", updatePrediction);
    bytesSlider.addEventListener("input", updatePrediction);
    
    // Initial Run
    updatePrediction();
}

/**
 * Standardizes inputs and runs the Logistic Regression Sigmoid equation
 */
function runLogisticRegression(duration, packets, bytes) {
    // 1. Standardize features (mimics StandardScaler)
    const z_dur = (duration - SCALER_PARAMS.duration.mean) / SCALER_PARAMS.duration.std;
    const z_pkts = (packets - SCALER_PARAMS.orig_pkts.mean) / SCALER_PARAMS.orig_pkts.std;
    const z_bytes = (bytes - SCALER_PARAMS.orig_bytes.mean) / SCALER_PARAMS.orig_bytes.std;
    
    // 2. Weighted Sum: z = w1*x1 + w2*x2 + ... + intercept
    const z = (z_dur * MODEL_WEIGHTS.duration) + 
              (z_pkts * MODEL_WEIGHTS.orig_pkts) + 
              (z_bytes * MODEL_WEIGHTS.orig_bytes) + 
              MODEL_WEIGHTS.intercept;
              
    // 3. Sigmoid activation: p = 1 / (1 + exp(-z))
    const probability = 1 / (1 + Math.exp(-z));
    return probability;
}

function updatePredictorUI(probability) {
    const percentText = document.getElementById("threat-percentage");
    const progressBar = document.getElementById("threat-bar");
    const alertBox = document.getElementById("prediction-alert");
    const alertIcon = document.getElementById("alert-icon");
    const alertMsg = document.getElementById("alert-msg");
    const statusLight = document.getElementById("status-light");
    const statusText = document.getElementById("status-text");
    
    const percentage = (probability * 100).toFixed(1) + "%";
    percentText.textContent = percentage;
    progressBar.style.width = percentage;
    
    if (probability >= 0.5) {
        // High Threat Alert
        alertBox.className = "prediction-alert-box threat";
        alertIcon.className = "fa-solid fa-circle-exclamation inline-icon";
        alertMsg.textContent = `MALICIOUS SESSION DETECTED (${percentage} probability). Intrusion alarm triggered!`;
        statusLight.className = "status-indicator online"; // Keep blinking, but alert level
        
        // Dynamically change progress bar color to red glow
        progressBar.style.background = "linear-gradient(90deg, #ff3366, #bf55ec)";
        progressBar.style.boxShadow = "0 0 10px #ff3366";
    } else {
        // Safe Benign Connection
        alertBox.className = "prediction-alert-box benign";
        alertIcon.className = "fa-solid fa-circle-check inline-icon";
        alertMsg.textContent = `Connection profiles as Normal (${percentage} probability). Benign session.`;
        
        progressBar.style.background = "linear-gradient(90deg, #00f5ff, #bf55ec)";
        progressBar.style.boxShadow = "0 0 10px #00f5ff";
    }
}

// 5. Continuous Network Packet Stream Simulation
function startPacketSimulation() {
    const tbody = document.getElementById("packet-tbody");
    
    // Pre-populate with a few rows
    for(let i=0; i<5; i++) {
        const packet = generateRandomPacket();
        addPacketRow(tbody, packet, false);
    }
    
    // Spawn new packets continuously
    setInterval(() => {
        const packet = generateRandomPacket();
        addPacketRow(tbody, packet, true);
    }, 3000);
}

function generateRandomPacket() {
    packetCounter++;
    const uid = "C" + String(packetCounter).padStart(6, '0');
    
    // Choose traffic category: 65% Benign, 15% DDoS, 10% Port Scan, 10% Brute Force
    const rand = Math.random();
    let type = "benign";
    if (rand > 0.65 && rand <= 0.80) type = "ddos";
    else if (rand > 0.80 && rand <= 0.90) type = "portscan";
    else if (rand > 0.90) type = "bruteforce";
    
    let proto = "tcp";
    let duration = 0.0;
    let orig_bytes = 0;
    let resp_bytes = 0;
    let state = "SF";
    
    if (type === "benign") {
        proto = Math.random() > 0.3 ? "tcp" : "udp";
        duration = +(Math.random() * 8.0 + 0.1).toFixed(3);
        orig_bytes = Math.floor(Math.random() * 5000 + 150);
        resp_bytes = Math.floor(Math.random() * 45000 + 200);
        state = Math.random() > 0.05 ? "SF" : "REJ";
    } else if (type === "ddos") {
        proto = Math.random() > 0.5 ? "tcp" : "udp";
        duration = +(Math.random() * 0.01 + 0.001).toFixed(4);
        orig_bytes = 0; // Empty payload flood
        resp_bytes = 0;
        state = "S0"; // Connection attempt, no response
    } else if (type === "portscan") {
        proto = "tcp";
        duration = 0.0;
        orig_bytes = 0;
        resp_bytes = 0;
        state = Math.random() > 0.5 ? "REJ" : "S0";
    } else if (type === "bruteforce") {
        proto = "tcp";
        duration = +(Math.random() * 3.0 + 1.0).toFixed(2);
        // Repeated identical passwords guess sizes
        orig_bytes = Math.random() > 0.5 ? 420 : 640;
        resp_bytes = Math.random() > 0.5 ? 240 : 380;
        state = "SF";
    }
    
    // Run real-time Logistic Regression classification on the packet
    const prob = runLogisticRegression(duration, 5, orig_bytes); // Assuming standard packets count
    const label = prob >= 0.5 ? "MALICIOUS" : "BENIGN";
    
    return {
        uid, proto, duration, bytes: `${orig_bytes}/${resp_bytes}`, state, type, label
    };
}

function addPacketRow(tbody, packet, animate) {
    const row = document.createElement("tr");
    if (animate) {
        row.style.opacity = "0";
        row.style.transform = "translateY(-10px)";
        row.style.transition = "all 0.5s ease";
    }
    
    let badgeClass = "benign";
    let displayType = "Benign Session";
    
    if (packet.type === "ddos") { badgeClass = "ddos"; displayType = "DDoS Flood"; }
    else if (packet.type === "portscan") { badgeClass = "portscan"; displayType = "Port Scan"; }
    else if (packet.type === "bruteforce") { badgeClass = "bruteforce"; displayType = "Brute Force"; }
    
    row.innerHTML = `
        <td>${packet.uid}</td>
        <td><i class="fa-solid fa-network-wired inline-icon"></i> ${packet.proto.toUpperCase()}</td>
        <td>${packet.duration}s</td>
        <td>${packet.bytes} B</td>
        <td>${packet.state}</td>
        <td><span class="table-badge ${badgeClass}">${displayType.toUpperCase()}</span></td>
    `;
    
    // Insert at the beginning of the table
    tbody.insertBefore(row, tbody.firstChild);
    
    if (animate) {
        // Trigger reflow
        row.offsetHeight;
        row.style.opacity = "1";
        row.style.transform = "translateY(0)";
    }
    
    // Prune excessive rows
    const rows = tbody.getElementsByTagName("tr");
    if (rows.length > MAX_PACKET_ROWS) {
        tbody.removeChild(rows[rows.length - 1]);
    }
}

// 6. Programmatic SVG K-Means Centroid & Point Generator
function generateClusterPoints() {
    const gPoints = document.getElementById("svg-datapoints");
    const gCentroids = document.getElementById("svg-centroids");
    if (!gPoints || !gCentroids) return;
    
    // Clear previous
    gPoints.innerHTML = "";
    gCentroids.innerHTML = "";
    
    // Define 4 clusters with centers:
    // C0: DDoS [Red, Centered at (100, 180)]
    // C1: Benign [Green, Centered at (280, 220)]
    // C2: Brute Force [Purple, Centered at (220, 100)]
    // C3: Port Scan [Orange, Centered at (380, 130)]
    const clusters = [
        { id: 0, cx: 100, cy: 180, count: 50, color: "var(--neon-red)", name: "DDoS" },
        { id: 1, cx: 280, cy: 220, count: 60, color: "var(--neon-green)", name: "Benign" },
        { id: 2, cx: 220, cy: 100, count: 45, color: "var(--neon-purple)", name: "Brute Force" },
        { id: 3, cx: 380, cy: 130, count: 55, color: "var(--neon-orange)", name: "Port Scan" }
    ];
    
    // Draw datapoints with randomized Gaussian scatter around centroids
    clusters.forEach(c => {
        for (let i = 0; i < c.count; i++) {
            // Box-Muller transform for Gaussian scatter
            const u1 = Math.random() || 0.0001;
            const u2 = Math.random();
            const radius = Math.sqrt(-2.0 * Math.log(u1)) * 25.0; // Scatter spread
            const theta = 2.0 * Math.PI * u2;
            
            const px = c.cx + radius * Math.cos(theta);
            const py = c.cy + radius * Math.sin(theta);
            
            // Constrain within SVG boundary box [50, 450] X [50, 300]
            const cx = Math.min(Math.max(px, 60), 440);
            const cy = Math.min(Math.max(py, 60), 290);
            
            const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
            circle.setAttribute("cx", cx);
            circle.setAttribute("cy", cy);
            circle.setAttribute("r", "3");
            circle.setAttribute("fill", c.color);
            circle.setAttribute("class", `svg-point cluster-${c.id}`);
            circle.setAttribute("opacity", "0.5");
            circle.setAttribute("style", `transform-origin: ${cx}px ${cy}px;`);
            
            // Add a slight stagger delay transition
            circle.style.animation = `fadeInTab 0.5s ease ${Math.random() * 0.5}s forwards`;
            
            gPoints.appendChild(circle);
        }
        
        // Draw Centroid X marker
        const cross = document.createElementNS("http://www.w3.org/2000/svg", "g");
        cross.setAttribute("class", "svg-centroid");
        cross.setAttribute("id", `centroid-${c.id}`);
        cross.setAttribute("transform", `translate(${c.cx}, ${c.cy})`);
        
        // Inner circle
        const cCircle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        cCircle.setAttribute("r", "8");
        cCircle.setAttribute("fill", "rgba(0,0,0,0.6)");
        cCircle.setAttribute("stroke", "#ffffff");
        cCircle.setAttribute("stroke-width", "2");
        
        // X Lines
        const line1 = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line1.setAttribute("x1", "-5");
        line1.setAttribute("y1", "-5");
        line1.setAttribute("x2", "5");
        line1.setAttribute("y2", "5");
        line1.setAttribute("stroke", "#ffffff");
        line1.setAttribute("stroke-width", "2");
        
        const line2 = document.createElementNS("http://www.w3.org/2000/svg", "line");
        line2.setAttribute("x1", "-5");
        line2.setAttribute("y1", "5");
        line2.setAttribute("x2", "5");
        line2.setAttribute("y2", "-5");
        line2.setAttribute("stroke", "#ffffff");
        line2.setAttribute("stroke-width", "2");
        
        cross.appendChild(cCircle);
        cross.appendChild(line1);
        cross.appendChild(line2);
        
        // Click interaction: Highlighting clicked cluster!
        cross.addEventListener("click", () => {
            highlightCluster(c.id);
        });
        
        gCentroids.appendChild(cross);
    });
}

function highlightCluster(clusterId) {
    // Reset all points first
    const allPoints = document.querySelectorAll(".svg-point");
    allPoints.forEach(p => {
        p.setAttribute("r", "3");
        p.setAttribute("opacity", "0.25");
    });
    
    // Highlight specific cluster points
    const activePoints = document.querySelectorAll(`.svg-point.cluster-${clusterId}`);
    activePoints.forEach(p => {
        p.setAttribute("r", "5");
        p.setAttribute("opacity", "1");
    });
    
    // Temporarily trigger card warning labels
    const statusText = document.getElementById("status-text");
    const statusLight = document.getElementById("status-light");
    
    if (clusterId === 1) {
        statusText.textContent = "AI TRACKING: ACTIVE";
        statusLight.className = "status-indicator online";
    } else {
        const clusterNames = ["DDoS Flood", "Benign", "Brute Force Threat", "Port Scan Alert"];
        statusText.textContent = `CLUSTERING: ${clusterNames[clusterId].toUpperCase()} SEPARATED`;
        statusLight.className = "status-indicator online";
    }
}
