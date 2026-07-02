from .llm_client import call_llm

def generate_newsletter_digest(newsletters):
    """
    Takes a list of newsletter email dicts.
    Returns a list of digest entries, each shaped as:
    {
      "source": str,
      "time": str,
      "points": list[str]
    }
    Using an extractive-then-abstractive LLM pipeline.
    """
    digest_entries = []
    
    if not newsletters:
        return []
        
    print(f"[Digest Generator] Generating digest for {len(newsletters)} newsletters...")
    
    for email in newsletters:
        source_name = email.get("from_name", "Unknown Source")
        subject = email.get("subject", "No Subject")
        body = email.get("body", "")
        
        if not body.strip():
            continue
            
        # Limit body length to prevent huge context size in 8GB RAM / API limitations
        truncated_body = body[:8000]
        
        # Step 1: Extractive Phase
        # Instruct LLM to extract 4-6 most important sentences verbatim.
        extractive_system_instruction = (
            "You are an assistant that extracts the most informative sentences verbatim from a newsletter email body.\n"
            "Select 4 to 6 key sentences that represent the core announcements, news, or messages. "
            "You MUST extract the sentences exactly as they appear in the original text. "
            "Output the extracted sentences as a plain text list separated by newlines. Do not add numbers, markdown, or commentary."
        )
        
        extractive_prompt = (
            f"Newsletter Subject: {subject}\n"
            f"Newsletter Sender: {source_name}\n\n"
            f"Body:\n{truncated_body}"
        )
        
        try:
            print(f"  Running Step 1 (Extractive) for {source_name}...")
            extracted_sentences = call_llm(
                extractive_prompt, 
                system_instruction=extractive_system_instruction, 
                json_mode=False
            )
            
            # Step 2: Abstractive Phase
            # Instruct LLM to turn those extracted sentences into 2-4 short bullet points.
            abstractive_system_instruction = (
                "You are an expert editor who summarizes raw extracted sentences from a newsletter.\n"
                "Review the provided sentences and summarize them into 2 to 4 short, punchy, and clear bullet points.\n"
                "Ensure the language is concise, professional, and captures the absolute essence of the news.\n"
                "Output ONLY the bullet points, one per line, without bullet symbols (like '-', '*', or '•'). Do not add any greeting or closing."
            )
            
            abstractive_prompt = (
                f"Extracted Sentences from {source_name}:\n"
                f"{extracted_sentences}"
            )
            
            print(f"  Running Step 2 (Abstractive) for {source_name}...")
            abstracted_text = call_llm(
                abstractive_prompt,
                system_instruction=abstractive_system_instruction,
                json_mode=False
            )
            
            # Parse bullet points
            points = [p.strip() for p in abstracted_text.split("\n") if p.strip()]
            
            # Strip leading characters like '-', '*', '•' or '1.' if the LLM outputted them despite instructions
            cleaned_points = []
            for pt in points:
                cleaned_pt = re_strip_list_symbols(pt)
                if cleaned_pt:
                    cleaned_points.append(cleaned_pt)
            
            if not cleaned_points:
                # Fallback to simple snippet if LLM extraction failed
                cleaned_points = [email.get("snippet", "No summary available.")]
                
            # Calculate reading time based on word count
            word_count = sum(len(pt.split()) for pt in cleaned_points)
            # Assuming average reading speed of 180 words per minute
            reading_seconds = max(15, int((word_count / 180) * 60))
            # Round to nearest 5 seconds
            reading_seconds = ((reading_seconds + 4) // 5) * 5
            time_str = f"[~{reading_seconds} sec read]"
            
            digest_entries.append({
                "source": source_name,
                "time": time_str,
                "points": cleaned_points
            })
            
        except Exception as e:
            print(f"Error generating digest for {source_name}: {e}")
            # Fallback
            digest_entries.append({
                "source": source_name,
                "time": "[~15 sec read]",
                "points": [email.get("snippet", "No summary available.")]
            })
            
    print(f"[Digest Generator] Successfully generated {len(digest_entries)} digest entries.")
    return digest_entries

def re_strip_list_symbols(text: str) -> str:
    """Removes leading list symbols, bullet marks, numbers, or spaces from LLM outputs."""
    # Matches bullet indicators like: -, *, •, 1., 2) at start of text
    cleaned = re.sub(r'^(?:[-*•\d+\.\)]\s*)+', '', text.strip())
    return cleaned.strip()
