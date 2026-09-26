from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights


# result = tavily_search("Best Hotels in India")
# print(result)

res = search_flights("Plan a 7 days Japan trip from Bangladesh")
print(res)