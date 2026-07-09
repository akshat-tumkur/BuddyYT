document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chatForm");
    const queryInput = document.getElementById("query");
    const submitButton = document.getElementById("submitButton");
    const chatStream = document.getElementById("chatStream");
    const responseMirror = document.getElementById("response");
    const connectionStatus = document.getElementById("connectionStatus");
    const messageCount = document.getElementById("messageCount");
    const pageTitle = document.getElementById("pageTitle");
    const pageUrl = document.getElementById("pageUrl");
    const suggestionChips = document.getElementById("suggestionChips");

    const state = {
        isLoading: false,
        messages: [],
        activeUrl: "",
        sessionUrl: "",
        sessionId: null,
    };

    renderEmptyState();
    wireEvents();
    loadActiveTab();

    function wireEvents() {
        chatForm.addEventListener("submit", handleSubmit);
        queryInput.addEventListener("input", syncComposerState);
        queryInput.addEventListener("keydown", handleComposerKeydown);

        suggestionChips.addEventListener("click", (event) => {
            const chip = event.target.closest(".chip");
            if (!chip) {
                return;
            }

            queryInput.value = chip.dataset.query || "";
            queryInput.focus();
            syncComposerState();
        });
    }

    async function loadActiveTab() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            state.activeUrl = tab?.url || "";
            pageTitle.textContent = tab?.title || "Active YouTube tab";
            pageUrl.textContent = formatUrl(tab?.url);
        } catch (error) {
            pageTitle.textContent = "Unable to read active tab";
            pageUrl.textContent = "Check that the side panel has tab access.";
        }
    }

    async function handleSubmit(event) {
        event.preventDefault();

        const query = queryInput.value.trim();
        if (!query || state.isLoading) {
            return;
        }

        const activeUrl = await getActiveUrl();
        if (!activeUrl) {
            setStatus("Open a YouTube video first.", "error");
            return;
        }

        if (state.sessionUrl && state.sessionUrl !== activeUrl) {
            resetConversationForNewVideo();
        }

        state.messages.push({ role: "user", content: query });
        renderMessages();
        queryInput.value = "";
        syncComposerState();

        setLoading(true);
        setStatus("Thinking with video context...", "busy");
        appendTypingIndicator();

        try {
            const result = await askAI(query, activeUrl, state.sessionId);
            state.sessionId = result.sessionId || state.sessionId;
            state.sessionUrl = activeUrl;
            removeTypingIndicator();
            state.messages.push({ role: "assistant", content: result.answer || "No answer returned." });
            renderMessages();
            responseMirror.textContent = result.answer || "";
            setStatus("Answer ready", "ready");
        } catch (error) {
            removeTypingIndicator();
            const message = error instanceof Error ? error.message : "Failed to reach the backend.";
            state.messages.push({ role: "assistant", content: `I couldn't get a response: ${message}` });
            renderMessages();
            setStatus("Connection problem", "error");
        } finally {
            setLoading(false);
        }
    }

    async function askAI(query, url, sessionId) {
        const response = await fetch("http://localhost:8000/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                query,
                url,
                session_id: sessionId,
            }),
        });

        if (!response.ok) {
            throw new Error(`Backend returned ${response.status}`);
        }

        const data = await response.json();
        return {
            answer: data.answer,
            sessionId: data.session_id,
        };
    }

    function renderEmptyState() {
        state.messages = [
            {
                role: "assistant",
                content: "Start with a question, or use a suggestion below to generate a focused answer from the current video.",
            },
        ];
        renderMessages();
        setStatus("Ready to chat", "ready");
        syncComposerState();
    }

    function resetConversationForNewVideo() {
        state.sessionId = null;
        state.sessionUrl = "";
        responseMirror.textContent = "";
        renderEmptyState();
    }

    function renderMessages() {
        chatStream.innerHTML = "";

        state.messages.forEach((message) => {
            const bubble = document.createElement("article");
            bubble.className = `message ${message.role}`;

            const roleLabel = document.createElement("div");
            roleLabel.className = "message-role";
            roleLabel.textContent = message.role === "user" ? "You" : "BuddyYT";

            const content = document.createElement("p");
            content.className = "message-content";
            content.textContent = message.content;

            bubble.append(roleLabel, content);
            chatStream.appendChild(bubble);
        });

        messageCount.textContent = `${state.messages.length} message${state.messages.length === 1 ? "" : "s"}`;
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    function appendTypingIndicator() {
        if (document.getElementById("typingIndicator")) {
            return;
        }

        const indicator = document.createElement("article");
        indicator.className = "message assistant typing";
        indicator.id = "typingIndicator";

        const roleLabel = document.createElement("div");
        roleLabel.className = "message-role";
        roleLabel.textContent = "BuddyYT";

        const dots = document.createElement("div");
        dots.className = "typing-dots";
        dots.innerHTML = "<span></span><span></span><span></span>";

        indicator.append(roleLabel, dots);
        chatStream.appendChild(indicator);
        chatStream.scrollTop = chatStream.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById("typingIndicator");
        if (indicator) {
            indicator.remove();
        }
    }

    function setLoading(isLoading) {
        state.isLoading = isLoading;
        submitButton.disabled = isLoading;
        queryInput.disabled = isLoading;
        suggestionChips.classList.toggle("is-disabled", isLoading);
        submitButton.textContent = isLoading ? "Sending..." : "Send";
    }

    function syncComposerState() {
        submitButton.disabled = state.isLoading || !queryInput.value.trim();
    }

    function handleComposerKeydown(event) {
        if (event.key !== "Enter" || event.shiftKey) {
            return;
        }

        event.preventDefault();
        chatForm.requestSubmit();
    }

    function setStatus(text, tone) {
        connectionStatus.textContent = text;
        connectionStatus.dataset.tone = tone;
    }

    async function getActiveUrl() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        state.activeUrl = tab?.url || "";
        pageTitle.textContent = tab?.title || "Active YouTube tab";
        pageUrl.textContent = formatUrl(tab?.url);
        return state.activeUrl;
    }

    function formatUrl(url) {
        if (!url) {
            return "No tab detected";
        }

        try {
            const parsedUrl = new URL(url);
            return parsedUrl.hostname + parsedUrl.pathname.replace(/\/$/, "");
        } catch {
            return url;
        }
    }
});