from sentence_transformers import SentenceTransformer, util
import nltk

# nltk.download("punkt")
# nltk.download("punkt_tab")
# from nltk.tokenize import sent_tokenize
import re
import torch


model = SentenceTransformer("all-MiniLM-L6-v2")

with torch.no_grad():
    model.encode(["warmup"])

def summarize_examples(model, text):
    queries = [
        "nudity",
        "explicit sexual content"
    ]

    sentences = re.split(r'(?<=[.!?])\s+', text)

    sent_emb = model.encode(sentences, convert_to_tensor=True) 
    query_emb = model.encode(queries, convert_to_tensor=True)

    scores = util.cos_sim(query_emb, sent_emb)

    results = {}
    for qi, q in enumerate(queries):
        relevant_sentences = [
            sentences[i]
            for i, s in enumerate(scores[qi])
            if s > 0.3
        ]

    if relevant_sentences:
        results_sent = [" ".join(relevant_sentences)]
    else:
        results_sent = ["No significant content found."]

    return results_sent


from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base", legacy=True)
model2 = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

def final_pass(model2, text):
    input_text = "Rewrite this into 2-3 proper sentences. Avoid specific scenes, character names, and explicit body-part detail." + text[0]
    input_ids = tokenizer(input_text, return_tensors="pt").input_ids

    outputs = model2.generate(input_ids)
    return (tokenizer.decode(outputs[0]))


# print("summarized text", summarize_examples(model, '''Parents need to know that Everything Everywhere All at Once is a trippy sci-fi/fantasy martial arts adventure from the directors of the dark comedy Swiss Army Man. It centers on a middle-aged laundromat owner named Evelyn (Michelle Yeoh), who discovers she must help save the multiverse during a routine trip to file her business taxes. Expect occasional strong language (mostly several uses of "f--k" and "s--t"), as well as plenty of violence, including stylized martial arts sequences that use both real and improvised weapons and include close-range brawling. There are a few deaths and a couple of bloody scenes. People kiss, there are super-quick shots of the main character making love (the focus is on her face or back), and you\'ll see fighting sex toys (both as weapons and skill amplifiers). Diverse representation includes a non-stereotypical Chinese American family and two women over 50 in central roles, as well as two women in a loving and supportive relationship. Families will have plenty to discuss after watching the movie, which is best suited for older teens and adults. In addition to martial arts-inspired fight sequences between Evelyn and the forces from the other verses, several characters from the multiverse die and battle with weapons (usually found objects, from a fanny pack to a trophy, but also real weapons). Some violence is comic, some bloody and realistic. In a scene where all versions of Evelyn are quickly shown, a couple are making love, showing her face and naked shoulders (these are blink-and-miss moments). Evelyn and her husband (or different versions of him) kiss in a few scenes. Phallic sex toys are used in a fight scene. Suggestive joke about a sex toy (a "butt plug") that\'s used as a prize for IRS auditors; later, two different men use it to invoke their special skills. In one case, the man who uses it is naked from the waist down. His crotch area is obscured, but audiences can see his butt during the fight scenes. Brief scenes show characters smoking cigarettes and marijuana and drinking.'''))

# print("summarized text", summarize_examples(model, '''Parents need to know that Little Women is an adaptation of the book by Louisa May Alcott. In an intense moment, beloved sister Beth becomes dangerously ill, recovers, but eventually dies young in a very sad sequence. The youngest sister, Amy, falls through the ice while skating but is pulled to safety. Kids will learn a bit about the time period during and just after the Civil War and will get to know an amazing group of role models in the March family. They are supportive of one another and wonderful members of the community, even giving away their Christmas dinner to those less fortunate. Beth becomes dangerously ill with scarlet fever, recovers, but eventually dies. Amy falls through the ice while skating but is pulled to safety. Amy comes home with a welt on her hand telling her family that she was struck by her teacher. Mr. March comes home from the war injured and the family fears for his safety constantly. A few kisses and mentions of romantic overtures. Some drinking at parties. Jo says she only takes alcohol medicinally. Laurie drinks from a hip flask in one scene.'''))

# print("summarized text", summarize_examples(model, '''Parents need to know that Oppenheimer is director Christopher Nolan\'s drama about J. Robert Oppenheimer (Cillian Murphy), the scientist responsible for the creation of the atomic bomb. But it\'s less an entertaining history lesson than it is a dense examination of the unholy matrimony of quantum physics and military bureaucracy, and things can get pretty confusing thanks to frequent undated time jumps and a barrage of names and characters to keep straight. The sex scenes (Nolan\'s first) include frequent partial nudity (particularly co-star Florence Pugh\'s breasts). Characters smoke, as would be expected in the 1930s–\'50s setting, and drink. A bomb trial demonstrates the enormousness of the weapon\'s capabilities, with fire, noise, and smoke. But viewers are told about, rather than shown, the horror that unfolded after the bomb was ultimately dropped on Hiroshima and Nagasaki. There are references to mass assassination and to suicide, and a brief hallucination of a young woman\'s skin appearing to blow off. Language includes a few uses of "f--k," plus "goddamn," "s--t," and more. Death by suicide. Massive fiery, loud bomb explosion, accompanied by a loud "doom" score that underlines the future impact of the detonation. Discussion of the impact of the atomic bomb on the people of Hiroshima and Nagasaki. In a hallucination, the skin on a woman\'s face appears to blow off. Attempted murder through the eyes of the protagonist. Several sex scenes with partial nudity, including long sequences with bare breasts. Recurring infidelity. Frequent drinking, including by a character who's portrayed as having an alcohol dependency. Smoking cigarettes and a pipe.'''))

summ = summarize_examples(model, '''Parents need to know that Oppenheimer is director Christopher Nolan\'s drama about J. Robert Oppenheimer (Cillian Murphy), the scientist responsible for the creation of the atomic bomb. But it\'s less an entertaining history lesson than it is a dense examination of the unholy matrimony of quantum physics and military bureaucracy, and things can get pretty confusing thanks to frequent undated time jumps and a barrage of names and characters to keep straight. The sex scenes (Nolan\'s first) include frequent partial nudity (particularly co-star Florence Pugh\'s breasts). Characters smoke, as would be expected in the 1930s–\'50s setting, and drink. A bomb trial demonstrates the enormousness of the weapon\'s capabilities, with fire, noise, and smoke. But viewers are told about, rather than shown, the horror that unfolded after the bomb was ultimately dropped on Hiroshima and Nagasaki. There are references to mass assassination and to suicide, and a brief hallucination of a young woman\'s skin appearing to blow off. Language includes a few uses of "f--k," plus "goddamn," "s--t," and more. Death by suicide. Massive fiery, loud bomb explosion, accompanied by a loud "doom" score that underlines the future impact of the detonation. Discussion of the impact of the atomic bomb on the people of Hiroshima and Nagasaki. In a hallucination, the skin on a woman\'s face appears to blow off. Attempted murder through the eyes of the protagonist. Several sex scenes with partial nudity, including long sequences with bare breasts. Recurring infidelity. Frequent drinking, including by a character who's portrayed as having an alcohol dependency. Smoking cigarettes and a pipe.''')
print("final", final_pass(model2, summ))