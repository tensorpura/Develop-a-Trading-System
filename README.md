# Develop-a-Trading-System-with-FIX

Develop a FIX client that facilitates the transmission of random orders to a FIX server, additionally computing specific statistics pertinent to the order flow. The primary requirements are detailed below:

FIX Protocol Version: Utilize version 4.2 of the Financial Information eXchange (FIX) protocol.
Programming Language: The application should be developed using Python 3.
Execution Instructions: Provide comprehensive guidance on how to execute the application effectively.
External Libraries: Utilization of open-source libraries is permitted.
FIX Flow Management: The application must manage basic FIX flows, including Logon and Sequence Number handling. For simplicity, the sequence number will be reset upon logon.
Message Types: The application should be capable of sending the following messages to the server:
New Order (35=D): Either a Limit Order or Market Order, with a random price specified for Limit Orders.
Order Cancel Request (35=F).
No other types of requests should be sent.
Server Responses: The application must handle the following messages from the server:
Reject (35=3)
Execution Report (35=8)
Order Cancel Reject (35=9)
Order Generation: The application is to send 1,000 random orders for MSFT, AAPL, and BAC, with the possibility of orders being BUY, SELL, or SHORT. Orders can be either limit or market orders. While it is not necessary to send all 1,000 orders simultaneously, endeavor to dispatch them within a 5-minute window following application start. Subsequently, randomly cancel a portion of these orders within 5 minutes of their submission.
Statistical Analysis: The application should calculate the following statistics:
Total trading volume in USD.
Profit and Loss (PNL) generated from the trading activities.
Volume Weighted Average Price (VWAP) of the fills for each instrument.
The server will supply adequate information for the maintenance of order state and the computation of the aforementioned statistics.

For connectivity, use configuration to connect to your desired exchange server.
