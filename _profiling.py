from dotenv import load_dotenv
from pyinstrument import Profiler

from app.api.chatbot.business import chatbot_business
from app.schema.chatbot import ChatbotRequest

load_dotenv()

profiler = Profiler()
profiler.start()
req = ChatbotRequest(user_query="je cherche un consultant data",
                     region=None,
                     city=None,
                     grade=None,
                     assigned_until=None,
                     availability_score=None,
                     )
res = chatbot_business(req)
profiler.stop()

profiler.open_in_browser()
