# OLIVIA: Optimized Light Intelligent Voice Interactive Assistant 
### This is a Digital Assitant capable of handling various tasks based on voice commands.
#### B.tech project Computer Science IIT Roorkee
**Students**: Gandhi Ronnie and Jaynil Jaiswal.

**Mentored by**: Prof. Partha Pratim Roy

# <a href="https://drive.google.com/file/d/1PL7dC4ZpeSq2ZF5GM51lRNWBjl858p3l/view?usp=sharing" target="_blank">Link to Report</a>
# <a href="https://www.youtube.com/watch?v=OpqlN1_icvM" target="_blank">Youtube Video</a>

Here is the workflow UI for the idea of our digital assistant.

![Workflow_UI](https://github.com/RonnieGandhi/ENJOY-Enhanced-Neurons-Juicing-Operations-Youthfully/blob/main/workflow_ui.png)

## Module Specifications:

In the flow diagram above there are some primary modules essential for running a digital assistant and some secondary modules that are addons to the basic infra.

### Primary Modules:
**Speech-to-text** (GPU-inference): NVidia QuartzNet model with a light weight Language Model. It has low word error rate and occupies less GPU space.(Ready to integrate)

**Text-to-speech** (GPU-inference): Forward Tacotron 2 model which is a fast light weight text to speech model with least GPU space required.(Ready to integrate)

**Natural-Language-Understanding** (NLU) shell (CPU-inference): Siamese BERT model to represent each text and finding a semantic similarity between the text input and available dictionary of words for each feature and select most related feature.(Ready to integrate)

**Chatbot** (CPU-inference): DialoGPT model which is a GPT-2 chatbot trained on clean reddit data and handles generic hello hi type of conversation.(Ready to integrate)

**Question And Answering** (CPU inference): Using the basic BERT based question answering for SQUAD-2.0 task but we can upgrade to better performing models as well. Current model is also giving great results. This is very important module to take care of finding information from the paragraphs extracted from the web in Find Information feature also might be helpful in other features like messaging.(Ready to integrate)

**DeepPunctuation** (CPU inference): This model adds punctuation to the plain text. We use this to add punctuation for the text generated from chatbot or any other place(where there isn't one). Well punctuated sentence help in better text to speech conversion generating voice with proper tonality(which our text-to-speech model is capable of). (Ready to integrate)

**Feature List Data**: For each feature we contain a word cloud/dictionary to be offered for semantic similarity based searching in the NLU-shell module.

**Task Optimizer/Schedular**: It will handle the processing power needs for each of these models and load or unload them whenever not required immediately. (Currently we are constructing a baseline architecture hence not required but will become essential as the complexity of the model increases after the feature list grows)

### Secondary Modules:

**Snap/Clap activation** (CPU inference): Audioset_tagging_cnn model is used for generic sound classification into 500 categories. We can using this classifier for activation of a task at snap or clap sound or we can also use this to keep our digital assistant on standby when no one is speaking. This is a fancy feature and hence will be integrated later on. However the running demo of this feature ready.(Ready to integrate)

**AdultFilter** (CPU inference): NudeNet model is used to filter out adult images and further videos for any indecent images in the retrieved content from web. (Ready to integrate)

**Voice Authentication**: Currently we will be using password based authentication. But we are searching for a user voice embedding based authentication model that is quick. (Pending)

**TextSummarization**(CPU inference): Scibert Scivocab based allenai's model to text summarization which might be needed in some features for finding information.(Ready to integrate)

### Feature Pool

**Time**: tells time 

**Weather**: tells weather

**Schedule List/Timetable**: tells what is there on today's timetable or on an hourly basis.

**Play Music**: using spotify api

**Find Information**: Using google and bing api or by scarpping results from them

**Send Message**: adding a whatsapp wrapper api

**Send Email**: using gmail api

**Play best videos related to a query**: search youtube videos and broadcasts on mobile/computer screen in the UI.

**Handle Call and extract information or send a relevant information**: Attending call from someone mode when the user is busy so as to note down important message to be conveyed to the user later. Aslo pulling a call to pass a particular information. (This feature needs some thinking)

**Trending news**: Searches top websites to get trending news of the day. Can be used to track updates on a particular ongoing event.
