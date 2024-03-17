from openai import OpenAI
from prompts import prompts
from personas import personas
import json
from ratelimit import limits, RateLimitException
from backoff import on_exception, expo
import time
client = OpenAI(api_key="")

data_dir = "P11-1076.Datasets/data/raw/"
questions_dir = data_dir + "questions"
answers_dir = data_dir + "answers"

with open(questions_dir) as f:
    questions = f.readlines()

with open(answers_dir) as f:
    answers = f.readlines()

def extract_id(string):
    tokens = string.split()
    id = tokens[0]
    text = " ".join(tokens[1:])
    return id, text

out_file = open("p1_1_instruct.jsonl", "a")

@on_exception(expo, RateLimitException)
@limits(calls=1, period=1)
def call_api(model, messages):
    return client.chat.completions.create(
                model=model,
                messages=messages,
                seed=0,
                max_tokens=4,
            ).choices[0].message.content

@on_exception(expo, RateLimitException)
@limits(calls=450, period=60)
def call_completions(model, prompt):
    return client.completions.create(
                model=model,
                prompt=prompt,
                seed=0,
                max_tokens=4,
            ).choices[0].text

for i, q in enumerate(questions):
    q_id, question = extract_id(q)

    # temp fix to continue last session
    # if float(q_id) < 11.6:
    #     continue
    
    _, correct_ans = extract_id(answers[i])
    prompt_id = "2.1"
    sys_prompt_temp = prompts[prompt_id]

    responses_dir = data_dir + q_id
    with open(responses_dir, encoding="latin-1") as f:
        responses = f.readlines()
    start_q = time.time()
    for j, r in enumerate(responses):
        # temp fix to continue last session
        # if float(q_id) <= 11.61 and j <= 17:
        #     continue

        _, response = extract_id(r)
        response = response.replace("<br>", "\n").strip()

        start_r = time.time()
        call_times = []

        for persona_id, persona in personas.items():
            # sys_prompt = sys_prompt_temp.format(question=question, correct_ans=correct_ans, persona=persona)
            prompt = sys_prompt_temp.format(question=question, correct_ans=correct_ans, persona=persona, answer=response)
        
            model = "gpt-3.5-turbo-instruct"
            # messages = [
            #     {"role": "system", "content": sys_prompt},
            #     {"role": "user", "content": response},
            # ]
            start_call = time.time()
            # completion = call_api(model, messages)
            completion = call_completions(model, prompt)
            call_time = time.time() - start_call
            call_times.append(round(call_time, 2))

            output = {
                "q_id": q_id,
                "r_idx": j,
                "prompt_id": prompt_id,
                "persona_id": persona_id,
                "completion": completion,
            }
            out_file.write(json.dumps(output) + "\n")
        print("completed r" + str(j), round(time.time() - start_r, 2), call_times)
        out_file.flush()
    print("completed q" + q_id, round(time.time() - start_q, 2))

out_file.close()
