// UI: Handle File Selection Feedback
function handleFileSelect() {
    const fileInput = document.getElementById("imageInput");
    const fileNameSpan = document.getElementById("fileName");
    
    // Check total files
    const count = fileInput.files.length;

    if (count > 0) {
        if (count === 1) {
            fileNameSpan.innerText = "✅ " + fileInput.files[0].name;
        } else {
            fileNameSpan.innerText = "✅ " + count + " Prescriptions Selected";
        }
        fileNameSpan.style.color = "#10b981"; 
        fileNameSpan.style.fontWeight = "600";
    }
}

// FEATURE: Voice Dictation (Browser API)
function toggleSpeech() {
    const micBtn = document.getElementById("micBtn");
    const descInput = document.getElementById("description");

    if (!('webkitSpeechRecognition' in window)) {
        alert("Voice input is not supported in this browser. Try Chrome or Edge.");
        return;
    }

    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = function() {
        micBtn.classList.add("mic-active");
        descInput.placeholder = "Listening... Speak now.";
    };

    recognition.onend = function() {
        micBtn.classList.remove("mic-active");
        descInput.placeholder = "e.g. Patient is currently taking Amoxicillin...";
    };

    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        descInput.value += (descInput.value ? " " : "") + transcript;
    };

    recognition.start();
}

// UI: Reset the Interface
function resetForm() {
    // Inputs
    document.getElementById("imageInput").value = "";
    document.getElementById("description").value = "";
    document.getElementById("fileName").innerText = "Click to Upload Prescription Image(s)";
    document.getElementById("fileName").style.color = "";
    
    // Reset Checkboxes
    const checkboxes = document.querySelectorAll('input[name="condition"]');
    checkboxes.forEach(cb => cb.checked = false);

    // Sections
    document.getElementById("inputSection").style.display = "block";
    document.getElementById("loading").style.display = "none";
    document.getElementById("results").style.display = "none";
    
    // Content
    document.getElementById("medsList").innerHTML = "";
    document.getElementById("alertMessage").innerText = "";
    document.getElementById("altList").innerHTML = "";
}

// API: Main Logic
async function checkInteractions() {
    const fileInput = document.getElementById("imageInput");
    const descriptionInput = document.getElementById("description");
    const languageSelect = document.getElementById("languageSelect");

    const files = fileInput.files; 
    const description = descriptionInput.value.trim();

    // Collect Selected Conditions
    const conditions = [];
    document.querySelectorAll('input[name="condition"]:checked').forEach(cb => {
        conditions.push(cb.value);
    });

    // Validation
    if (files.length === 0 && !description) {
        alert("⚠️ Action Required:\nPlease upload at least one prescription image OR enter medication details.");
        return;
    }

    const inputSection = document.getElementById("inputSection");
    const loading = document.getElementById("loading");
    const results = document.getElementById("results");

    inputSection.style.display = "none";
    loading.style.display = "block";
    results.style.display = "none";

    const formData = new FormData();
    
    for (let i = 0; i < files.length; i++) {
        formData.append("image", files[i]);
    }

    if (description) formData.append("description", description);
    
    // Send Language
    formData.append("language", languageSelect.value);
    
    // Send Conditions (as comma-separated string)
    if (conditions.length > 0) {
        formData.append("conditions", conditions.join(", "));
    }

    try {
        const response = await fetch("http://localhost:5000/api/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Server error");

        const json = await response.json();

        setTimeout(() => {
            loading.style.display = "none";
            results.style.display = "block";
            renderResults(json.data);
        }, 800);

    } catch (error) {
        console.error("Analysis error:", error);
        loading.style.display = "none";
        inputSection.style.display = "block";
        alert("System Error: Unable to complete analysis. Please try again.");
    }
}

// UI: Display Data
function renderResults(data) {
    const resultCard = document.getElementById("results");
    const riskBadge = document.getElementById("riskBadge");

    riskBadge.innerText = data.risk_level;
    
    const themeColor = data.risk_hex || "#64748b"; 

    riskBadge.style.backgroundColor = themeColor;
    resultCard.style.borderLeftColor = themeColor;

    const medsList = document.getElementById("medsList");
    medsList.innerHTML = "";
    if (data.medicines_found && data.medicines_found.length > 0) {
        data.medicines_found.forEach(med => {
            const span = document.createElement("span");
            span.className = "med-tag";
            span.innerText = med;
            medsList.appendChild(span);
        });
    } else {
        medsList.innerHTML = "<span class='text-muted'>No specific medications identified</span>";
    }

    document.getElementById("alertMessage").innerText = data.alert_message;

    const altSection = document.getElementById("altSection");
    const altList = document.getElementById("altList");
    
    if (data.alternatives && data.alternatives.length > 0) {
        altSection.style.display = "block";
        altList.innerHTML = "";
        data.alternatives.forEach(alt => {
            const li = document.createElement("li");
            li.innerHTML = `<strong>Suggested:</strong> ${alt}`;
            altList.appendChild(li);
        });
    } else {
        altSection.style.display = "none";
    }
}