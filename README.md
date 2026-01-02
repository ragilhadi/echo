# Echo 🔊

**Echo** is a AI chat assistant application built with Streamlit and OpenRouter. It provides a beautiful, intuitive interface for interacting with multiple AI models through a single platform.

## Features

- 🤖 **Multiple AI Models** - Access various AI models through OpenRouter API
- 💬 **Multi-Room Chat** - Create and manage multiple chat rooms
- 💾 **Persistent History** - All conversations are saved in SQLite database
- 🐳 **Docker Ready** - Fully containerized for easy deployment
- 🎨 **Modern UI** - Clean, responsive interface built with Streamlit
- 🔄 **Streaming Responses** - Real-time AI responses with streaming support

## Quick Start

### Using Docker (Recommended)

1. **Pull the image from Docker Hub:**
   ```bash
   docker pull ragilhadi/echo:latest
   ```

2. **Create a `.env` file with your OpenRouter API key:**
   ```bash
   OPENROUTER_API_KEY=your_api_key_here
   ```

3. **Create a `docker-compose.yml` file:**
   ```yaml
   services:
     echo:
       image: ragilhadi/echo:latest
       container_name: echo
       ports:
         - "8501:8501"
       volumes:
         - ./echo_data:/app/data
       environment:
         - DB_PATH=/app/data/chat_history.db
       env_file:
         - .env
       restart: unless-stopped

   volumes:
     echo_data:
       driver: local
   ```

4. **Run the application:**
   ```bash
   docker-compose up -d
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`

### Building from Source

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd chatbot-web
   ```

2. **Create `.env` file:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY` (required) - Your OpenRouter API key
- `DB_PATH` (optional) - Path to SQLite database file (default: `chat_history.db`)

### Getting an OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai/)
2. Sign up for an account
3. Navigate to API Keys section
4. Generate a new API key
5. Add it to your `.env` file

## Project Structure

```
.
├── app.py                      # Main Streamlit application
├── constants.py                # Application constants
├── modules/
│   ├── client/                 # OpenRouter API client
│   │   ├── base.py            # Base chat client
│   │   ├── openrouter.py      # OpenRouter implementation
│   │   └── exception.py       # Custom exceptions
│   ├── db/                    # Database layer
│   │   └── db.py              # SQLite database operations
│   └── frontend/              # Frontend components
│       ├── components/        # UI components
│       └── managers/          # State and data managers
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker Compose configuration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Usage

### Creating a Chat Room

1. On the homepage, enter a name for your chat room
2. Click "Create New Chat Room"
3. Start chatting with AI models

### Managing Chat Rooms

- **Switch Rooms**: Use the sidebar to navigate between different chat rooms
- **Delete Room**: Remove a chat room and all its messages
- **Clear History**: Clear conversation history while keeping the room

### Selecting AI Models

- Choose from available OpenRouter models in the chat interface
- Models are dynamically loaded from OpenRouter API
- Free models are available for testing

## Data Persistence

All chat data is stored in a SQLite database that persists in the Docker volume:
- **Volume Location**: `./echo_data` on your host machine
- **Database File**: `chat_history.db`
- **Tables**: `chat_rooms`, `messages`

To backup your data, simply copy the `./echo_data` directory.

## Docker Commands

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f echo

# Stop the application
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# Remove everything including volumes
docker-compose down -v
```

## Development

### Local Development (without Docker)

1. **Install Python 3.11+**

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API key
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Technology Stack

- **Frontend**: Streamlit
- **AI API**: OpenRouter
- **Database**: SQLite
- **Containerization**: Docker & Docker Compose
- **Language**: Python 3.11

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Author

**Ragil Prasetyo**
- Email: ragilhprasetyo@gmail.com

## Support

If you encounter any issues or have questions:
1. Check the logs: `docker-compose logs -f echo`
2. Ensure your `.env` file has a valid OpenRouter API key
3. Verify Docker and Docker Compose are properly installed

---

**Enjoy chatting with Echo! 🔊**
