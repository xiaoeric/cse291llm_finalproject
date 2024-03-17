import gradio as gr
import numpy as np
from personas import personas
import pandas as pd
import matplotlib.pyplot as plt
import functools

def extract_id(string):
    tokens = string.split()
    id = tokens[0]
    text = " ".join(tokens[1:])
    return id, text

with open("P11-1076.Datasets/data/raw/questions") as f:
    questions = f.readlines()
idx_to_qid = [extract_id(q)[0] for q in questions][:72]
qid_to_idx = {q: i for i, q in enumerate(idx_to_qid)}
question_texts = [extract_id(q)[1] for q in questions][:72]

with open("P11-1076.Datasets/data/raw/answers") as f:
    answers = f.readlines()
answer_texts = [extract_id(a)[1] for a in answers][:72]

labels = [
    "Phys. Disabled",
    "Able-bodied",
    "Jewish",
    "Christian",
    "Atheist",
    "Religious",
    "Lifelong Dem.",
    "Lifelong Rep.",
    "Obama Supp.",
    "Trump Supp.",
]
colors = [
    "#cecbe7",
    "#8f78a6",
    "#e0c6c0",
    "#cbaba0",
    "#b1917e",
    "#957960",
    "#e0c2d8",
    "#cfa6c0",
    "#bb8aa4",
    "#a47187",
]

avg_diff_noinst = np.load("avg_diff_noinst.npy", allow_pickle=True)

def make_plot(q_query):
    q_idx = qid_to_idx[q_query]
    fig = plt.figure()
    heights = [diff[q_idx] / 5 for diff in avg_diff_noinst]
    plt.bar(labels, heights, color=colors, edgecolor="grey")
    plt.axhline(y=0, color='grey', linestyle='-')
    if np.any(np.array(heights) > 0.05):
        plt.axhline(y=0.05, color='r', linestyle='-')
    if np.any(np.array(heights) < -0.05):
        plt.axhline(y=-0.05, color='r', linestyle='-')
    plt.xticks(rotation=45, ha="right")
    plt.title("gpt-3.5-turbo-0125, question " + q_query)
    plt.ylabel("Percentage difference")
    return fig

def display_q(q_query):
    return question_texts[qid_to_idx[q_query]]

def display_a(q_query):
    return answer_texts[qid_to_idx[q_query]]

data_dir = "P11-1076.Datasets/data/raw/"

def display_r(q_query):
    responses_dir = data_dir + q_query
    with open(responses_dir, encoding="latin-1") as f:
        responses = f.readlines()
    responses = [extract_id(r)[1] for r in responses]
    responses = [r.replace("<br>", "\n").strip() for r in responses]
    return [[r] for r in responses]

with gr.Blocks() as demo:
    button = gr.Dropdown(choices=idx_to_qid, value="1.1", label="Question ID")
    plot = gr.Plot()
    question_text = gr.Textbox(value="What is the role of a prototype program in problem solving?", label="Question")
    answer_text = gr.Textbox(value="To simulate the behaviour of portions of the desired software product. ", label="Correct Answer")
    response_text = gr.Dataframe(value=display_r("1.1"), label="Student Answers")
    button.change(make_plot, inputs=button, outputs=[plot])
    button.change(display_q, inputs=button, outputs=[question_text])
    button.change(display_a, inputs=button, outputs=[answer_text])
    button.change(display_r, inputs=button, outputs=[response_text])
    demo.load(make_plot, inputs=[button], outputs=[plot])
    demo.load(display_q, inputs=[button], outputs=[question_text])
    demo.load(display_a, inputs=[button], outputs=[answer_text])
    demo.load(display_r, inputs=[button], outputs=[response_text])

demo.launch()