document.addEventListener("DOMContentLoaded", function () {
  const chatbox = document.getElementById("chat-box");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("query");
  const docTypeSelect = document.getElementById("docType");
  const linkSection = document.getElementById("link-section");

  let selectedDocType = "";
  let questions = [];
  let currentQuestionIndex = 0;
  let userResponses = {};

  const questionSets = {
    divorce: [
      { key: "who_is_filing", text: "Who is filing the divorce notice? (Husband/Wife)" },
      { key: "husband_name", text: "What is the husband's full name?" },
      { key: "husband_address", text: "What is the husband's address?" },
      { key: "wife_name", text: "What is the wife's full name?" },
      { key: "wife_address", text: "What is the wife's address?" },
      { key: "marriage_date", text: "What is the date of marriage? (DD-MM-YYYY)" },
      { key: "marriage_place", text: "Where was the marriage held?" },
      { key: "reason", text: "Mention the grounds for divorce (e.g., abuse, dowry demand, etc.):" }
    ],
    nda: [
      { key: "disclosing_party_name", text: "Who is the disclosing party?" },
      { key: "disclosing_party_representative", text: "Who represents the disclosing party?" },
      { key: "disclosing_party_title", text: "What is the title of the disclosing party representative?" },
      { key: "disclosing_party_address", text: "What is the disclosing party's address?" },
      { key: "receiving_party_name", text: "Who is the receiving party?" },
      { key: "receiving_party_representative", text: "Who represents the receiving party?" },
      { key: "receiving_party_title", text: "What is the title of the receiving party representative?" },
      { key: "receiving_party_address", text: "What is the receiving party's address?" },
      { key: "effective_date", text: "What is the effective date? (DD-MM-YYYY)" },
      { key: "duration", text: "Enter the NDA duration in years:" },
      { key: "definition_confidential_information", text: "Provide a definition of the confidential information." },
      { key: "jurisdiction", text: "Which jurisdiction will govern the NDA?" },
      { key: "dispute_resolution_method", text: "What method will be used to resolve disputes?" },
      { key: "created_at", text: "What is the date this NDA is being created? (DD-MM-YYYY)" }
    ]
  };

  function appendMessage(message, sender = "bot") {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;
    msgDiv.innerText = message;
    chatbox.appendChild(msgDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  function askNextQuestion() {
    if (currentQuestionIndex < questions.length) {
      appendMessage(questions[currentQuestionIndex].text, "bot");
    } else {
      generateLegalNotice();
    }
  }

  function resetChat() {
    chatbox.innerHTML = "<div class='message bot'>Hi! I’m your legal assistant. Type /start to begin.</div>";
    linkSection.innerHTML = "";
    currentQuestionIndex = 0;
    userResponses = {};
  }

  function generateLegalNotice() {
    const data = new URLSearchParams();
    for (const q of questions) {
      data.append(q.key, userResponses[q.key] || "");
    }
    data.append("document_type", selectedDocType);

    // Show loading state
    appendMessage("Generating document, please wait...", "bot generating");
    linkSection.innerHTML = "<p>Loading...</p>";

    fetch("/generate_legal_doc_wordfile/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: data
    })
      .then(res => {
        linkSection.innerHTML = ""; // Clear loading state
        console.log("Server response status:", res.status); // Debug: Log status
        if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
        return res.json();
      })
      .then(result => {
        console.log("Server response data:", result); // Debug: Log response
        linkSection.innerHTML = "";
        if (result.success && (result.document1 || result.document2)) {
          appendMessage(`${selectedDocType === 'divorce' ? 'Divorce Notice' : 'NDA'} generated successfully:`, "bot");

          if (result.document1) {
            const link1 = document.createElement("a");
            link1.href = result.document1;
            link1.textContent = `Download ${selectedDocType === 'divorce' ? 'Divorce Notice' : 'NDA'} Document 1`;
            link1.classList.add("download-link");
            link1.target = "_blank";
            linkSection.appendChild(link1);
            linkSection.appendChild(document.createElement("br"));
            linkSection.appendChild(document.createTextNode(" "));
          }

          if (result.document2) {
            const link2 = document.createElement("a");
            link2.href = result.document2;
            link2.textContent = `Download ${selectedDocType === 'divorce' ? 'Divorce Notice' : 'NDA'} Document 2`;
            link2.classList.add("download-link");
            link2.target = "_blank";
            linkSection.appendChild(link2);
          }
        } else if (result.success && !(result.document1 || result.document2)) {
          appendMessage("Document generation completed, but no files were returned. Contact support if this persists.", "bot error");
        } else {
          appendMessage(result.error || "No documents were generated. Please check your inputs and try again.", "bot error");
          // Add retry button
          const retryButton = document.createElement("button");
          retryButton.textContent = "Retry";
          retryButton.classList.add("retry-button");
          retryButton.onclick = () => {
            currentQuestionIndex = 0;
            userResponses = {};
            resetChat();
            questions = questionSets[selectedDocType];
            askNextQuestion();
          };
          linkSection.appendChild(retryButton);
        }
      })
      .catch(err => {
        console.error("Fetch error:", err); // Debug: Log error
        linkSection.innerHTML = "";
        appendMessage("An error occurred while generating the document. Please try again later.", "bot error");
        // Add retry button
        const retryButton = document.createElement("button");
        retryButton.textContent = "Retry";
        retryButton.classList.add("retry-button");
        retryButton.onclick = () => {
          currentQuestionIndex = 0;
          userResponses = {};
          resetChat();
          questions = questionSets[selectedDocType];
          askNextQuestion();
        };
        linkSection.appendChild(retryButton);
      });
  }

  chatForm.addEventListener("submit", function (e) {
    e.preventDefault();
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    appendMessage(userMessage, "user");
    userInput.value = "";

    if (userMessage.toLowerCase() === "/start") {
      selectedDocType = docTypeSelect.value;
      if (!selectedDocType) {
        appendMessage("Please select a document type first.", "bot error");
        return;
      }
      resetChat();
      questions = questionSets[selectedDocType];
      setTimeout(askNextQuestion, 500);
    } else if (currentQuestionIndex < questions.length) {
      const key = questions[currentQuestionIndex].key;
      userResponses[key] = userMessage;
      currentQuestionIndex++;
      setTimeout(askNextQuestion, 500);
    }
  });

  // Initialize
  resetChat();
});