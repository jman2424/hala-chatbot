import openai  

def get_ai_response(user_message):  
    response = openai.ChatCompletion.create(  
        model="gpt-4",  
        messages=[{"role": "system", "content": "You are a helpful AI for Tariq Halal Meat Shop, assisting customers with orders, delivery, and products."},  
                  {"role": "user", "content": user_message}],  
        temperature=0.7  
    )  
    return response['choices'][0]['message']['content']  

