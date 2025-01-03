from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import JsonOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Initialize the LLM
llm_resto = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=os.getenv('GOOGLE_API_KEY'))

# Define the prompt template
prompt_template_resto = PromptTemplate(
    input_variables=['age', 'gender', 'weight', 'height', 'veg_or_nonveg', 'disease', 'region', 'allergics', 'foodtype'],
    template=(
        "Diet Recommendation System:\n"
        "I want you to recommend 5 restaurants names, 5 breakfast names, 5 dinner names, and 5 workout names, "
        "based on the following criteria:\n"
        "Person age: {age}\n"
        "Person gender: {gender}\n"
        "Person weight: {weight}\n"
        "Person height: {height}\n"
        "Person veg_or_nonveg: {veg_or_nonveg}\n"
        "Person generic disease: {disease}\n"
        "Person region: {region}\n"
        "Person allergics: {allergics}\n"
        "Person foodtype: {foodtype}."
        """Respond strictly only in the given json schema everytime : {{"restaurant_names":[list of string containing restaurents],"breakfast_names":[List of string containing breakfast],"dinner_names":[list of string containing dinner names],"workout_names":[list of string containing workout names]}}"""
    )
)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/recommend", response_class=HTMLResponse)
async def recommend(
    request: Request,
    age: str = Form(...),
    gender: str = Form(...),
    weight: str = Form(...),
    height: str = Form(...),
    veg_or_nonveg: str = Form(...),
    disease: str = Form(...),
    region: str = Form(...),
    allergics: str = Form(...),
    foodtype: str = Form(...),
):
    # Initialize the chain

    chain_resto = (
        RunnableParallel({
            'age': RunnablePassthrough(),
            'gender': RunnablePassthrough(),
            'weight': RunnablePassthrough(),
            'height': RunnablePassthrough(),
            'veg_or_nonveg': RunnablePassthrough(),
            'disease': RunnablePassthrough(),
            'region': RunnablePassthrough(),
            'allergics': RunnablePassthrough(),
            'foodtype': RunnablePassthrough()
        })
        | prompt_template_resto
        | llm_resto
        | JsonOutputParser()
    )

    # Prepare input data
    input_data = {
        'age': age,
        'gender': gender,
        'weight': weight,
        'height': height,
        'veg_or_nonveg': veg_or_nonveg,
        'disease': disease,
        'region': region,
        'allergics': allergics,
        'foodtype': foodtype
    }

    # Execute the chain
    results = chain_resto.invoke(input_data)
    # Extract and clean recommendations
    restaurant_names = results.get('restaurant_names', [])
    breakfast_names = results.get('breakfast_names', [])
    dinner_names = results.get('dinner_names', [])
    workout_names = results.get('workout_names', [])

    return templates.TemplateResponse(
        "RESULT.html",
        {
            "request": request,
            "restaurant_names": restaurant_names,
            "breakfast_names": breakfast_names,
            "dinner_names": dinner_names,
            "workout_names": workout_names
        }
    )
