from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer

def summarize_examples(model, text, tokenizer):
    queries = [
        "nudity",
        "implications or appearances of sexual content"
    ]

    def chunk_by_tokens(text, max_tokens=480):
        tokens = tokenizer(text, add_special_tokens=False)["input_ids"]

        for i in range(0, len(tokens), max_tokens):
            chunk = tokens[i:i + max_tokens]
            yield tokenizer.decode(chunk)

    chunks = list(chunk_by_tokens(text))
    sent_emb = model.encode(chunks, convert_to_tensor=True)
    query_emb = model.encode(queries, convert_to_tensor=True)

    scores = util.cos_sim(query_emb, sent_emb)

    results = []

    for qi, q in enumerate(queries):
        for i, s in enumerate(scores[qi]):
            if s > 0.3:
                results.append(chunks[i])

    if results:
        results_sent = [" ".join(results)]
    else:
        results_sent = ["No significant content found."]

    return results_sent


from transformers import pipeline

pipe = pipeline("text-generation", model="HuggingFaceTB/SmolLM2-1.7B-Instruct")

def classify(text, pipe):

    messages = [{
        "role": "user",
        "content": (
            f"Does this text describe mature content? Light or minimal content should be classified as NO.\n\n"
            f"{text[0]}\n\n"
            f"Answer YES or NO:"
        )
    }]

    prompt = pipe.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    
    outputs = pipe(
        prompt,
        max_new_tokens=10,
        do_sample=False,
    )
    
    result = outputs[0]["generated_text"][len(prompt):].strip().upper()
    
    if 'YES' in result[:20]:
        return 'NO'
    elif 'NO' in result[:20]:
        return 'YES'
    else:
        return 'MAYBE'
    

def final_pass(text, pipe):
    if not text or text[0].strip() == "No significant content found.":
        return "No significant mature content found."

    messages = [
        {
            "role": "user",
            "content": (
            f"Text to summarize:\n{text[0]}\n\n"
            f"Instructions: Write 2-3 sentences summarizing the above. "
            f"DO NOT include any character names, character roles, specific scenes, or explicit details. "
        )
        }
    ]


    prompt = pipe.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    outputs = pipe(
        prompt,
        max_new_tokens=150,
        do_sample=False,
        repetition_penalty=1.1,
        eos_token_id=pipe.tokenizer.eos_token_id,
    )

    generated_text = outputs[0]["generated_text"]

    return generated_text[len(prompt):].strip()

