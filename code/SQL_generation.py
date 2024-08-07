# -*- coding: utf-8 -*-
"""20th July - SQL generation using agents.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1I8pv8CRwXScTthppENbXqHDwpGMvBy89
"""

#!pip install langgraph==0.1.8
#!pip install httpx
#!pip install langchain
#!pip install langchain-openai
#!pip install langchain_community
#!pip install pyodbc
#!apt install libgraphviz-dev
#!pip install pygraphviz
#!pip install grandalf
#!pip install ipywidgets
#!pip install langchain_cohere

# Commented out IPython magic to ensure Python compatibility.
# %%sh
# apt-get install -y unixodbc-dev
# curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
# curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
# sudo apt-get update
# sudo ACCEPT_EULA=Y apt-get -q -y install msodbcsql17

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, List
import operator
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from langchain_openai import ChatOpenAI
from langchain import LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.pydantic_v1 import BaseModel
from langchain.memory import ConversationBufferMemory
from langchain_community.utilities import SQLDatabase
from langchain.agents import AgentExecutor
from langchain_cohere.react_multi_hop.agent import create_cohere_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import Tool
from langchain_experimental.utilities import PythonREPL

from langchain_community.utilities.sql_database import SQLDatabase
from sqlalchemy import create_engine
import pyodbc

from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field

from operator import itemgetter
from langchain.chains.openai_tools import create_extraction_chain_pydantic
from langchain_core.pydantic_v1 import BaseModel, Field
import pandas as pd
from typing import List, TypedDict, Any
import os
import json
from langgraph.checkpoint import MemorySaver
from sqlalchemy import create_engine, text
from langchain.agents import Tool
from langchain_experimental.utilities import PythonREPL

import base64
from io import BytesIO
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import uuid

memory = SqliteSaver.from_conn_string(":memory:")

os.environ['OPENAI_API_KEY'] = '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'
os.environ['LANGCHAIN_TRACING_V2'] = "true"
os.environ['LANGCHAIN_API_KEY'] = "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"

os.environ['COHERE_API_KEY'] = "t2m56Pw0bdOaFDAl4DTKLJFLw69mkpbilg6Nz2Oh"

# Create the Cohere chat model
from langchain_cohere.chat_models import ChatCohere


# Initialize the model
model = ChatOpenAI(model="gpt-4o", temperature=0)

# Initialize the memory
memory = ConversationBufferMemory()

conn_str = (
    r'DRIVER={ODBC Driver 17 for SQL Server};'
    r'SERVER=sales-data1.database.windows.net;'
    r'DATABASE=salesdata;'
    r'UID=azure_server;'
    r'PWD=Mydatabase@123;'
)
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={conn_str}")
# Create the SQLDatabase instance

db = SQLDatabase(engine)

print(db.get_table_names())

schema_info = {
    "Order_data": {
        "SO_Document": "Sales Document Number",
        "Line_Item": "Line Number in the sales document which contains detail of the item sold",
        "Customer_Code": "Customer Code",
        "Purchase_Order_Date": "Date on which Purchase order was received from the customer",
        "Product_Division": "Classification of item sold as per division",
        "Product_Quality": "Classification of item sold as per Quality",
        "Testing_Req": "Does customer require third party inspection? (Yes or No)",
        "Receiving_Customer_Code": "Customer Code to whom item has been delivered",
        "SO_Date": "Creation Date of Doc",
        "Order_Volume": "Total Quantity of item sold",
        "Unit_Rate": "Rate of the item per unit",
        "Ingredient_1": "% of Nickle content in the item",
        "Ingredient_2": "% of Molybdenum content in the item",
        "Total_Amount": "Total amount of the item sold",
        "Terms_Condition": "Description of Payment Terms",
        "Shipping_Location": "Location code from where item has been shipped to the customer",
        "Sales_Area": "Company sales office which carried out this sales",
        "Sales_Person_Name": "Name of the Sales Person",
        "Order_Requirement_Date": "Date on which customer requires item",
        "Zone": "Region in which sales happened",
        "Factory": "Plant Name",
        "Product_Code": "Product Code"
    },

    "Product_master": {
        "Product_Code": "Product code",
        "Product_Category": "Classification of item/product sold as per series",
        "Product_Parameter_1": "Classification of item sold as per grade",
        "Product_Parameter_2": "Classification of item sold as per Thickness in mm",
        "Product_Parameter_3": "Classification of item sold as per Width in mm",
        "Product_Parameter_4": "Classification of item sold as per Length in mm",
        "Product_Parameter_5": "Classification of item sold as per Finish",
        "Product_Parameter_6": "Classification of item sold as per Edge Condition",
    },

    "Discount_pricing": {
        "Sales_Area": "Company sales office which carried out this sales",
        "Sales_Enquiry_Number": "Unique identifier assigned to an enquiry received by the customer for set of items",
        "Sales_Quotation_Number": "Unique identifier assigned to a sales quote against the enquiry received by the customer",
        "Sales_Person_Name": "Name of the Sales Person",
        "Quotation_Revision_Number": "Count of sales quote version provided to the customer in response to the received inquiry",
        "Quotation_Creation_Date_Time": "Creation date and time of sales quote",
        "CRM_Platform_Customer_Code": "Customer Code assigned to customer in the CRM software",
        "Customer_Code": "Unique identifier code assigned to a customer",
        "Quotation_Closure_Position": "Open or closure status of the quotation provided to the customer",
        "Quotation_Achievement_Position": "Progress status of the quotation provided to customer; if quote is won or lost",
        "Sales_Quotation_Line_Item": "Line Number in the sales quote which contains detail of the item",
        "Product_Division": "Classification of item sold as per division",
        "Quotation_Revision_Reason": "Reason for the revision of sales quotation",
        "Quotation_Volume": "Total quantity of item for which quote is provided to the customer",
        "Market_Floor_Price_per_Unit": "Base price / market price per unit for the item",
        "Price_Reduction_on_Floor_Price_per_Unit": "Discount given in the quote to the customer below market floor price per unit",
        "Additional_Cost_per_Unit": "Additional cost per unit charged for extra services or test required by the customer",
        "Final_Price_per_Unit": "Final per unit price offered to customer for the item after considering discount and extra cost",
        "Product_Code": "Unique identifier assigned to the product"
    },

    "Billing_data": {
        "Invoice_Date": "Date on which billing is done to the customer",
        "Product_Division": "Classification of item sold as per division",
        "Sales_Area": "Company sales office which carried out this sales",
        "Factory": "Plant Name",
        "Product_Quality": "Classification of item sold as per Quality",
        "Customer_Code": "Unique identifier code assigned to a customer",
        "Receiving_Customer_Code": "Customer Code to whom item has been delivered",
        "Invoice_Document": "Invoice Document Number",
        "SO_Document": "Sales Document Number",
        "Line_Item": "Line Number in the sales document which contains detail of the item sold",
        "Invoice_Volume": "Final Invoice Volume of the item",
        "SO_Planned_Date": "Date on which order has been assigned for production",
        "SO_Date": "Creation Date of Doc",
        "Order_Acknowledge_Date": "Date on which order has been mutually acknowledged by the sales team and the customer",
        "Sales_Person_Name": "Name of the Sales Person",
        "Shipping_Location": "Location code from where item has been shipped to the customer",
        "Product_Code": "Unique identifier assigned to the product"
    },

    "Customer_master": {
        "Customer_Type_1": "Customer Classification as per Market Indicator",
        "Customer_Type_2": "Customer Classification",
        "Customer_Type_3": "Type of customer based on MoU signed with company or not",
        "Customer_Type_4": "Customer Classification as per Segment",
        "Customer_Name": "Name of the Customer"
    }
}

llm = ChatOpenAI(model="gpt-4o", temperature=0)
agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

# Define the AgentState class and Table model
from typing import Any

class AgentState(TypedDict):
    task: str
    selected_tables: List[str]
    table_descriptions: List[str]
    user_query: str
    critique: str
    content: List[str]
    revision_number: int
    max_revisions: int
    initial_query: str
    final_answer: str
    generated_output: str
    is_query_correct: bool
    sql_query: str
    message_history: List[ChatMessage]
    plot_code: str
    plot_result: Any

class Table(BaseModel):
    name: str = Field(description="Name of table in SQL database.")

def get_table_details():
    table_description = pd.DataFrame(["Order_data", "Product_master"], columns=['Table'])
    table_description['Description'] = [
        "The Table contains the information about the sales across various financial year, by different sales teams, customers and other possible information related to the sales",
        "The table contains the information/details about the product - specifically its category and its parameters"
    ]

    table_details = ""
    for index, row in table_description.iterrows():
        table_details += f"Table Name: {row['Table']}\nTable Description: {row['Description']}\n\n"
    return table_details

def table_info_node(state: AgentState):
    selected_tables = state["selected_tables"]
    table_descriptions = []

    for table in selected_tables:
        if table in schema_info:
            columns_info = schema_info[table]
            description = f"Table Name: {table}\nColumns:\n"
            for column, col_description in columns_info.items():
                description += f"  - {column}: {col_description}\n"
            table_descriptions.append(description)

    state["table_descriptions"] = table_descriptions
    return state#{"table_descriptions": table_descriptions}

def select_tables_node(state: AgentState) -> AgentState:

    #if 'message_history' not in state:
    #    state['message_history'] = []
    def get_tables(tables: List[Table]) -> List[str]:
        return [table.name for table in tables]

    # Extract necessary details from the state
    user_query = state['user_query']
    table_details = get_table_details()  # Get table details from the function

    if len(state['message_history'])>0:
      history_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state['message_history']])
    else:
      history_content = ""

    # Define the prompt template
    prompt_template = """
    Given the following user query, Chat queries, their outputs and table descriptions, select the relevant tables that should be used to answer the query.

    Chat queries:
    {history_content}

    User Query: {user_query}

    Table Descriptions:
    {table_details}

    Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed.
    Only Return a dictionary with "selected_tables" as key and list of tables as value without any extra text.
    Don't return any other text or brackets.
    """
    # Format the prompt
    prompt = prompt_template.format(user_query=user_query, table_details=table_details, history_content = history_content)

    # Generate the response from the model
    response = model([HumanMessage(content=prompt)])

    # Extract the selected tables from the response
    selected_tables = []
    try:
        result = json.loads(response.content)
        selected_tables = result.get("selected_tables", [])
    except json.JSONDecodeError:
        print("Error decoding JSON response from the model")

    # Update the state with the selected tables
    state['selected_tables'] = selected_tables

    # Append the user query and the model response to the message history
    state['message_history'].append({
        'role': 'user',
        'content': user_query
    })
    state['message_history'].append({
        'role': 'system',
        'content': response.content
    })
    return state

WRITER_PROMPT = """You are a SQL assistant tasked with generating the best SQL query possible for the user's request. The SQL query will be used in Microsoft SQL Server so generate the syntax accordingly. Utilize all the information below as needed:

chat queries:
{history_content}

Table Descriptions:
{table_descriptions}

User Query:
{user_query}

Here are few examples of SQL queries and their expected output:

*User Query 1:* select all the orders of last financial year
SQL output: SELECT * from Order_data od where od.Purchase_Order_Date >= '2023-04-01' AND od.Purchase_Order_Date < '2024-04-01';

*User Query 2:* Which division's sale is growing month on month?
SQL output: WITH Monthly_Invoice_Volume AS (SELECT [Product_Division], YEAR([Invoice_Date]) AS Invoice_Year, MONTH([Invoice_Date]) AS Invoice_Month, SUM([Invoice_Volume]) AS Total_Monthly_Invoice FROM Billing_data GROUP BY [Product_Division], YEAR([Invoice_Date]), MONTH([Invoice_Date])), Slope_Calculations AS (SELECT [Product_Division], COUNT(*) AS N, SUM(Invoice_Month) AS Sum_X, SUM(Total_Monthly_Invoice) AS Sum_Y, SUM(Invoice_Month * Total_Monthly_Invoice) AS Sum_XY, SUM(Invoice_Month * Invoice_Month) AS Sum_XX, (COUNT(*) * SUM(Invoice_Month * Invoice_Month)) - (SUM(Invoice_Month) * SUM(Invoice_Month)) AS Denominator FROM Monthly_Invoice_Volume GROUP BY [Product_Division]), Slope_Values AS (SELECT [Product_Division], CASE WHEN Denominator != 0 THEN (N * Sum_XY - Sum_X * Sum_Y) / Denominator ELSE NULL END AS Slope, ROW_NUMBER() OVER (ORDER BY CASE WHEN Denominator != 0 THEN (N * Sum_XY - Sum_X * Sum_Y) / Denominator ELSE NULL END DESC) AS Rank FROM Slope_Calculations) SELECT [Product_Division], Slope FROM Slope_Values WHERE Rank = 1;

*User Query 3:* Which geographic areas are performing best, and which are lagging?
SQL output: WITH Monthly_Sales AS (SELECT [Sales_Area], YEAR([Invoice_Date]) AS Sales_Year, MONTH([Invoice_Date]) AS Sales_Month, SUM([Invoice_Volume]) AS Total_Monthly_Sales FROM Billing_data GROUP BY [Sales_Area], YEAR([Invoice_Date]), MONTH([Invoice_Date])), Average_Monthly_Sales AS (SELECT [Sales_Area], AVG(Total_Monthly_Sales) AS Avg_Monthly_Sales FROM Monthly_Sales GROUP BY [Sales_Area]), Ranked_Sales AS (SELECT [Sales_Area], Avg_Monthly_Sales, ROW_NUMBER() OVER (ORDER BY Avg_Monthly_Sales DESC) AS High_Rank, ROW_NUMBER() OVER (ORDER BY Avg_Monthly_Sales ASC) AS Low_Rank FROM Average_Monthly_Sales) SELECT [Sales_Area], Avg_Monthly_Sales FROM Ranked_Sales WHERE High_Rank = 1 OR Low_Rank = 1;

*User Query 4:* Which customer has the highest order booking monthly average?
SQL output: WITH Monthly_Averages AS (SELECT cm.[Customer_Name], od.[Customer_Code], YEAR(od.[SO_Date]) AS Order_Year, MONTH(od.[SO_Date]) AS Order_Month, SUM(od.[Order_Volume]) AS Total_Monthly_Order_Volume FROM Order_data od JOIN [Customer_master] cm ON od.[Customer_Code] = cm.[Customer_Code] GROUP BY cm.[Customer_Name], od.[Customer_Code], YEAR(od.[SO_Date]), MONTH(od.[SO_Date])), Customer_Averages AS (SELECT [Customer_Name], AVG(Total_Monthly_Order_Volume) AS Avg_Monthly_Order_Volume, ROW_NUMBER() OVER (ORDER BY AVG(Total_Monthly_Order_Volume) DESC) AS Rank FROM Monthly_Averages GROUP BY [Customer_Name]) SELECT [Customer_Name], Avg_Monthly_Order_Volume AS [Average_Monthly_Order_Volume] FROM Customer_Averages WHERE Rank = 1;

*User Query 5:* Which customer has the highest growth trend in order volumes across all months?
SQL output: WITH Monthly_Order_Volumes AS (SELECT cm.[Customer_Name], od.[Customer_Code], YEAR(od.[SO_Date]) AS Order_Year, MONTH(od.[SO_Date]) AS Order_Month, SUM(od.[Order_Volume]) AS Total_Monthly_Order_Volume FROM Order_data od JOIN [Customer_master] cm ON od.[Customer_Code] = cm.[Customer_Code] GROUP BY cm.[Customer_Name], od.[Customer_Code], YEAR(od.[SO_Date]), MONTH(od.[SO_Date])), Customer_Slopes AS (SELECT [Customer_Name], COUNT(*) AS N, SUM(Order_Month) AS Sum_X, SUM(Total_Monthly_Order_Volume) AS Sum_Y, SUM(Order_Month * Total_Monthly_Order_Volume) AS Sum_XY, SUM(Order_Month * Order_Month) AS Sum_XX FROM Monthly_Order_Volumes GROUP BY [Customer_Name]), Slope_Calculations AS (SELECT [Customer_Name], (N * Sum_XY - Sum_X * Sum_Y) / NULLIF((N * Sum_XX - Sum_X * Sum_X), 0) AS Slope, ROW_NUMBER() OVER (ORDER BY (N * Sum_XY - Sum_X * Sum_Y) / NULLIF((N * Sum_XX - Sum_X * Sum_X), 0) DESC) AS RowNum FROM Customer_Slopes) SELECT [Customer_Name], Slope FROM Slope_Calculations WHERE RowNum = 1;

*User Query 6:* Which product division has the highest monthly average order volume?
SQL output: WITH Monthly_Order_Volumes AS (SELECT [Product_Division], YEAR([SO_Date]) AS Order_Year, MONTH([SO_Date]) AS Order_Month, SUM([Order_Volume]) AS Total_Monthly_Order_Volume FROM Order_data GROUP BY [Product_Division], YEAR([SO_Date]), MONTH([SO_Date])), Division_Averages AS (SELECT [Product_Division], AVG(Total_Monthly_Order_Volume) AS Avg_Monthly_Order_Volume FROM Monthly_Order_Volumes GROUP BY [Product_Division]) SELECT [Product_Division], Avg_Monthly_Order_Volume FROM Division_Averages ORDER BY Avg_Monthly_Order_Volume DESC;

*User Query 7:* Which Product Division has the highest order to billing ratio across months?
SQL output: WITH Monthly_Billing AS (SELECT [Product_Division], YEAR([Invoice_Date]) AS Billing_Year, MONTH([Invoice_Date]) AS Billing_Month, SUM([Invoice_Volume]) AS Total_Monthly_Billing FROM Billing_data GROUP BY [Product_Division], YEAR([Invoice_Date]), MONTH([Invoice_Date])), Monthly_Order AS (SELECT [Product_Division], YEAR([SO_Date]) AS Order_Year, MONTH([SO_Date]) AS Order_Month, SUM([Order_Volume]) AS Total_Monthly_Order FROM Order_data GROUP BY [Product_Division], YEAR([SO_Date]), MONTH([SO_Date])), Average_Volumes AS (SELECT b.[Product_Division], AVG(b.Total_Monthly_Billing) AS Avg_Monthly_Billing, AVG(o.Total_Monthly_Order) AS Avg_Monthly_Order FROM Monthly_Billing b JOIN Monthly_Order o ON b.[Product_Division] = o.[Product_Division] GROUP BY b.[Product_Division]), Billing_Order_Ratio AS (SELECT [Product_Division], Avg_Monthly_Billing, Avg_Monthly_Order, (Avg_Monthly_Billing / NULLIF(Avg_Monthly_Order, 0)) AS Billing_to_Order_Ratio FROM Average_Volumes), Ranked_Ratios AS (SELECT [Product_Division], Avg_Monthly_Billing AS Billing_Volume_Average, Avg_Monthly_Order AS Order_Volume_Average, Billing_to_Order_Ratio, ROW_NUMBER() OVER (ORDER BY Billing_to_Order_Ratio DESC) AS Rank FROM Billing_Order_Ratio) SELECT [Product_Division], Billing_Volume_Average, Order_Volume_Average, Billing_to_Order_Ratio FROM Ranked_Ratios WHERE Rank = 1;

*User Query 8:* What are the product information & their sales figures for the last financial year?
SQL output: '''SELECT pm.[Product_Code], pm.[Product_Category], pm.[Product_Parameter_1], pm.[Product_Parameter_2], pm.[Product_Parameter_3], pm.[Product_Parameter_4], pm.[Product_Parameter_5], pm.[Product_Parameter_6], SUM(bd.[Invoice_Volume]) AS Total_Sales_Volume, SUM(od.[Total_Amount]) AS Total_Sales_Amount FROM Product_master pm JOIN Billing_data bd ON pm.[Product_Code] = bd.[Product_Code] JOIN Order_data od ON bd.[SO_Document] = od.[SO_Document] AND bd.[Line_Item] = od.[Line_Item] WHERE bd.[Invoice_Date] >= '2023-04-01' AND bd.[Invoice_Date] < '2024-04-01' GROUP BY pm.[Product_Code], pm.[Product_Category], pm.[Product_Parameter_1], pm.[Product_Parameter_2], pm.[Product_Parameter_3], pm.[Product_Parameter_4], pm.[Product_Parameter_5], pm.[Product_Parameter_6] ORDER BY Total_Sales_Amount DESC;'''


Remember that the column names should be only those given in the table description. Do not invent any new column names.
Only use the relevant columns required to answer the user query in the SQL query.
"""

def generation_node(state: AgentState) -> AgentState:
    # Create content for table descriptions and columns
    table_descriptions = "\n\n".join(state['table_descriptions'] or [])
    user_query = state["user_query"]

    if len(state['message_history'])>0:
      history_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state['message_history']])
    else:
      history_content = ""

    # User message to include task and selected table information
    prompt_content = WRITER_PROMPT.format(table_descriptions=table_descriptions, user_query=user_query, history_content = history_content)
    user_message = HumanMessage(content=f"{state['task']}\n\nHere is the information of the selected tables:\n\n{table_descriptions}\n\nUser Query: {user_query}")

    messages = [
        SystemMessage(content=prompt_content),
        user_message
    ]

    # Invoke the model to generate the SQL query
    response = model(messages)

    # Update the state with the generated query and revision number
    state["generated_output"] = response.content
    state["revision_number"] = state.get("revision_number", 1) + 1

    #state['message_history'].append({
    #    'role': 'system',
    #    'content': response.content
    #})

    return state

reflection_prompt = """You are an expert in SQL queries. Based on the user's input query, chat history and the given table descriptions, evaluate whether the generated SQL query will return the required output as per the user's query. Ensure that the column names in the query match those given in the table descriptions.

Chat queries:
{history_content}

User's Input Query:
{user_query}

Table Descriptions:
{table_descriptions}

Generated Output:
{generated_output}

While checking the generated output, consider the following:

1. **Sufficiency of Columns**: Ensure the column names used in the query are sufficient to answer the user's query.
2. **Column Name Accuracy**: Verify that the column names in the SQL query match exactly with those provided in the table descriptions. Check for:
    a. Exact case match (e.g., "ColumnName" should match "ColumnName").
    b. Exact underscore usage (e.g., "column_name" should match "column_name").
    c. Exact space usage (e.g., "Column Name" should match "Column Name").
3. **Join Conditions**: Ensure that column names used for joining tables match those in the table descriptions for the respective tables. For example, "product_code" in table A should correctly join with "Product_code" in table B as `A.product_code = B.Product_code`.
4. **Logical Output**: The output of the query should logically match the user's query requirements.
5. **Microsoft SQL Syntax**: Ensure the SQL query syntax is correct for Microsoft SQL Database. For example, use `TOP 10` instead of `LIMIT 10`.

If the query is correct, explicitly mention "correct". Otherwise, provide a critique and recommendations, and state "the generated output is wrong". Specify the corrections needed if there are errors.
"""

query_extraction = """As a SQL query extraction expert, your task is to extract only the SQL query from the given input.
Do not include any additional text, characters, or code formatting (like triple backticks or words like sql).

If there is no SQL query in the input, return exactly: "Exception: Can't generate the SQL query for the given input".

Input Query:
{query}
"""

def reflection_node(state: AgentState):

    generated_output = state['generated_output']
    user_query = state['user_query']
    table_descriptions = state['table_descriptions']

    if len(state['message_history'])>0:
      history_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state['message_history']])
    else:
      history_content = ""

    sql_output = [
        SystemMessage(content=query_extraction),
        HumanMessage(content=generated_output)
    ]

    sql_response = model.invoke(sql_output)

    sql_output = sql_response.content

    state['message_history'].append({
        'role': 'system',
        'content': sql_response.content
    })

    # Use LLM to evaluate the query
    messages = [
        SystemMessage(content=reflection_prompt),
        HumanMessage(content=sql_output)
    ]
    response = model.invoke(messages)
    critique = response.content
    #print("critique")
    #print(critique)
    #print("\n\n")

    is_query_correct = "correct" in critique.lower()

    if is_query_correct:
      state["critique"] = "The query is correct. No need to change anything"

    else:
      state["critique"] = critique

    state['message_history'].append({
        'role': 'system',
        'content': response.content
    })
    state["is_query_correct"] = is_query_correct
    state["sql_query"] = sql_output

    return state

regenerate_query_content = """
You are an expert SQL assistant. Your task is to generate an optimal SQL query based on the given information. The previously generated SQL query is incorrect. Using the following details, please create the correct SQL query:

  - **Chat history:**
    {history_content}

  - **Table Descriptions:**
    {table_descriptions}

  - **User Query:**
    {initial_query}

  - **Previous SQL Query:**
    {previous_query}

  - **Critique of Previous Query:**
    {critique}

Please ensure the new query addresses the issues highlighted in the critique. Make sure to use the exact column names as provided in the table descriptions. Do not invent any new column names.
"""

def research_critique_node(state: AgentState) -> AgentState:

    if state["is_query_correct"]:
      return state  # Return the correct query without rewriting

    else:
      print("This is running")
      if len(state['message_history'])>0:
        history_content = "\n".join([f"{msg['role']}: {msg['content']}" for msg in state['message_history']])
      else:
        history_content = ""

      critique = state['critique']
      user_query = state['user_query']
      previous_query = state['sql_query']
      table_descriptions = "\n\n".join(state['table_descriptions'])

      # Use the critique to generate a revised query

      messages = [
          SystemMessage(content="You are an expert SQL writer. Based on the provided information, generate the corrected SQL query."),
          HumanMessage(content=regenerate_query_content)
      ]

      response = model(messages)

      generated_output = response.content

      sql_output = [
          SystemMessage(content=query_extraction),
          HumanMessage(content=generated_output)
      ]

      sql_response = model.invoke(sql_output)

      sql_output = sql_response.content

      state["sql_query"] = response.content

      state['message_history'].append({
          'role': 'system',
          'content': response.content
      })

      return state

def fetch_data_node(state: AgentState) -> AgentState:

  query = state.get('sql_query', '')

  # Execute the query and fetch results
  try:
    with engine.connect() as connection:
      result = connection.execute(text(query))

      # Fetch the column names
      column_names = result.keys()
      columns = [x for x in column_names]
      f = pd.DataFrame(result.fetchall(), columns=columns)
      state['final_answer'] = f.to_dict(orient='records')

  except Exception as e:
    state['final_answer'] = f"Error executing query: {e}"

  return state

"""## Plot generation"""

def plot_generator(state: AgentState) -> AgentState:
  user_query = state['user_query']
  query = state.get('sql_query', '')


  chat = ChatCohere(model="command-r-plus", temperature=0.3)

  python_repl = PythonREPL()
  repl_tool = Tool(
      name="python_repl",
      description="Executes python code and returns the result. The code runs in a static sandbox without interactive mode, so print output or save output to a file.",
      func=python_repl.run,
  )
  repl_tool.name = "python_interpreter"

  # from langchain_core.pydantic_v1 import BaseModel, Field
  class ToolInput(BaseModel):
      code: str = Field(description="Python code to execute.")

  repl_tool.args_schema = ToolInput

  # Create the prompt
  prompt = ChatPromptTemplate.from_template("{input}")

  # Create the ReAct agent
  agent = create_cohere_react_agent(
      llm=chat,
      tools=[repl_tool],
      prompt=prompt,
  )

  agent_executor = AgentExecutor(agent=agent, tools=[repl_tool], verbose=True)

  # Execute the query and fetch results
  #try:
  with engine.connect() as connection:
      result = connection.execute(text(query))

      # Fetch the column names
      column_names = result.keys()
      columns = [x for x in column_names]
      df = pd.DataFrame(result.fetchall(), columns=columns)

      state['data_frame'] = df

      # Convert DataFrame to a more manageable format for the prompt
      data_sample = df.head(10).to_string(index=False)  # Sample for prompt
      data_summary = df.describe().to_string()  # Summary statistics

      # Create the prompt for Cohere to generate the plot code
      prompt_text = f"""
      User query: {user_query}

      Here is a sample of the data:
      {data_sample}

      Here are summary statistics of the data:
      {data_summary}

      Based on the user query, generate the appropriate Python code to create a plot using matplotlib.
      Note that please choose the type appropriate type of plot as per user query. It could be Bar plot, line plot, pie chart, waterfall etc
      Add code to convert the image into bytes.

      Only return the code. Do not include any other text or keywords like python or backticks or code or anything else.
      Alsi, i want image in the form of array which will be converted into a list to export to the state.
      Here are few examples:

      **Query 1**: Tell me the year wise total sales.

      import matplotlib.pyplot as plt
      import io
      from io import BytesIO
      import numpy as np

      # Convert data to DataFrame
      import pandas as pd
      import uuid

      # Plotting
      plt.figure(figsize=(10, 6))
      plt.plot(df['Sales_Year'], df['Total_Sales'], marker='o')
      plt.xlabel('Sales Year')
      plt.ylabel('Total Sales')
      plt.title('Year-wise Total Sales')
      plt.grid(True)

      # Converting plot to bytes
      buf = io.BytesIO()
      plt.savefig(buf, format="png", bbox_inches='tight')
      buf.seek(0)

      image_bytes = buf.getvalue()

      # Create a BytesIO object to save the plot
      img_buffer = BytesIO()
      plt.savefig(img_buffer, format='png')
      img_buffer.seek(0)

      # Convert image to NumPy array
      img_array = np.frombuffer(img_buffer.getvalue(), dtype=np.uint8)

      file_name = f"plot_image_{uuid.uuid4().hex}.png"
      with open(file_name, "wb") as f:
          f.write(image_bytes)
      gdrive_file = drive.CreateFile({{'title': file_name}})
      gdrive_file.SetContentFile(file_name)
      gdrive_file.Upload()
      print(f"Image saved to Google Drive with file ID: {{gdrive_file['id']}}")

      ** Query 2**:

      Expected output:
      import matplotlib.pyplot as plt
      import io
      from io import BytesIO
      import numpy as np

      # Convert data to DataFrame
      import pandas as pd
      import uuid

      df = pd.DataFrame(data, columns=['Zone', 'Sales_Person_Name', 'Order_to_Invoice_Ratio'])

      # Calculate the highest ratio per zone
      highest_ratio_per_zone = df.groupby('Zone')['Order_to_Invoice_Ratio'].max().reset_index()

      # Plotting
      plt.figure(figsize=(10, 6))
      plt.bar(highest_ratio_per_zone['Zone'], highest_ratio_per_zone['Order_to_Invoice_Ratio'], align='center')
      plt.xlabel('Zone')
      plt.ylabel('Highest Order to Invoice Ratio')
      plt.title('Highest Order Volume to Invoice Volume Ratio by Zone')
      plt.xticks(rotation=45, ha='right')
      plt.grid(axis='y', linestyle='--', alpha=0.7)

      # Converting plot to bytes
      buf = io.BytesIO()
      plt.savefig(buf, format="png", bbox_inches='tight')
      buf.seek(0)

      image_bytes = buf.getvalue()

      # Create a BytesIO object to save the plot
      img_buffer = BytesIO()
      plt.savefig(img_buffer, format='png')
      img_buffer.seek(0)

      # Convert image to NumPy array
      img_array = np.frombuffer(img_buffer.getvalue(), dtype=np.uint8)

      file_name = f"plot_image_{uuid.uuid4().hex}.png"
      with open(file_name, "wb") as f:
        f.write(image_bytes)

      gdrive_file = drive.CreateFile({{'title': file_name}})
      gdrive_file.SetContentFile(file_name)
      gdrive_file.Upload()
      print(f"Image saved to Google Drive with file ID: {{gdrive_file['id']}}")



      The Above one is just an example. The type of plot should be as per the question.
      Please Note that the code should not contain plt.close()
      Generate the code properly. Do not include any other text or keywords like python or backticks or code or anything else.
      """

      # Create a HumanMessage object from the prompt
      prompt_message = HumanMessage(content=prompt_text)

      # Get the response from Cohere
      response = chat([prompt_message]).content.strip()
      try:
        cleaned_code = response.strip("```python").strip("```")

      except:

        try:
          cleaned_code = response.strip("```")
        except:
          cleaned_code = response


      #print("cleaned code")
      #print(cleaned_code)
      #print("\n\n\n\n\n")

      exec_globals = {}
      try:
        out = exec(cleaned_code, exec_globals)

        img_bytes = exec_globals['img_array']


        #print("-------------Here is the image-----------------")
        img = Image.open(BytesIO(np.array(img_bytes.tolist(), dtype=np.uint8)))
        img.show()
        #print("------------------------------------------------")
        img_list = img_array.tolist()
      except:
        #print("---")
        img_list = []
        img_bytes = None

      # Save the base64 string in the state
      state['plot_result'] = img_list
      state['cleaned_code'] = cleaned_code


      return state

#memory = MemorySaver()

def call_pipeline():

  from langgraph.checkpoint.sqlite import SqliteSaver

  memory = SqliteSaver.from_conn_string(":memory:")

  def should_continue(state):
      if state["is_query_correct"]:
          return "fetch_data"
      elif state["revision_number"] > state["max_revisions"]:
          return "fetch_data"
      return "reflect"

  builder = StateGraph(AgentState)

  # Adding nodes
  builder.add_node("select_tables", select_tables_node)
  builder.add_node("table_info", table_info_node)
  builder.add_node("generate_query", generation_node)
  builder.add_node("reflect", reflection_node)
  builder.add_node("query_critique", research_critique_node)
  builder.add_node("fetch_data", fetch_data_node)  # Adding the new node
  builder.add_node("plot_generator", plot_generator)  # Adding the new node

  # Setting the entry point
  builder.set_entry_point("select_tables")

  # Adding conditional edges to manage flow based on conditions
  builder.add_conditional_edges(
      "reflect",
      should_continue,
      {"fetch_data": "fetch_data", "reflect": "query_critique"}
  )

  # Linking nodes directly
  builder.add_edge("select_tables", "table_info")
  builder.add_edge("table_info", "generate_query")
  builder.add_edge("query_critique", "generate_query")
  builder.add_edge("generate_query", "reflect")
  builder.add_edge("fetch_data", "plot_generator")  # Linking fetch_data to END
  builder.add_edge("plot_generator", END)  # Linking fetch_data to END

  # Compile the graph with the checkpointer
  graph = builder.compile(checkpointer=memory)

  return graph

graph = call_pipeline()

def get_initital_state(user_query):
  initial_state = {
    'task': "First generate the SQL query and then fetch the data for the following user input",
    'user_query': user_query, #"For each zone, tell me the name of sales person with highest order volume to invoice volume ratio?",
    'selected_tables': [],
    'table_descriptions': [],
    'critique': "",
    'content': [],
    "max_revisions": 3,
    "revision_number": 0,
    "initial_query": "",
    "final_answer": "",
    "sql_query": "",
    "is_query_correct": False,
    "message_history": [],
    "plot_code": "",
    "plot_result": [],
    "cleaned_code": ""
}

  return initial_state

def get_thread(thread_id = "1"):

  thread = {"configurable": {"thread_id": thread_id}}

  final_state = None
  thread = {"configurable": {"thread_id": thread_id}}

  return thread


def final_genai_function(user_query, thread, is_initial_state = True, verbose=False):

  graph = call_pipeline()
  if is_initial_state:
    initial_state = get_initital_state(user_query)
  else:
    initial_state = {}
    initial_state['user_query'] = user_query
  # try:
  output = graph.invoke(initial_state, thread)

  return output


