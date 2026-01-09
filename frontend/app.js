async function checkInteractions() {
    const fileInput = document.getElementById('imageInput');
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select an image first.");
        return;
    }

    // Show loading, hide results
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';

    const formData = new FormData();
    formData.append('image', file);

    try {
        const response = await fetch('http://localhost:5000/api/analyze', {
            method: 'POST',
            body: formData
        });

        const json = await response.json();

        document.getElementById('loading').style.display = 'none';
        document.getElementById('results').style.display = 'block';

        renderResults(json.data);

    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred during analysis.");
        document.getElementById('loading').style.display = 'none';
    }
}

function renderResults(data) {
    // Medicines
    const medicineList = document.getElementById('medicineList');
    medicineList.innerHTML = "";

    data.medicines_found.forEach(med => {
        const li = document.createElement("li");
        li.textContent = med;
        medicineList.appendChild(li);
    });

    // Risk Banner
    const banner = document.getElementById('riskBanner');
    banner.className = `risk-banner risk-${data.risk_color}`;
    banner.textContent = `Risk Level: ${data.risk_level}`;

    // Explanation
    document.getElementById('alertMessage').textContent = data.alert_message;

    // Alternatives
    const alternativesSection = document.getElementById('alternativesSection');
    const alternativesList = document.getElementById('alternativesList');
    alternativesList.innerHTML = "";

    if (data.alternatives && data.alternatives.length > 0) {
        alternativesSection.style.display = 'block';

        data.alternatives.forEach(alt => {
            const li = document.createElement("li");
            li.textContent = alt;
            alternativesList.appendChild(li);
        });
    } else {
        alternativesSection.style.display = 'none';
    }
}
