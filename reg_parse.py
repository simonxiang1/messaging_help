import streamlit as st
import cohere
import re

my_file = open("parsed_messages.txt","r")
lines = my_file.readlines()

with open("conversation.txt", "w") as o:
    for line in lines:
        print(line)
        output = re.findall("\>[a-zA-Z0-9_ \n]+\<", line)
        output = [word.lstrip(">").rstrip("<") for word in output]
        o.write(": ".join(output)+"\n\n")

my_file.close()

col1,col2 = st.columns(2)

with col1:
    st.header("The motivation")
    st.write("Currently we have one of our team member's chat logs stored in our database. Clearly he needs some help with his messaging skills. So we decided to implement a web app that extracts messages from raw HTML, and helps the user decide what to say next.")

with col2:
    st.image("data/IMG_2.png")


st.header("The process")
st.write("We got the messages in raw text form by parsing the raw HTML from Facebook messenger, and using a clever regex to strip away all the div tags. Here is an example of the text output:")

st.text("A: ye anyways\nB: yeahhh but im the type of person that feels bad\nwhenever i dont tell someone something and im like ahhhhhhh\nA: Mmm\nA: No")


st.write("We took this file of conversations and fed them into co:here, an NLP model, to see if AI can help decide what our team member should say next. Our script feeds co:here the following input:")

st.text("Andrew Shang: I STREAMED\nA: TO A REAL PERSON\nA: RANDOM\nA: WHAT THE HELL\nA: I STREAMED FOR 40 MIN\nA: BRO\nA: AAAAAAAAAAAA\nA: IT FELT SO GOOD BUT SO HARD AND NERVOUS\nA: ok lowkey it was scary")

co = cohere.Client('ge5r64R9wLPQIkftrlgz8zBiGFW0RqkmrCVuoyJY')
response = co.generate(
        prompt='Andrew Shang: I STREAMED\nA: TO A REAL PERSON\nA: RANDOM\nA: WHAT THE HELL\nA: I STREAMED FOR 40 MIN\nA: BRO\nA: AAAAAAAAAAAA\nA: IT FELT SO GOOD BUT SO HARD AND NERVOUS\nA: ok lowkey it was scary\n'
)

st.write("And gives the following output:")
st.text('{}'.format(response.generations[0].text))


st.header("Demo: Try it yourself!")
#st.write("As of now we don't have an option for you to upload your own HTML files (although if you did we could parse it for you on our local machines, but for now you can test on a text snippet.")

