async function checkInteractions() {
    const fileInput = document.getElementById("imageInput");
    const descriptionInput = document.getElementById("description");

    const file = fileInput.files[0];
    const description = descriptionInput.value.trim();

    if (!file && !description) {
        alert("Please upload a prescription image or enter a description.");
        return;
    }

    // UI state
    const loading = document.getElementById("loading");
    const results = document.getElementById("results");

    if (loading) loading.style.display = "block";
    if (results) results.style.display = "none";

    const formData = new FormData();

    if (file) {
        formData.append("image", file);
    }

    if (description) {
        formData.append("description", description);
    }

    try {
        const response = await fetch("http://localhost:5000/api/analyze", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const json = await response.json();

        if (loading) loading.style.display = "none";
        if (results) results.style.display = "block";

        renderResults(json.data);

    } catch (error) {
        console.error("Analysis error:", error);
        alert("Failed to analyze. Please try again.")
    }