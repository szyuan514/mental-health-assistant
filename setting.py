from openai import OpenAI
from risk import detect_risk, CRISIS_RESPONSE

API_KEY = "sk-30adfeead85647148d24a16e37f399c0"

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.deepseek.com"
)

messages =[{"role": "system", "content": "一名温和的心理健康陪伴助手"}]


while True:
    user_input = input(" ")
    if user_input.lower() == "quit":
        print("👋 再见，保重！")
        break
    
    risk_level = detect_risk(user_input, client)
    
    if risk_level == 'high':
        messages.append({"role": "user", "content": user_input})
        print(f"AI:{CRISIS_RESPONSE}")
        messages.append({"role": "assistant", "content": CRISIS_RESPONSE})
        
    elif risk_level == 'medium':
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        ai_reply = response.choices[0].message.content
        medium_reminder = "\n\n---\n如果心里太难受，可以拨打 12356 心理援助热线，那里有专业人士可以倾听你。"
        final_reply = ai_reply + medium_reminder
        
        print(f"{final_reply}")
        messages.append({"role": "assistant", "content": final_reply})
        
    else:
        messages.append({"role": "user", "content": user_input})
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        ai_reply = response.choices[0].message.content
        
        print(f"{ai_reply}")
        messages.append({"role": "assistant", "content": ai_reply})