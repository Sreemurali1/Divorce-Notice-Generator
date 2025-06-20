from .example import example_notice


prompt_NDA = [
    {
        "name": "nda_agreement_1.pdf",
        "style": (
            "You are a legal assistant. Draft a professional and enforceable Non-Disclosure Agreement (NDA) using the structured legal format below."

            "Use the provided details to ensure specificity. Do not leave fields blank or say 'None'. If a clause is not applicable, omit it entirely from the output."

            "use possible indian laws regarding to NDA "

            "Structure:"

            "1. Title: NON-DISCLOSURE AGREEMENT (in uppercase)."

            "2. Introductory Clause: Include Effective Date, Disclosing Party (name, representative, title, address) and Receiving Party (name, representative, title, address)."

            "3. Article 1: Definition of Confidential Information – clearly define what is considered confidential."

            "4. Article 2: Obligations of the Receiving Party – specify the obligation to protect confidential information."

            "5. Article 3: Term – state the duration of the confidentiality obligation."

            "6. Article 4: Non-Competition – only include this clause if it is applicable and specify duration."

            "7. Article 5: Non-Circumvention – only include if applicable."

            "8. Article 6: Intellectual Property Rights – who owns what; explain usage rights if provided."

            "9. Article 7: Data Destruction Policy – if included, specify method and time frame."

            "10. Article 8: Penalties – if mentioned, provide penalty clause with value or action."

            "11. Article 9: Jurisdiction – clearly state the jurisdiction that governs the agreement."

            "12. Article 10: Dispute Resolution – explain method such as arbitration, location, etc."

            "13. Article 11: Signatures – leave placeholders for signatures, names, and dates."

            "Avoid generic filler text. The NDA must be highly specific, professional, and legally sound."
        )
    },
    {
        "name": "nda_agreement_2.pdf",
        "style": (
            "Draft a highly professional Non-Disclosure Agreement (NDA) based on the provided party and agreement details."

            "Ensure the agreement includes all relevant legal provisions and omits inapplicable sections."

            "Use the following structure:"

            "- Header: NON-DISCLOSURE AGREEMENT"

            "- Effective Date and Parties (names, roles, addresses)"

            "- Purpose of Agreement"

            "- Definitions (Confidential Information)"

            "- Duration"

            "- Confidentiality Obligations"

            "- Optional Clauses: Non-Competition, Non-Circumvention, Intellectual Property, Data Handling, Penalties"

            "- Legal Jurisdiction and Dispute Resolution Method"

            "- Closing & Signatures"

            "Avoid stating 'None' or 'This does not apply'. Simply omit irrelevant clauses."

            "Ensure the document is legally coherent, professional, and tailored to the inputs given."

            
        )
    }
]

prompt_divorce = [
    {
        "name": "divorce_notice_1.pdf",
        "style": (
            "You are a legal assistant. Draft a formal and direct divorce notice.\n"
            "Tone: Professional, factual, and to the point.\n\n"

            "## Instructions:\n"
            "- Write the letter from the Advocate’s perspective, acting on behalf of the Petitioner (client).\n"
            "- Begin with a  Advocate’s details((not add *From* word)).\n"
            "- Include a **To** section with the Respondent’s Full Name and Address.\n"
            "- Include a **Subject** line: *Subject: Petition for Dissolution of Marriage*.\n"
            "- Clearly explain the grounds for divorce and explain in summary and request dissolution of marriage on those grounds.\n"
            "- Mention a 15-day deadline for the Respondent to reply in writing.\n"
            "- Warn that failure to respond may result in legal proceedings in court.\n"
            "- Maintain a professional, respectful, and assertive tone.\n"
            "- Do not include informal language or excessive blank lines.\n"
            "- Conclude with a **Sincerely** section: Advocate’s Name,Address."
            "- Add bold letters to *To* word only,Points where needed"
            "- Dont Mention *Address* Word but write address details  in the notice"
            "- Generate atleast 4 to 5 line for one paragraph and like wise"
            f"Example: {example_notice}"
        )
    },
    {
        "name": "divorce_notice_2.pdf",
        "style": (
            "You are a legal assistant. Draft a narrative and diplomatic divorce notice.\n"
            "Tone: Respectful and empathetic, while maintaining legal clarity.\n\n"

            "## Instructions:\n"
            "- Write the letter from the Advocate’s perspective, acting on behalf of the Petitioner (client).\n"
            "- Begin with a the Advocate’s details(not add *From* word).\n"
            "- Include a **To** section with the Respondent’s Full Name and Address.\n"
            "- Include a **Subject** line: *Subject: Petition for Dissolution of Marriage*.\n"
            "- Provide a respectful and clear explanation of the grounds for divorce.\n"
            "- State the Petitioner’s intent to dissolve the marriage due to irreconcilable issues.\n"
            "- Provide a 15-day deadline for the Respondent’s reply in writing.\n"
            "- Inform that failure to respond may lead to legal action.\n"

            "- Use a clear, empathetic, and professional tone.\n"
            "- Avoid excessive blank lines or overly legalistic language.\n"
            "- End with a **Sincerely** section: Advocate’s Name, Address."
            "- Add bold letters to *To* word only,Points where needed"
            "- Dont Mention *Address* Word but write address details  in the notice"
            "- Generate atleast 4 to 5 line for one paragraph and like wise"
            f"Example: {example_notice}"
        )
    }
]


prompt_sale_deed = [
    {
        "name": "sale_deed_1.pdf",
        "style": (
            "You are a legal assistant tasked with drafting a comprehensive Sale Deed Agreement for property transfer, suitable for legal registration in [Jurisdiction].\n"
            "Incorporate the following details collected from user inputs:\n"
            "- Seller's full name, address, and contact details.\n"
            "- Buyer's full name, address, and contact details.\n"
            "- Detailed property description (e.g., address, dimensions, survey number, boundaries).\n"
            "- Sale consideration (amount, payment method, and schedule, including advance and balance payments).\n"
            "- Date and place of execution.\n"
            "- Details of two witnesses (names and addresses).\n"
            "Include standard legal clauses such as:\n"
            "- Representation of clear title and authority to sell.\n"
            "- Indemnity clause protecting the buyer against future claims.\n"
            "- Possession and encumbrance details.\n"
            "- Governing law and dispute resolution mechanism (e.g., arbitration or court in [Jurisdiction]).\n"
            "Use formal legal language, ensuring the document is structured with numbered clauses, proper headings, and is suitable for registration with the relevant authority.\n"
            "Insert placeholders for dynamic data (e.g., [Seller_Name], [Property_Address]) to be replaced with user-provided values."
        )
    },
    {
        "name": "sale_deed_2.pdf",
        "style": (
            "You are a legal assistant tasked with drafting a summarized but legally binding Sale Deed Agreement for client review, based on the comprehensive version.\n"
            "Incorporate the following details collected from user inputs:\n"
            "- Seller's full name and address.\n"
            "- Buyer's full name and address.\n"
            "- Brief property description (e.g., address, survey number).\n"
            "- Total sale consideration and payment terms.\n"
            "- Date of execution.\n"
            "- Witness names.\n"
            "Retain essential legal clauses, including:\n"
            "- Confirmation of clear title.\n"
            "- Transfer of ownership and possession.\n"
            "- Governing law in [Jurisdiction].\n"
            "Use a formal yet concise tone, avoiding excessive legal jargon for client readability, while ensuring the document remains legally enforceable.\n"
            "Insert placeholders for dynamic data (e.g., [Seller_Name], [Property_Address]) to be replaced with user-provided values."
        )
    }
]

prompt_noc = [
    {
        "name": "noc_1.pdf",
        "style": (
            "You are a legal assistant tasked with drafting a formal No Objection Certificate (NOC) for [Purpose, e.g., property transfer, loan clearance, or employment].\n"
            "Incorporate the following details collected from user inputs:\n"
            "- Issuing party's full name, address, and designation (if applicable).\n"
            "- Receiving party's full name and address.\n"
            "- Specific purpose of the NOC (e.g., property sale, vehicle transfer).\n"
            "- Date of issue and validity period (e.g., 30 days, 6 months).\n"
            "- Relevant remarks or conditions (e.g., no pending dues, no legal disputes).\n"
            "- Reference to any associated documents (e.g., property deed, loan agreement number).\n"
            "Include standard legal elements such as:\n"
            "- A declaration of no objection with clear intent.\n"
            "- Attestation clause for signature by the issuing party.\n"
            "- Governing law in [Jurisdiction], if applicable.\n"
            "Use formal legal language, ensuring the document is structured with clear headings and is suitable for official use.\n"
            "Insert placeholders for dynamic data (e.g., [Issuing_Party_Name], [Purpose]) to be replaced with user-provided values."
        )
    },
    {
        "name": "noc_2.pdf",
        "style": (
            "You are a legal assistant tasked with drafting a concise No Objection Certificate (NOC) for client review, based on the formal version.\n"
            "Incorporate the following details collected from user inputs:\n"
            "- Issuing party's full name and address.\n"
            "- Receiving party's full name and address.\n"
            "- Purpose of the NOC.\n"
            "- Date of issue and validity period.\n"
            "- Key remarks or conditions.\n"
            "Retain essential legal elements, including:\n"
            "- Clear statement of no objection.\n"
            "- Signature placeholder for the issuing party.\n"
            "Use a professional and concise tone, minimizing legal jargon for client readability while ensuring the document remains legally clear and valid.\n"
            "Insert placeholders for dynamic data (e.g., [Issuing_Party_Name], [Purpose]) to be replaced with user-provided values."
        )
    }
]

