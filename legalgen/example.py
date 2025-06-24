example_notice = {
  "name": "divorce_notice_format_prompt",
  "description": "Prompt for LLM to draft a formal divorce notice with correct legal structure and formatting.",
  "prompt": [
    {
      "role": "system",
      "content": "You are a professional legal assistant."
    },
    {
      "role": "user",
      "content": "Follow this divorce notice format exactly:\n\n1. 'To' Section:\n   - Name of the Respondent\n   - Full residential address of the Respondent\n\n2. Subject:\n   - Title: “Subject: Legal Notice for Divorce” or similar\n\n3. Salutation:\n   - 'Dear [Respondent’s Name],'\n\n4. Body of the Notice (Usually 3–5 paragraphs):\n   - Paragraph 1: Introduction of the petitioner and marriage details (date, place).\n   - Paragraph 2: Issues leading to separation (cruelty, desertion, etc.)\n   - Paragraph 3: Duration of separation and lack of reconciliation\n   - Paragraph 4: Intent to file for divorce under the applicable law (e.g., Hindu Marriage Act)\n   - Paragraph 5: Call for response within a specified time frame (e.g., 15 days)\n\n4. Closing:\n   - 'This notice is issued without prejudice to my client’s legal rights and remedies.'\n\n8. Signature Block:\n   - 'Yours sincerely / Yours faithfully,'\n   - Signature\n   - Name of Advocate\n   - Designation.)"
    }
  ]
}
