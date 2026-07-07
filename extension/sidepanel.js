let currentTab;
document.addEventListener("DOMContentLoaded", async () => {

    const [tab] = await chrome.tabs.query({
        active: true,
        currentWindow: true
    });

    currentTab = tab;

});

document.getElementById("submitButton").addEventListener("click", async () => {

    const query = document.getElementById("query").value
    const answer = await askAI(query)
    document.getElementById("response").textContent = answer

})

async function askAI(query) {

    const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            query: query,
            url: currentTab.url
        })
    });

    const data = await response.json();
    return data.answer;
}