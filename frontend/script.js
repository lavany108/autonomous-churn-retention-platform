document.getElementById("churnForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    const data = {
        gender: formData.get("gender"),
        SeniorCitizen: 0,
        Partner: "Yes",
        Dependents: "No",
        tenure: parseInt(formData.get("tenure")),
        PhoneService: "Yes",
        MultipleLines: "No",
        InternetService: "DSL",
        OnlineSecurity: "No",
        OnlineBackup: "Yes",
        DeviceProtection: "No",
        TechSupport: "No",
        StreamingTV: "Yes",
        StreamingMovies: "No",
        Contract: formData.get("Contract"),
        PaperlessBilling: "Yes",
        PaymentMethod: "Credit card (automatic)",
        MonthlyCharges: parseFloat(formData.get("MonthlyCharges")),
        TotalCharges: parseFloat(formData.get("TotalCharges"))
    };

    const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    const riskBadge = document.getElementById("riskTierBadge");
    const probabilityBar = document.getElementById("probabilityBar");
    const probabilityText = document.getElementById("probabilityText");

    const riskTier = result.risk_tier;
    const probability = result.churn_probability * 100;

    // Set badge text
    riskBadge.innerText = riskTier;

    // Reset classes
    riskBadge.className = "badge";

    // Safe class formatting
    if (riskTier) {
        const tierClass = riskTier.toLowerCase().replace(/\s+/g, "-");
        riskBadge.classList.add(tierClass);
    }

    probabilityBar.className = "progress-bar";

    if (riskTier === "Very Low" || riskTier === "Low") {
        probabilityBar.style.background = "#2ecc71";
    }
    else if (riskTier === "Medium") {
        probabilityBar.style.background = "#f39c12";
    }
    else {
        probabilityBar.style.background = "#e74c3c";
    }

    // Animate probability bar
    probabilityBar.style.width = probability + "%";
    probabilityText.innerText = probability.toFixed(2) + "%";

    document.getElementById("actionBox").innerText =
        result.recommended_action;

    document.getElementById("result").classList.remove("hidden");
});