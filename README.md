# MemoSphere AI – An Intelligent Memory-Powered Chat Assistant

## Introduction

MemoSphere AI is a memory-powered conversational chatbot developed using Python, Streamlit, LangChain, and Ollama. It provides an interactive chat experience by maintaining conversation context and remembering previous interactions.

Unlike a basic chatbot that treats every message independently, MemoSphere AI uses LangChain's ConversationBufferMemory to retain the context of ongoing conversations. This allows users to ask follow-up questions and continue discussions without repeatedly providing the same information.

The application uses SQLite to store conversation history locally, making previous conversations accessible even after restarting the application.

## Objectives

- Develop an intelligent conversational chatbot using a locally running Large Language Model.
- Implement conversational memory using LangChain.
- Maintain context across multiple interactions.
- Store and retrieve conversation history using SQLite.
- Provide an interactive and user-friendly interface using Streamlit.
- Enable users to search and export their conversations.

## Key Features

### 1. Context-Aware Conversations
Uses LangChain ConversationBufferMemory to maintain the context of previous messages and generate relevant responses.

### 2. Local LLM Integration
Integrates the Qwen2.5:3B model through Ollama to generate AI-powered responses locally.

### 3. Conversation History
Stores user messages and AI responses in an SQLite database for persistent conversation management.

### 4. Search Previous Conversations
Allows users to search saved conversations by their titles and quickly access previous discussions.

### 5. Conversation Export
Provides an option to download the current conversation as a text file for future reference.

### 6. New Conversation Management
Allows users to start new conversations and switch between previously saved chats.

### 7. Clear Conversation
Enables users to clear the messages in the current conversation while retaining the conversation entry.

### 8. Interactive User Interface
Provides a clean and responsive interface developed using Streamlit with a redesigned layout and chat interface.

## Technologies Used

- **Python** – Core programming language.
- **Streamlit** – Interactive web application framework.
- **LangChain** – Framework for building LLM-powered applications.
- **ConversationBufferMemory** – Maintains conversational context.
- **Ollama** – Runs the language model locally.
- **Qwen2.5:3B** – Large Language Model used for response generation.
- **SQLite** – Local database for storing conversations.
- **Requests** – Handles communication with the Ollama service.

## System Architecture

MemoSphere AI follows a simple conversational architecture:

1. The user enters a message through the Streamlit interface.
2. The message is passed to the LangChain conversation chain.
3. ConversationBufferMemory provides the previous conversational context.
4. Ollama processes the prompt using the Qwen2.5:3B model.
5. The generated response is displayed in the Streamlit interface.
6. Both the user message and AI response are stored in the SQLite database.
7. Previous conversations can be retrieved, searched, and exported when required.

## Memory Management

MemoSphere AI uses LangChain's ConversationBufferMemory to retain the conversation history during an active chat session.

The SQLite database provides persistent storage for conversations. When an existing conversation is opened, its stored messages are loaded back into the memory component, allowing the chatbot to continue with the available conversational context.

## Database

The application uses SQLite for local conversation storage.

The database maintains two main tables:

**1. Conversations**

Stores conversation details such as:
- Conversation ID
- Conversation title
- Creation timestamp
- Last updated timestamp

**2. Messages**

Stores individual conversation messages such as:
- Message ID
- Conversation ID
- Message role
- Message content
- Creation timestamp

## Applications

- Personal AI chat assistance.
- Context-aware question answering.
- Interactive learning and information assistance.
- Maintaining conversational records.
- Exploring conversational memory in Large Language Models.
- Understanding local LLM integration with LangChain.

## Future Enhancements

- Support for multiple local language models.
- Improved long-term memory management.
- Automatic conversation summarization.
- File upload and document-based question answering.
- Conversation categorization and tagging.
- Advanced memory retrieval techniques.
- Customizable chatbot personalities.

## Conclusion

MemoSphere AI demonstrates how conversational memory can improve interactions with Large Language Models. By combining LangChain memory, Ollama, Qwen2.5:3B, Streamlit, and SQLite, the project provides a conversational assistant that maintains context, stores previous interactions, and supports convenient conversation management.

The project highlights the practical implementation of local LLM integration and memory-based conversational AI applications.
