#!/bin/bash
# Build and Test Script for Green Coding Assistant

echo "🌱 Green Coding Assistant - Build & Test Script"
echo "================================================"
echo ""

# Check if gradlew exists
if [ ! -f "./gradlew" ]; then
    echo "❌ Error: gradlew not found. Are you in the project root?"
    exit 1
fi

# Make gradlew executable
chmod +x ./gradlew

echo "📦 Step 1: Cleaning old builds..."
./gradlew clean --quiet

echo "🔨 Step 2: Building plugin..."
./gradlew buildPlugin --quiet

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "📍 Plugin location:"
    ls -lh build/distributions/*.zip
    echo ""
    echo "📋 Next steps:"
    echo "   1. Install in PyCharm: Settings → Plugins → Install Plugin from Disk"
    echo "   2. Install CodeCarbon: pip install codecarbon"
    echo "   3. Open demo.py in PyCharm to test"
    echo ""
    echo "🚀 Or run in development mode:"
    echo "   ./gradlew runIde"
else
    echo "❌ Build failed!"
    exit 1
fi

echo ""
echo "================================================"
echo "✨ Ready for testing!"

