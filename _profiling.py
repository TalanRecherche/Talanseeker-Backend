from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from pyinstrument import Profiler  # noqa: E402

from app.api.chatbot.business import chatbot_business  # noqa: E402
from app.schema.chatbot import ChatbotRequest  # noqa: E402

profiler = Profiler()
profiler.start()
req = ChatbotRequest(
    user_query="je veux un consultant qui puisse faire du java et du SQL",
    region=None,
    city=None,
    grade=None,
    assigned_until=None,
    availability_score=None,
    )
res = chatbot_business(req)
profiler.stop()

profiler.open_in_browser()
