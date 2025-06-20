document.addEventListener("DOMContentLoaded", function () {
  const chatbox = document.getElementById("chat-box");
  const chatForm = document.getElementById("chat-form");
  const userInput = document.getElementById("query");
  const docTypeSelect = document.getElementById("docType");
  const linkSection = document.getElementById("link-section");
  const uploadInput = document.getElementById("draft-upload");

  let docDraftSessionId = null;
  let draftStarted = false;
  let draftUploadedFile = null;
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
      { key: "non_competition", text: "Include a non-competition clause? (Yes/No)" },
      { key: "non_competition_duration", text: "If yes, specify non-competition duration in years:" },
      { key: "non_circumvention", text: "Include a non-circumvention clause? (Yes/No)" },
      { key: "intellectual_property_rights", text: "Specify any intellectual property rights details:" },
      { key: "data_destruction_policy", text: "What is the data destruction policy?" },
      { key: "penalties", text: "Specify any penalties for breach:" },
      { key: "jurisdiction", text: "Which jurisdiction will govern the NDA?" },
      { key: "dispute_resolution_method", text: "What method will be used to resolve disputes?" },
      { key: "created_at", text: "What is the date this NDA is being created? (DD-MM-YYYY)" }
    ],
    sale_deed: [
      { key: "client_name", text: "What is the client's full name?" },
      { key: "seller_name", text: "What is the seller's full name?" },
      { key: "seller_address", text: "What is the seller's address?" },
      { key: "buyer_name", text: "What is the buyer's full name?" },
      { key: "buyer_address", text: "What is the buyer's address?" },
      { key: "property_address", text: "What is the property's address?" },
      { key: "property_type", text: "What is the type of property (e.g., residential, commercial)?" },
      { key: "property_description", text: "Provide a detailed description of the property:" },
      { key: "sale_amount", text: "What is the sale amount (in ₹)?" },
      { key: "payment_mode", text: "What is the payment mode (e.g., bank transfer, cheque)?" },
      { key: "date_of_agreement", text: "What is the date of the agreement? (DD-MM-YYYY)" },
      { key: "date_of_registration", text: "What is the date of registration? (DD-MM-YYYY)" },
      { key: "witness_1", text: "Who is the first witness?" },
      { key: "witness_2", text: "Who is the second witness?" }
    ],
    noc: [
      { key: "client_name", text: "What is the client's full name?" },
      { key: "noc_type", text: "What is the type of NOC (e.g., property transfer, vehicle)?" },
      { key: "party_issuing", text: "Who is issuing the NOC?" },
      { key: "party_receiving", text: "Who is receiving the NOC?" },
      { key: "purpose", text: "What is the purpose of the NOC?" },
      { key: "date_issued", text: "What is the issue date? (DD-MM-YYYY)" },
      { key: "valid_until", text: "What is the validity date? (DD-MM-YYYY)" },
      { key: "remarks", text: "Any additional remarks for the NOC?" }
    ],
    doc_draft: []
  };

  function appendMessage(message, sender = "bot") {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;
    msgDiv.textContent = message;
    chatbox.appendChild(msgDiv);
    chatbox.scrollTop = chatbox.scrollHeight;
  }

  function getCsrfToken() {
    const tokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    return tokenElement ? tokenElement.value : "";
  }

  function resetChat() {
    chatbox.innerHTML = "<div class='message bot'>Hi! I’m your legal assistant. Type /start to begin.</div>";
    linkSection.innerHTML = "";
    currentQuestionIndex = 0;
    userResponses = {};
    draftStarted = false;
    docDraftSessionId = null;
    uploadInput.value = "";
  }

  function askNextQuestion() {
    if (currentQuestionIndex < questions.length) {
      appendMessage(questions[currentQuestionIndex].text, "bot");
    } else {
      generateLegalNotice();
    }
  }

  async function handleDocDraft(userMessage) {
    console.log("handleDocDraft called. File:", draftUploadedFile);

    if (!draftUploadedFile) {
      appendMessage("Please upload a PDF before starting doc draft Q&A.", "bot error");
      return;
    }

    if (!draftUploadedFile.name.toLowerCase().endsWith(".pdf")) {
      appendMessage("Invalid file type. Please upload a valid PDF.", "bot error");
      draftUploadedFile = null;
      uploadInput.value = "";
      return;
    }

    if (!draftStarted) {
      const formData = new FormData();
      formData.append("files", draftUploadedFile);

      appendMessage("Uploading PDF, please wait...", "bot uploading");

      try {
        const response = await fetch("/upload/", {
          method: "POST",
          body: formData
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.status}`);
        }

        const data = await response.json();
        console.log("Upload response:", data);

        const responseData = data[0];

        if (responseData.error) {
          appendMessage(responseData.error, "bot error");
          return;
        }

        docDraftSessionId = responseData.session_id;
        draftStarted = true;

        appendMessage(responseData.current_question, "bot");
      } catch (err) {
        console.error("Error uploading file:", err);
        appendMessage("File upload failed. Try again later.", "bot error");
      }
      return;
    }

    try {
      const response = await fetch("/answer/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          session_id: docDraftSessionId,
          answer: userMessage
        })
      });

      const data = await response.json();

      if (data.generate) {
        const finalRes = await fetch("/generate_filled_text/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCsrfToken(),
            "Content-Type": "application/x-www-form-urlencoded"
          },
          body: new URLSearchParams({
            session_id: docDraftSessionId
          })
        });

        const finalData = await finalRes.json();

        if (finalData.document_url) {
          appendMessage("✅ Document ready.", "bot");
          linkSection.innerHTML = `<a href="${finalData.document_url}" target="_blank">📄 Download PDF</a>`;
        } else {
          appendMessage("Document generation failed.", "bot error");
        }
      } else {
        appendMessage(data.current_question, "bot");
      }
    } catch (err) {
      console.error("Doc draft error:", err);
      appendMessage("Something went wrong. Try again.", "bot error");
    }
  }

  async function generateLegalNotice() {
    const data = new URLSearchParams();
    for (const q of questions) {
      data.append(q.key, userResponses[q.key] || "");
    }
    data.append("document_type", selectedDocType);

    appendMessage("Generating document, please wait...", "bot");

    try {
      const response = await fetch("/generate_legal_doc_wordfile/", {
        method: "POST",
        headers: {
          "X-CSRFToken": getCsrfToken(),
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: data
      });

      const result = await response.json();

      if (result.status === "success") {
        appendMessage("✅ Document generated successfully.", "bot");
        if (result.document1) {
          linkSection.innerHTML += `<a href="${result.document1}" target="_blank">Download Document 1</a><br>`;
        }
        if (result.document2) {
          linkSection.innerHTML += `<a href="${result.document2}" target="_blank">Download Document 2</a>`;
        }
      } else {
        appendMessage("Failed to generate document.", "bot error");
      }
    } catch (err) {
      console.error("Error generating document:", err);
      appendMessage("Server error while generating document.", "bot error");
    }
  }

  uploadInput.addEventListener("change", () => {
    if (uploadInput.files.length > 0) {
      draftUploadedFile = uploadInput.files[0];
      console.log("File uploaded:", draftUploadedFile.name);
      appendMessage("✅ Draft uploaded. Type /start to begin Q&A.", "bot");
    } else {
      draftUploadedFile = null;
      appendMessage("No file selected.", "bot error");
    }
  });

  chatForm.addEventListener("submit", async function (e) {
    e.preventDefault();
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    appendMessage(userMessage, "user");
    userInput.value = "";

    if (userMessage.toLowerCase() === "/start") {
      selectedDocType = docTypeSelect.value;
      if (!selectedDocType) {
        appendMessage("Please select a document type.", "bot error");
        return;
      }

      resetChat();
      questions = questionSets[selectedDocType] || [];

      if (selectedDocType === "doc_draft") {
        if (!draftUploadedFile) {
          appendMessage("Please upload a PDF before starting doc draft Q&A.", "bot error");
          return;
        }
        await handleDocDraft(userMessage);
      } else {
        setTimeout(askNextQuestion, 500);
      }
    } else if (selectedDocType === "doc_draft") {
      await handleDocDraft(userMessage);
    } else if (currentQuestionIndex < questions.length) {
      const key = questions[currentQuestionIndex].key;
      userResponses[key] = userMessage;
      currentQuestionIndex++;
      setTimeout(askNextQuestion, 500);
    } else {
      appendMessage("No more questions. Type /start to begin again.", "bot");
    }
  });

  // Initialize chat UI
  resetChat();
});

