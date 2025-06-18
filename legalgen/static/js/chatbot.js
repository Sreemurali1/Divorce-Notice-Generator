// chatbot.js

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
      { key: "client_name", text: "Who is the client requesting the NDA?" },
      { key: "disclosing_party_name", text: "Who is the disclosing party?" },
      { key: "disclosing_party_representative", text: "Who represents the disclosing party?" },
      { key: "disclosing_party_title", text: "What is their title?" },
      { key: "disclosing_party_address", text: "What is the disclosing party's address?" },
      { key: "receiving_party_name", text: "Who is the receiving party?" },
      { key: "receiving_party_representative", text: "Who represents the receiving party?" },
      { key: "receiving_party_title", text: "What is their title?" },
      { key: "receiving_party_address", text: "What is the receiving party's address?" },
      { key: "effective_date", text: "What is the effective date? (DD-MM-YYYY)" },
      { key: "duration", text: "What is the NDA duration (in years)?" },
      { key: "definition_confidential_information", text: "Define the confidential information." },
      { key: "jurisdiction", text: "Enter the jurisdiction." },
      { key: "dispute_resolution_method", text: "What is the dispute resolution method?" }
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
      data.append(q.key, userResponses[q.key]);
    }
    data.append("document_type", selectedDocType);

    fetch("/generate_legal_doc_wordfile/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
      },
      body: data
    })
      .then(res => res.json())
      .then(result => {
        linkSection.innerHTML = "";
        appendMessage("Documents generated successfully:", "bot");

        if (result.document1) {
          const link1 = document.createElement("a");
          link1.href = result.document1;
          link1.textContent = "Download Document 1";
          link1.target = "_blank";
          linkSection.appendChild(link1);
        }

        if (result.document2) {
          const link2 = document.createElement("a");
          link2.href = result.document2;
          link2.textContent = "Download Document 2";
          link2.target = "_blank";
          linkSection.appendChild(link2);
        }
      })
      .catch(err => {
        console.error("Error:", err);
        appendMessage("An error occurred. Please try again later.", "bot");
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
        appendMessage("Please select a document type first.", "bot");
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
