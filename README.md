# Article Analysis Assistant

This project is an advanced article analysis assistant that leverages AI tools to perform thorough research and analysis on articles. It uses a combination of Bing search and a custom research assistant to gather and synthesize information, providing comprehensive insights into the content.

## Features

- **Bing Search Integration**: Uses Bing to search for additional information on topics discussed in the article.
- **Research Assistant**: Generates detailed reports on subjects that require deeper understanding.
- **RSS Feed and Article Parsing**: Fetches and processes content from RSS feeds or direct article URLs.
- **Title Generation**: Automatically generates concise and informative titles for articles.
- **Streamlined Analysis**: Utilizes a structured prompt to guide the AI's analysis process, ensuring thorough exploration and reasoning.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/article-analysis-assistant.git
   cd article-analysis-assistant
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in a `.env` file:
   ```
   OPENAI_API_KEY=<your_openai_api_key>
   TAVILY_API_KEY=<your_tavily_api_key>
   AZURE_OPENAI_API_KEY=<your_azure_openai_api_key>
   AZURE_OPENAI_ENDPOINT=<your_azure_openai_endpoint>
   AZURE_OPENAI_DEPLOYMENT_NAME=<your_azure_openai_deployment_name>
   AZURE_OPENAI_API_VERSION=<your_azure_openai_api_version>
   BING_SEARCH_URL=<your_bing_search_url>
   BING_SUBSCRIPTION_KEY=<your_bing_subscription_key>
   LANGSMITH_TRACING=<true_or_false>
   LANGSMITH_ENDPOINT=<your_langsmith_endpoint>
   LANGSMITH_API_KEY=<your_langsmith_api_key>
   LANGSMITH_PROJECT=<your_langsmith_project>
   ```

## Usage

1. Run the main script:
   ```bash
   python main.py
   ```

2. Enter an RSS feed URL or an article URL when prompted.

3. The assistant will fetch the content, perform analysis, and save the results in the `results` directory.

## File Structure

- `main.py`: The main script that orchestrates the article analysis process.
- `prompt.txt`: Contains the structured prompt used to guide the AI's analysis.
- `feedParser.py`: Handles fetching and parsing of RSS feeds and articles.
- `results/`: Directory where analysis results are saved.