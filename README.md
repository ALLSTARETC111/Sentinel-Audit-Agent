Sentinel Audit Agent
​Autonomous Real-Time Smart Contract Security & Analysis
​The Sentinel Audit Agent is a "reasoning-first" agentic pipeline built to monitor the Base Mainnet mempool in real-time. Unlike traditional scanners, this agent uses high-level reasoning to detect and analyze new smart contract deployments before they are fully confirmed on the blockchain, providing a critical window for security assessment.
​🚀 Core Capabilities
​Live Mempool Monitoring: Interfaces directly with Base Mainnet via Alchemy WebSockets (WSS) to catch Contract Creation transactions (where to is null) with millisecond latency.
​Agentic Bytecode Reasoning: Utilizes a reasoning-first approach to evaluate contract logic and identify structural risks without relying on stale databases or simulated data.
​Observable Front-End Delivery: Streams real-time alerts and logic-check results directly to a dedicated Telegram interface for immediate oversight.
​Production-Grade Architecture: Designed for 24/7 uptime using a stateless, environment-variable-driven deployment model.
​🛠 Technical Flow
​The agent follows a Think-Act-Observe loop to ensure 100% data accuracy:
​Listen: A persistent WebSocket connection to the base-mainnet node monitors every pending transaction.
​Filter: The agent filters for transactions specifically creating new smart contracts.
​Analyze: The agent extracts the deployment hash and performs an immediate logic-check for vulnerabilities such as:
​Reentrancy Flaws
​Honeypot Logic
​Hidden Ownership Backdoors
​Broadcast: A formatted Live Audit Report is sent via the Telegram API to the user's front-end.
​📋 Setup & Deployment
​This agent is optimized for zero-investment hosting on Render using a Python-based runtime.
​Required Environment Variables
​To make the agent active, the following keys must be configured in your hosting environment:
​ALCHEMY_WSS_URL: The WebSocket URL for Base Mainnet.
​TELEGRAM_TOKEN: The API token from @BotFather.
​TELEGRAM_CHAT_ID: Your unique numeric identifier from @IDBot.
​Installation
​Clone the repository.
​Install dependencies: pip install -r requirements.txt.
​Run the agent: python app.py.
