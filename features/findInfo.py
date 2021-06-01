import wikipedia
from linkpreview import link_preview
from search_engines import Google,Bing,Duckduckgo,Yahoo,Startpage,Aol,Dogpile,Ask,Mojeek,Torch
from similarity.jarowinkler import JaroWinkler

jarowinkler = JaroWinkler()

def FindInfoFinalData(query):

    results = getSearchResults(query)
    results = sorted([[jarowinkler.similarity(query,x),x] for x in results], key=lambda x: x[0],reverse=True)
    
    results = [x[1] for x in results]

    wiki_name = [x.split("/")[-1] for x in results if "wikipedia" in x.lower()]

    results = [x for x in results if "wikipedia" not in x.lower()]

    temp = []

    for x in results:
        try:
            linkp = link_preview(x)

            if(linkp.title!=None and linkp.image!=None and linkp.description!=None):
                temp.append([x,linkp.title,linkp.image,linkp.description])
        except Exception as e:
            print(x+" caused link preview error")

    results = temp
    
    wiki_summary = ""

    wiki_image_list = [x[2] for x in results]

    wiki_url = ""

    if wiki_name == []:
        wiki_answers = wikipedia.search(query)
        if wiki_answers!=[]:

            final_answer = sorted([[jarowinkler.similarity(query,x),x] for x in wiki_answers], key=lambda x: x[0])[-1]

            if final_answer[0] >= 0.8:
                wiki_answer_final = final_answer.lower()
                wiki_summary = wikipedia.summary(wiki_answer_final,auto_suggest=False)
                wiki_pg = wikipedia.page(wiki_answer_final,auto_suggest=False)
                wiki_image_list = wiki_image_list + wiki_pg.images[:20]
                wiki_url = wiki_pg.url

    else:
        wiki_answer_final = wiki_name[0].replace("_"," ").lower()

        if jarowinkler.similarity(query,wiki_answer_final) >= 0.8 :
            wiki_summary = wikipedia.summary(wiki_name[0],auto_suggest=False)
            wiki_pg = wikipedia.page(wiki_name[0],auto_suggest=False)
            wiki_image_list = wiki_pg.images
            wiki_url = wiki_pg.url

    results = [str(x[0])+"#^3^#"+str(x[1])+"#^3^#"+str(x[2])+"#^3^#"+str(x[3]) for x in results]

    return [results,wiki_summary,wiki_image_list, wiki_url]

def getSearchResults(query):
    # results = [Google().search(query).links(), Bing().search(query).links(), Duckduckgo().search(query).links(), Yahoo().search(query).links(), Startpage().search(query).links(), 
    #             Aol().search(query).links(), Ask().search(query).links(), Dogpile().search(query).links()] 
    #             # Due to Dogpile, code is giving TypeError: search() missing 1 required positional argument: 'query', so keeping it at last argument
    #             # Mojeek and Torch giving 403 and timout errors

    # return set().union(*results)
    return Google().search(query).links()
