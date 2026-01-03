#!/bin/bash
echo "🚀 Launching Antigravity Cockpit..."

# Get the absolute path to the directory containing this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start Server
echo "Starting Server..."
cd "$DIR/Beats-PM-System/cockpit/server"
npm install > /dev/null 2>&1
npm start &
SERVER_PID=$!

# Start Client (Dev Mode for now, or serve from server if built)
# For better UX in dev, we'll start the vite dev server
echo "Starting Client..."
cd "$DIR/Beats-PM-System/cockpit/client"
npm install > /dev/null 2>&1
npm run dev &
CLIENT_PID=$!

echo "✅ Systems Active."
echo "   Server: http://localhost:3000"
echo "   Client: http://localhost:5173"
echo ""
echo "Press CTRL+C to stop."

wait $SERVER_PID $CLIENT_PID
